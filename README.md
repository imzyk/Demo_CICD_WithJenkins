# Demo_CICD_WithJenkins
A quick demo of how to orchestrate different stages of testing together with pipeline

Jenkinsfile: Declarative Jenkins file. 5 stages are defined
             Stage1: Prepare to copy related scripts from git to Jenkins
             Stage2: Smoking test stage. It would invoke docker_launcher.py file under scripts folder
             Stage3: Basic E2E function testing stage which would invoke jenkins_launcher.py
             Stage4: Check if precondition is met for next stage
             Stage5: Upgrade testing which would copy test code from another git repo

scripts/docker_launcher.py: Test script used for Stage2. Such script would SSH to a docker host to
                            spawn docker instance and run tests upon it
scripts/jenkins_launcher.py: Test script used for Stage3. Such script would invoke Jenkins job directly 
                             through Jenkins Web Service
