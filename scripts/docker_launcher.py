#!/usr/bin/env python
###############################################################################
#
# docker_launcher.py
#
###############################################################################
import logging
import argparse
import paramiko
import re
import sys

reload(sys)
sys.setdefaultencoding('utf8')

logger = logging.getLogger(__name__)

class DockerLauncher():

    def __init__(self, ip, username, password):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, 22, username, password)
        self.ssh_client = ssh_client

    def executeSmokingJob(self, args_for_smoking):
        cmd = "StartSmokingJob " + ' '.join(args_for_smoking)
        logger.info("Executing a smoking job via:\n%s" % start_cat_docker_cmd)
        # SSH to the docker host where docker engineer started, spawn a docker
        # instance, executing job and put result to resultsdir
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
        for line in iter(lambda: stdout.readline(2048), ""):
            print(line)
        logger.info("Successfully executed the smoking job.")

        parser = argparse.ArgumentParser()
        parser.add_argument('--resultsdir')
        args, unknown = parser.parse_known_args(args_for_smoking)
        logger.info("Checking the test result.")
        self.checkTestResult(args.resultsdir)

    def checkTestResult(self, result_dir):
        with open(result_dir + "/fullDebug.log") as fp:
            for i, line in enumerate(fp):
                match = re.search('Overall test result:\s+(\w+)', line)
                if match:
                    logger.info("All cases passed.")
                    if match.group(1) == "PASS":
                        return
                    raise Exception("Not all cases passed.", match.group(1))
            raise Exception("Could not find \"Overall test result\" in fullDebug.log.")


def setup_logging():
    logger.setLevel(logging.INFO)
    log_format = "%(asctime)s [%(threadName)s] [%(levelname)s]:\n%(message)s"
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

if __name__ == "__main__":
    setup_logging()

    docker_host_ip = sys.argv[1]
    docker_host_username = sys.argv[2]
    docker_host_password = sys.argv[3]
    args_for_smoking = sys.argv[4:]

    launcher = DockerLauncher(docker_host_ip, docker_host_username, docker_host_password)
    launcher.executeSmokingJob(args_for_smoking)

