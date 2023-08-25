# coding=utf8

"""
@Author: jiyelin
@Version: 1.0
@Date: 2021/08/25 17:50
@Desc: 季哥提供😌
"""
import base64
import hashlib

from Crypto.Cipher import AES

BS = AES.block_size


def padding_pkcs5(value):
    """
    填充需要加密的内容长度
    :param value: 需要加密的内容
    :return: 填充后的内容
    """
    return str.encode(value + (BS - len(value) % BS) * chr(BS - len(value) % BS))


def aes_ecb_encrypt(key, value) -> str:
    """
    aes加密

    :param key: 随机key
    :param value: 加密内容
    :return: 加密结果
    """
    cryptor = AES.new(bytes.fromhex(key), AES.MODE_ECB)
    padding_value = padding_pkcs5(value)
    ciphertext = cryptor.encrypt(padding_value)
    return "".join(["%02x" % i for i in ciphertext]).upper()


def get_sha1prng_key(key) -> str:
    """
    通过SHA1PRNG算法加密key
    :param key: 随机key
    :return: 加密key
    """
    signature = hashlib.sha1(key.encode()).digest()
    signature = hashlib.sha1(signature).digest()
    return "".join(["%02x" % i for i in signature]).upper()[:32]


def generate_token(key, value) -> str:
    result_as_hex = aes_ecb_encrypt(get_sha1prng_key(key), value)
    return base64.b64encode(result_as_hex.encode("utf8")).decode()


if __name__ == "__main__":
    # 测试3环境数据.
    # result = generate_token("6O3u7B7nB0xT36Up", "%s_%s_%s" % ("U201903281423219250092305", "20200911143550", "ios"))
    # expected_result = (
    #     "QTQzODc4MDE2NjI0Q0Q0QzY0MTUxMURGREIwMDEwRDUxNTc0REMzQkZEOTE2NENCNUY5QjIxREU4RTUwREUyQTk0MTBC"
    #     "Njk3RTBCMzY0RDlGMTkzMkZDMzYyRDRERUQ0"
    # )
    # print(result == expected_result)
    t=get_sha1prng_key("test1@163.com")
    get_sha1prng_key(t)