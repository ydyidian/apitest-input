# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/07 14:18
@Desc:
"""

import collections
import difflib
import pprint
import re
import sys
import traceback
import types
import warnings

from .util import _common_shorten_repr, _count_diff_all_purpose, _count_diff_hashable, safe_repr

DIFF_OMITTED = "\nDiff is %s characters long. " "Set self.maxDiff to None to see it."


class Assertion(object):

    failureException = AssertionError

    longMessage = True

    maxDiff = 80*8

    # If a string is longer than _diffThreshold, use normal comparison instead
    # of difflib.  See #11763.
    _diffThreshold = 2**16

    # Attribute used by TestSuite for classSetUp

    _classSetupFailed = False

    _class_cleanups = []
    # 不同类型对应的equal校验
    _type_equality_funcs = {
        dict: "assertDictEqual",
        list: "assertListEqual",
        tuple: "assertTupleEqual",
        set: "assertSetEqual",
        frozenset: "assertSetEqual",
        str: "assertMultiLineEqual",
    }

    def assertFalse(self, expr, msg=None):
        """Check that the expression is false."""
        if expr:
            msg = self._formatMessage(msg, "%s is not false" % safe_repr(expr))
            raise self.failureException(msg)

    def assertTrue(self, expr, msg=None):
        """Check that the expression is true."""
        if not expr:
            msg = self._formatMessage(msg, "%s is not true" % safe_repr(expr))
            raise self.failureException(msg)

    def fail(self, msg=None):
        """Fail immediately, with the given message."""
        raise self.failureException(msg)

    def _formatMessage(self, msg, standardMsg):
        """Honour the longMessage attribute when generating failure messages.
        If longMessage is False this means:
        * Use only an explicit message if it is provided
        * Otherwise use the standard message for the assert

        If longMessage is True:
        * Use the standard message
        * If an explicit message is provided, plus ' : ' and the explicit message
        """
        if not self.longMessage:
            return msg or standardMsg
        if msg is None:
            return standardMsg
        try:
            # don't switch to '{}' formatting in Python 2.X
            # it changes the way unicode input is handled
            return "%s : %s" % (standardMsg, msg)
        except UnicodeDecodeError:
            return "%s : %s" % (safe_repr(standardMsg), safe_repr(msg))

    def assertRaises(self, expected_exception, *args, **kwargs):
        """Fail unless an exception of class expected_exception is raised
        by the callable when invoked with specified positional and
        keyword arguments. If a different type of exception is
        raised, it will not be caught, and the test case will be
        deemed to have suffered an error, exactly as for an
        unexpected exception.

        If called with the callable and arguments omitted, will return a
        context object used like this::

             with self.assertRaises(SomeException):
                 do_something()

        An optional keyword argument 'msg' can be provided when assertRaises
        is used as a context object.

        The context manager keeps a reference to the exception as
        the 'exception' attribute. This allows you to inspect the
        exception after the assertion::

            with self.assertRaises(SomeException) as cm:
                do_something()
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code, 3)
        """
        context = _AssertRaisesContext(expected_exception, self)
        try:
            return context.handle("assertRaises", args, kwargs)
        finally:
            # bpo-23890: manually break a reference cycle
            context = None

    def assertWarns(self, expected_warning, *args, **kwargs):
        """Fail unless a warning of class warnClass is triggered
        by the callable when invoked with specified positional and
        keyword arguments.  If a different type of warning is
        triggered, it will not be handled: depending on the other
        warning filtering rules in effect, it might be silenced, printed
        out, or raised as an exception.

        If called with the callable and arguments omitted, will return a
        context object used like this::

             with self.assertWarns(SomeWarning):
                 do_something()

        An optional keyword argument 'msg' can be provided when assertWarns
        is used as a context object.

        The context manager keeps a reference to the first matching
        warning as the 'warning' attribute; similarly, the 'filename'
        and 'lineno' attributes give you information about the line
        of Python code from which the warning was triggered.
        This allows you to inspect the warning after the assertion::

            with self.assertWarns(SomeWarning) as cm:
                do_something()
            the_warning = cm.warning
            self.assertEqual(the_warning.some_attribute, 147)
        """
        context = _AssertWarnsContext(expected_warning, self)
        return context.handle("assertWarns", args, kwargs)

    def _getAssertEqualityFunc(self, first, second):
        """Get a detailed comparison function for the types of the two args.

        Returns: A callable accepting (first, second, msg=None) that will
        raise a failure exception if first != second with a useful human
        readable error message for those types.
        """
        #
        # NOTE(gregory.p.smith): I considered isinstance(first, type(second))
        # and vice versa.  I opted for the conservative approach in case
        # subclasses are not intended to be compared in detail to their super
        # class instances using a type equality func.  This means testing
        # subtypes won't automagically use the detailed comparison.  Callers
        # should use their type specific assertSpamEqual method to compare
        # subclasses if the detailed comparison is desired and appropriate.
        # See the discussion in http://bugs.python.org/issue2578.
        #
        if type(first) is type(second):
            asserter = self._type_equality_funcs.get(type(first))
            if asserter is not None:
                if isinstance(asserter, str):
                    asserter = getattr(self, asserter)
                return asserter

        return self._baseAssertEqual

    def _baseAssertEqual(self, first, second, msg=None):
        """The default assertEqual implementation, not type specific."""
        if not first == second:
            standardMsg = "%s != %s" % _common_shorten_repr(first, second)
            msg = self._formatMessage(msg, standardMsg)
            raise self.failureException(msg)

    def assertEqual(self, first, second, msg=None):
        """Fail if the two objects are unequal as determined by the '=='
        operator.
        """
        assertion_func = self._getAssertEqualityFunc(first, second)
        assertion_func(first, second, msg=msg)

    def assertMultiEqual(self, *elements, msg=None):
        """
        校验多个元素相同

        :param msg: 错误信息, 默认值: None
        """
        item_cnt = len(elements)
        assert item_cnt > 1
        assertion_func = self._getAssertEqualityFunc(elements[0], elements[1])
        for i in range(item_cnt - 1):
            assertion_func(
                elements[i],
                elements[i + 1],
                msg=f"index[{i}] and index[{i + 1}] is not equal! {'' if msg is None else msg}",
            )

    def assertNotEqual(self, first, second, msg=None):
        """Fail if the two objects are equal as determined by the '!='
        operator.
        """
        if not first != second:
            msg = self._formatMessage(msg, "%s == %s" % (safe_repr(first), safe_repr(second)))
            raise self.failureException(msg)

    def assertAlmostEqual(self, first, second, places=None, msg=None, delta=None):
        """Fail if the two objects are unequal as determined by their
        difference rounded to the given number of decimal places
        (default 7) and comparing to zero, or by comparing that the
        difference between the two objects is more than the given
        delta.

        Note that decimal places (from zero) are usually not the same
        as significant digits (measured from the most significant digit).

        If the two objects compare equal then they will automatically
        compare almost equal.
        """
        if first == second:
            # shortcut
            return
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")

        diff = abs(first - second)
        if delta is not None:
            if diff <= delta:
                return

            standardMsg = "%s != %s within %s delta (%s difference)" % (
                safe_repr(first),
                safe_repr(second),
                safe_repr(delta),
                safe_repr(diff),
            )
        else:
            if places is None:
                places = 7

            if round(diff, places) == 0:
                return

            standardMsg = "%s != %s within %r places (%s difference)" % (
                safe_repr(first),
                safe_repr(second),
                places,
                safe_repr(diff),
            )
        msg = self._formatMessage(msg, standardMsg)
        raise self.failureException(msg)

    def assertNotAlmostEqual(self, first, second, places=None, msg=None, delta=None):
        """Fail if the two objects are equal as determined by their
        difference rounded to the given number of decimal places
        (default 7) and comparing to zero, or by comparing that the
        difference between the two objects is less than the given delta.

        Note that decimal places (from zero) are usually not the same
        as significant digits (measured from the most significant digit).

        Objects that are equal automatically fail.
        """
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")
        diff = abs(first - second)
        if delta is not None:
            if not (first == second) and diff > delta:
                return
            standardMsg = "%s == %s within %s delta (%s difference)" % (
                safe_repr(first),
                safe_repr(second),
                safe_repr(delta),
                safe_repr(diff),
            )
        else:
            if places is None:
                places = 7
            if not (first == second) and round(diff, places) != 0:
                return
            standardMsg = "%s == %s within %r places" % (safe_repr(first), safe_repr(second), places)

        msg = self._formatMessage(msg, standardMsg)
        raise self.failureException(msg)

    def assertSequenceEqual(self, seq1, seq2, msg=None, seq_type=None):
        """An equality assertion for ordered sequences (like lists and tuples).

        For the purposes of this function, a valid ordered sequence type is one
        which can be indexed, has a length, and has an equality operator.

        Args:
            seq1: The first sequence to compare.
            seq2: The second sequence to compare.
            seq_type: The expected datatype of the sequences, or None if no
                    datatype should be enforced.
            msg: Optional message to use on failure instead of a list of
                    differences.
        """
        if seq_type is not None:
            seq_type_name = seq_type.__name__
            if not isinstance(seq1, seq_type):
                raise self.failureException("First sequence is not a %s: %s" % (seq_type_name, safe_repr(seq1)))
            if not isinstance(seq2, seq_type):
                raise self.failureException("Second sequence is not a %s: %s" % (seq_type_name, safe_repr(seq2)))
        else:
            seq_type_name = "sequence"

        differing = None
        try:
            len1 = len(seq1)
        except (TypeError, NotImplementedError):
            differing = "First %s has no length.    Non-sequence?" % (seq_type_name)

        if differing is None:
            try:
                len2 = len(seq2)
            except (TypeError, NotImplementedError):
                differing = "Second %s has no length.    Non-sequence?" % (seq_type_name)

        if differing is None:
            if seq1 == seq2:
                return

            differing = "%ss differ: %s != %s\n" % ((seq_type_name.capitalize(),) + _common_shorten_repr(seq1, seq2))

            for i in range(min(len1, len2)):
                try:
                    item1 = seq1[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += "\nUnable to index element %d of first %s\n" % (i, seq_type_name)
                    break

                try:
                    item2 = seq2[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += "\nUnable to index element %d of second %s\n" % (i, seq_type_name)
                    break

                if item1 != item2:
                    differing += "\nFirst differing element %d:\n%s\n%s\n" % ((i,) + _common_shorten_repr(item1, item2))
                    break
            else:
                if len1 == len2 and seq_type is None and type(seq1) != type(seq2):
                    # The sequences are the same, but have differing types.
                    return

            if len1 > len2:
                differing += "\nFirst %s contains %d additional " "elements.\n" % (seq_type_name, len1 - len2)
                try:
                    differing += "First extra element %d:\n%s\n" % (len2, safe_repr(seq1[len2]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += "Unable to index element %d " "of first %s\n" % (len2, seq_type_name)
            elif len1 < len2:
                differing += "\nSecond %s contains %d additional " "elements.\n" % (seq_type_name, len2 - len1)
                try:
                    differing += "First extra element %d:\n%s\n" % (len1, safe_repr(seq2[len1]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += "Unable to index element %d " "of second %s\n" % (len1, seq_type_name)
        standardMsg = differing
        diffMsg = "\n" + "\n".join(difflib.ndiff(pprint.pformat(seq1).splitlines(), pprint.pformat(seq2).splitlines()))

        standardMsg = self._truncateMessage(standardMsg, diffMsg)
        msg = self._formatMessage(msg, standardMsg)
        self.fail(msg)

    def _truncateMessage(self, message, diff):
        max_diff = self.maxDiff
        if max_diff is None or len(diff) <= max_diff:
            return message + diff
        return message + (DIFF_OMITTED % len(diff))

    def assertListItemEqual(self, list1, list2, key=None, msg=None):
        """
        校验序列的每一项相同
        :param list1: 序列1
        :param list2: 序列2
        :param key: 排序规则, 默认值: 无，默认顺序校验
        :param msg: 错误信息, 默认值: None
        """
        list1.sort(key=key)
        list2.sort(key=key)
        self.assertSequenceEqual(list1, list2, msg)

    def assertListEqual(self, list1, list2, msg=None):
        """A list-specific equality assertion.

        Args:
            list1: The first list to compare.
            list2: The second list to compare.
            msg: Optional message to use on failure instead of a list of
                    differences.

        """
        self.assertSequenceEqual(list1, list2, msg, seq_type=list)

    def assertTupleEqual(self, tuple1, tuple2, msg=None):
        """A tuple-specific equality assertion.

        Args:
            tuple1: The first tuple to compare.
            tuple2: The second tuple to compare.
            msg: Optional message to use on failure instead of a list of
                    differences.
        """
        self.assertSequenceEqual(tuple1, tuple2, msg, seq_type=tuple)

    def assertSetEqual(self, set1, set2, msg=None):
        """A set-specific equality assertion.

        Args:
            set1: The first set to compare.
            set2: The second set to compare.
            msg: Optional message to use on failure instead of a list of
                    differences.

        assertSetEqual uses ducktyping to support different types of sets, and
        is optimized for sets specifically (parameters must support a
        difference method).
        """
        try:
            difference1 = set1.difference(set2)
        except TypeError as e:
            self.fail("invalid type when attempting set difference: %s" % e)
        except AttributeError as e:
            self.fail("first argument does not support set difference: %s" % e)

        try:
            difference2 = set2.difference(set1)
        except TypeError as e:
            self.fail("invalid type when attempting set difference: %s" % e)
        except AttributeError as e:
            self.fail("second argument does not support set difference: %s" % e)

        if not (difference1 or difference2):
            return

        lines = []
        if difference1:
            lines.append("Items in the first set but not the second:")
            for item in difference1:
                lines.append(repr(item))
        if difference2:
            lines.append("Items in the second set but not the first:")
            for item in difference2:
                lines.append(repr(item))

        standardMsg = "\n".join(lines)
        self.fail(self._formatMessage(msg, standardMsg))

    def assertIn(self, member, container, msg=None):
        """Just like self.assertTrue(a in b), but with a nicer default message."""
        if member not in container:
            standardMsg = "%s not found in %s" % (safe_repr(member), safe_repr(container))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertNotIn(self, member, container, msg=None):
        """Just like self.assertTrue(a not in b), but with a nicer default message."""
        if member in container:
            standardMsg = "%s unexpectedly found in %s" % (safe_repr(member), safe_repr(container))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIs(self, expr1, expr2, msg=None):
        """Just like self.assertTrue(a is b), but with a nicer default message."""
        if expr1 is not expr2:
            standardMsg = "%s is not %s" % (safe_repr(expr1), safe_repr(expr2))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsNot(self, expr1, expr2, msg=None):
        """Just like self.assertTrue(a is not b), but with a nicer default message."""
        if expr1 is expr2:
            standardMsg = "unexpectedly identical: %s" % (safe_repr(expr1),)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertDictEqual(self, d1, d2, msg=None):
        self.assertIsInstance(d1, dict, "First argument is not a dictionary")
        self.assertIsInstance(d2, dict, "Second argument is not a dictionary")

        if d1 != d2:
            standardMsg = "%s != %s" % _common_shorten_repr(d1, d2)
            diff = "\n" + "\n".join(difflib.ndiff(pprint.pformat(d1).splitlines(), pprint.pformat(d2).splitlines()))
            standardMsg = self._truncateMessage(standardMsg, diff)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertDictContainsSubset(self, subset, dictionary, msg=None):
        """Checks whether dictionary is a superset of subset."""
        warnings.warn("assertDictContainsSubset is deprecated", DeprecationWarning)
        missing = []
        mismatched = []
        for key, value in subset.items():
            if key not in dictionary:
                missing.append(key)
            elif value != dictionary[key]:
                mismatched.append(
                    "%s, expected: %s, actual: %s" % (safe_repr(key), safe_repr(value), safe_repr(dictionary[key]))
                )

        if not (missing or mismatched):
            return

        standardMsg = ""
        if missing:
            standardMsg = "Missing: %s" % ",".join(safe_repr(m) for m in missing)
        if mismatched:
            if standardMsg:
                standardMsg += "; "
            standardMsg += "Mismatched values: %s" % ",".join(mismatched)

        self.fail(self._formatMessage(msg, standardMsg))

    def assertCountEqual(self, first, second, msg=None):
        """Asserts that two iterables have the same elements, the same number of
        times, without regard to order.

            self.assertEqual(Counter(list(first)),
                             Counter(list(second)))

         Example:
            - [0, 1, 1] and [1, 0, 1] compare equal.
            - [0, 0, 1] and [0, 1] compare unequal.

        """
        first_seq, second_seq = list(first), list(second)
        try:
            first = collections.Counter(first_seq)
            second = collections.Counter(second_seq)
        except TypeError:
            # Handle case with unhashable elements
            differences = _count_diff_all_purpose(first_seq, second_seq)
        else:
            if first == second:
                return
            differences = _count_diff_hashable(first_seq, second_seq)

        if differences:
            standardMsg = "Element counts were not equal:\n"
            lines = ["First has %d, Second has %d:  %r" % diff for diff in differences]
            diffMsg = "\n".join(lines)
            standardMsg = self._truncateMessage(standardMsg, diffMsg)
            msg = self._formatMessage(msg, standardMsg)
            self.fail(msg)

    def assertMultiLineEqual(self, first, second, msg=None):
        """Assert that two multi-line strings are equal."""
        self.assertIsInstance(first, str, "First argument is not a string")
        self.assertIsInstance(second, str, "Second argument is not a string")

        if first != second:
            # don't use difflib if the strings are too long
            if len(first) > self._diffThreshold or len(second) > self._diffThreshold:
                self._baseAssertEqual(first, second, msg)
            firstlines = first.splitlines(keepends=True)
            secondlines = second.splitlines(keepends=True)
            if len(firstlines) == 1 and first.strip("\r\n") == first:
                firstlines = [first + "\n"]
                secondlines = [second + "\n"]
            standardMsg = "%s != %s" % _common_shorten_repr(first, second)
            diff = "\n" + "".join(difflib.ndiff(firstlines, secondlines))
            standardMsg = self._truncateMessage(standardMsg, diff)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertLess(self, a, b, msg=None):
        """Just like self.assertTrue(a < b), but with a nicer default message."""
        if not a < b:
            standardMsg = "%s not less than %s" % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertLessEqual(self, a, b, msg=None):
        """Just like self.assertTrue(a <= b), but with a nicer default message."""
        if not a <= b:
            standardMsg = "%s not less than or equal to %s" % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertGreater(self, a, b, msg=None):
        """Just like self.assertTrue(a > b), but with a nicer default message."""
        if not a > b:
            standardMsg = "%s not greater than %s" % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertGreaterEqual(self, a, b, msg=None):
        """Just like self.assertTrue(a >= b), but with a nicer default message."""
        if not a >= b:
            standardMsg = "%s not greater than or equal to %s" % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsNone(self, obj, msg=None):
        """Same as self.assertTrue(obj is None), with a nicer default message."""
        if obj is not None:
            standardMsg = "%s is not None" % (safe_repr(obj),)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsNotNone(self, obj, msg=None):
        """Included for symmetry with assertIsNone."""
        if obj is None:
            standardMsg = "unexpectedly None"
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsInstance(self, obj, cls, msg=None):
        """Same as self.assertTrue(isinstance(obj, cls)), with a nicer
        default message."""
        if not isinstance(obj, cls):
            standardMsg = "%s is not an instance of %r" % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertNotIsInstance(self, obj, cls, msg=None):
        """Included for symmetry with assertIsInstance."""
        if isinstance(obj, cls):
            standardMsg = "%s is an instance of %r" % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertRaisesRegex(self, expected_exception, expected_regex, *args, **kwargs):
        """Asserts that the message in a raised exception matches a regex.

        Args:
            expected_exception: Exception class expected to be raised.
            expected_regex: Regex (re.Pattern object or string) expected
                    to be found in error message.
            args: Function to be called and extra positional args.
            kwargs: Extra kwargs.
            msg: Optional message used in case of failure. Can only be used
                    when assertRaisesRegex is used as a context manager.
        """
        context = _AssertRaisesContext(expected_exception, self, expected_regex)
        return context.handle("assertRaisesRegex", args, kwargs)

    def assertWarnsRegex(self, expected_warning, expected_regex, *args, **kwargs):
        """Asserts that the message in a triggered warning matches a regexp.
        Basic functioning is similar to assertWarns() with the addition
        that only warnings whose messages also match the regular expression
        are considered successful matches.

        Args:
            expected_warning: Warning class expected to be triggered.
            expected_regex: Regex (re.Pattern object or string) expected
                    to be found in error message.
            args: Function to be called and extra positional args.
            kwargs: Extra kwargs.
            msg: Optional message used in case of failure. Can only be used
                    when assertWarnsRegex is used as a context manager.
        """
        context = _AssertWarnsContext(expected_warning, self, expected_regex)
        return context.handle("assertWarnsRegex", args, kwargs)

    def assertRegex(self, text, expected_regex, msg=None):
        """Fail the test unless the text matches the regular expression."""
        if isinstance(expected_regex, (str, bytes)):
            assert expected_regex, "expected_regex must not be empty."
            expected_regex = re.compile(expected_regex)
        if not expected_regex.search(text):
            standardMsg = "Regex didn't match: %r not found in %r" % (expected_regex.pattern, text)
            # _formatMessage ensures the longMessage option is respected
            msg = self._formatMessage(msg, standardMsg)
            raise self.failureException(msg)

    def assertNotRegex(self, text, unexpected_regex, msg=None):
        """Fail the test if the text matches the regular expression."""
        if isinstance(unexpected_regex, (str, bytes)):
            unexpected_regex = re.compile(unexpected_regex)
        match = unexpected_regex.search(text)
        if match:
            standardMsg = "Regex matched: %r matches %r in %r" % (
                text[match.start() : match.end()],
                unexpected_regex.pattern,
                text,
            )
            # _formatMessage ensures the longMessage option is respected
            msg = self._formatMessage(msg, standardMsg)
            raise self.failureException(msg)


def _is_subtype(expected, basetype):
    if isinstance(expected, tuple):
        return all(_is_subtype(e, basetype) for e in expected)
    return isinstance(expected, type) and issubclass(expected, basetype)


class _BaseTestCaseContext:
    def __init__(self, test_case):
        self.test_case = test_case

    def _raiseFailure(self, standardMsg):
        msg = self.test_case._formatMessage(self.msg, standardMsg)
        raise self.test_case.failureException(msg)


class _AssertRaisesBaseContext(_BaseTestCaseContext):
    def __init__(self, expected, test_case, expected_regex=None):
        _BaseTestCaseContext.__init__(self, test_case)
        self.expected = expected
        self.test_case = test_case
        if expected_regex is not None:
            expected_regex = re.compile(expected_regex)
        self.expected_regex = expected_regex
        self.obj_name = None
        self.msg = None

    def handle(self, name, args, kwargs):
        """
        If args is empty, assertRaises/Warns is being used as a
        context manager, so check for a 'msg' kwarg and return self.
        If args is not empty, call a callable passing positional and keyword
        arguments.
        """
        try:
            if not _is_subtype(self.expected, self._base_type):
                raise TypeError("%s() arg 1 must be %s" % (name, self._base_type_str))
            if not args:
                self.msg = kwargs.pop("msg", None)
                if kwargs:
                    raise TypeError("%r is an invalid keyword argument for " "this function" % (next(iter(kwargs)),))
                return self

            callable_obj, *args = args
            try:
                self.obj_name = callable_obj.__name__
            except AttributeError:
                self.obj_name = str(callable_obj)
            with self:
                callable_obj(*args, **kwargs)
        finally:
            # bpo-23890: manually break a reference cycle
            self = None


class _AssertRaisesContext(_AssertRaisesBaseContext):
    """A context manager used to implement TestCase.assertRaises* methods."""

    _base_type = BaseException
    _base_type_str = "an exception type or tuple of exception types"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            if self.obj_name:
                self._raiseFailure("{} not raised by {}".format(exc_name, self.obj_name))
            else:
                self._raiseFailure("{} not raised".format(exc_name))
        else:
            traceback.clear_frames(tb)
        if not issubclass(exc_type, self.expected):
            # let unexpected exceptions pass through
            return False
        # store exception, without traceback, for later retrieval
        self.exception = exc_value.with_traceback(None)
        if self.expected_regex is None:
            return True

        expected_regex = self.expected_regex
        if not expected_regex.search(str(exc_value)):
            self._raiseFailure('"{}" does not match "{}"'.format(expected_regex.pattern, str(exc_value)))
        return True

    __class_getitem__ = classmethod(types.GenericAlias)


class _AssertWarnsContext(_AssertRaisesBaseContext):
    """A context manager used to implement TestCase.assertWarns* methods."""

    _base_type = Warning
    _base_type_str = "a warning type or tuple of warning types"

    def __enter__(self):
        # The __warningregistry__'s need to be in a pristine state for tests
        # to work properly.
        for v in sys.modules.values():
            if getattr(v, "__warningregistry__", None):
                v.__warningregistry__ = {}
        self.warnings_manager = warnings.catch_warnings(record=True)
        self.warnings = self.warnings_manager.__enter__()
        warnings.simplefilter("always", self.expected)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.warnings_manager.__exit__(exc_type, exc_value, tb)
        if exc_type is not None:
            # let unexpected exceptions pass through
            return
        try:
            exc_name = self.expected.__name__
        except AttributeError:
            exc_name = str(self.expected)
        first_matching = None
        for m in self.warnings:
            w = m.message
            if not isinstance(w, self.expected):
                continue
            if first_matching is None:
                first_matching = w
            if self.expected_regex is not None and not self.expected_regex.search(str(w)):
                continue
            # store warning for later retrieval
            self.warning = w
            self.filename = m.filename
            self.lineno = m.lineno
            return
        # Now we simply try to choose a helpful failure message
        if first_matching is not None:
            self._raiseFailure('"{}" does not match "{}"'.format(self.expected_regex.pattern, str(first_matching)))
        if self.obj_name:
            self._raiseFailure("{} not triggered by {}".format(exc_name, self.obj_name))
        else:
            self._raiseFailure("{} not triggered".format(exc_name))


if __name__ == "__main__":
    ass = Assertion()
    a = b = 1
    c = 2

    ass.assertMultiEqual(a, b, c)
