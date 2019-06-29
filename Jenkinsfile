boolean isAnotherUpgradeRunning = false
boolean isInAppropriateTimeslot = false

String upgradeFolderPath = "${env.JENKINS_HOME}/workspace/${env.JOB_NAME}/POTS"

String findOneInputMatrix (String folder) {
    String allMatrix= sh (
            script: "ls ${folder}/*.xml",
            returnStdout: true
            ).trim()
    String[] matrixArray = allMatrix.split('\n')
    Random rand = new Random()
    String oneTimeMatrix = matrixArray[rand.nextInt(matrixArray.size())]
    echo "Fetch matrix  ${oneTimeMatrix} out of ${matrixArray.size()} entries"
    return oneTimeMatrix
}

def parseResult(String logFile, String testType, int buildID) {
    String UPG_REPORT_DIR = '/UPG_Report/'
    String reportFile = sh (
            script: "tail ${logFile} | grep -i 'Check html result' | rev | cut -d '/' -f 1 | rev  | uniq",
            returnStdout: true
            ).trim()
    echo "Result generated with name of ${reportFile}"
    String reportFilePath = sh (
            script: "find . -name ${reportFile} | cut -d '/' -f 2-",
            returnStdout: true
            ).trim()
    echo "Find report file path as ${reportFilePath}"
    sh "cp  ${reportFilePath} ${UPG_REPORT_DIR}"
    archiveArtifacts artifacts: reportFilePath, fingerprint: true, onlyIfSuccessful: true
    publishHTML (
            [allowMissing: false,
                alwaysLinkToLastBuild: false,
                keepAll: false,
                reportDir: UPG_REPORT_DIR,
                reportFiles: reportFile,
                reportName: "$testType Report",
                reportTitles: "$testType Report from build # $buildID"
            ]
            )
}

pipeline {
    agent any
    
    stages {
        stage('Prepare') {
            steps {
                echo "Doing preparation"
                git credentialsId: 'ID', url: 'git@github.com:imzyk/Demo_CICD_WithJenkins.git'                
            }
        }
        
        stage('Smoking') {
            parallel {
                stage('Smoking Test on LinuxOS') {
                    steps {
                        echo "Executing Lin smoking"
                        timeout(time: 4, unit: 'HOURS') {
                            sh "/usr/bin/python ${WORKSPACE}/scripts/docker_launcher.py IP USR PWD ${params.smoking} --test_component lin"
                        }
                    }
                }
                stage('Smoking Test on WinOS') {
                    steps {
                        echo "Executing Win smoking"
                        timeout(time: 4, unit: 'HOURS') {
                            sh "/usr/bin/python ${WORKSPACE}/scripts/docker_launcher.py IP USR PWD ${params.smoking} --test_component win"
                        }
                    }
                }
            }
        }
        
        stage('FVT') {
            steps {
                echo "Executing FVT"
                timeout(time: 4, unit: 'HOURS') {
                    sh "/usr/bin/python ${WORKSPACE}/scripts/jenkins_launcher.py 'FVT_Job_4Pipeline' --BUILDNUMBER ${params.BuildNum}"
                }
            }
        }
        

        stage('Check Upgrade preconditions') {
            steps {
                echo "Checking time slot"
                script {
                    Calendar nowC = Calendar.getInstance()
                    int weekOfMonth = nowC.get(Calendar.WEEK_OF_MONTH)
                    int dayOfWeek = nowC.get(Calendar.DAY_OF_WEEK)
                    echo "Week is ${weekOfMonth} and Day is ${dayOfWeek}"

                    isInAppropriateTimeslot = ( weekOfMonth % 2 == 1 && dayOfWeek ==  Calendar.SATURDAY)
                }
            }
        }
        
        stage('Upgrade') {
            when {
                allOf {
                    expression { ! isAnotherUpgradeRunning }
                    expression { isInAppropriateTimeslot }
                }
            }
            parallel {
                stage('Executing Upgrade') {
                    steps {
                        echo "Executing upgrade"
                        script {
                            isAnotherUpgradeRunning = true 
                            echo "Making Upgrade folder"
                            upgradeFolder.mkdirs()
                            String upgLog = 'upg.log'
                            dir (upgradeFolderPath) {
                                // Get upgrade testing script from another GIT repo
                                git credentialsId: SSH_TOKEN, url: GIT_URL_FOR_UPGRADE
                                echo "./upgradeLauncher.py --srcbld ${params.sourceBuild} --tgtbld ${params.targetBuild}> ${upgLog} 2>&1"
                                parseResult(upgLog, 'UpgradeTesting', currentBuild.number)
                            }
                            isAnotherUpgradeRunning = false
                        }
                    }
                }
            }
        }
    }

    post { 
        always { 
            echo 'Clean up work space'
            deleteDir()
        }
    }
}
