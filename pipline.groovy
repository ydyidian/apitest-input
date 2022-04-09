/**
 * @Author: yiciu
 * @Version: 1.0
 * @Date: 2022/04/09 14:34 | 周六
 * @Desc: 输入法流水线脚本
 * 
 * */


pipeline {
    agent any
    parameters {
        choice name: "auto_env", choices: ['test_3d', 'test_2', 'test_3', 'test_3a', 'test_3b', 'test_3c', 'test_1'], description: "运行环境"
        choice name: "mix_type", choices: ['and', 'or'], description: "案例是否交集「and交集｜or并集」"
        extendedChoice name: 'markers', description: '标签集合', multiSelectDelimiter: ',', quoteValue: false, saveJSONParameterToFile: false, type: 'PT_CHECKBOX', value: 'smoke,user,script', visibleItemCount: 5
    }
    environment {
        markers = ""
    }
    stages {
        stage("初始化") {
            steps {
                echo '重置构建名称'
                wrap([$class: 'BuildUser']) {
                    script {
                        BUILD_USER = "${env.BUILD_USER}"
                    }
				}
                buildName "#${BUILD_NUMBER}-${env.JOB_NAME}-${params.auto_env}-${BUILD_USER}"
                echo '获取标签信息'
                script {
                    markers = "${params.markers}".split(",").join(" ${params.mix_type} ")
                    echo "本次执行的标签条件：${markers}"
                }
            }
        }
        stage("拉取代码") {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/master']], extensions: [], userRemoteConfigs: [[url: 'https://10.20.32.27/wego-test/apitest-input.git']]])
                echo '拉取代码success！'
            }
        }
        stage("执行用例") {
            steps {
                echo '开始执行用例···'
                sh "cd $WORKSPACE && pytest -v -m '$markers' --alluredir=$WORKSPACE/allure-results --clean-alluredir"
                echo '用例执行done!'
            }
        }
    }
    post {
        always {
            script {
                allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
            }
            echo '报告生成done!'
        }
    }
}