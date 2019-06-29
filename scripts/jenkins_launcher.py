#!/usr/bin/env python
###############################################################################
#
# jenkins_launcher.py
#
###############################################################################

import argparse
import logging
import jenkins
import os
import re
import sys
import time


logger = logging.getLogger(__name__)

jenkins_server_url = TBD
jenkins_user_name =  TBD
jenkins_api_token = TBD

jenkins_server = jenkins.Jenkins(jenkins_server_url, username=jenkins_user_name, password=jenkins_api_token)

class JenkinsPackage():

    def __init__(self, package_name):
        self.package_name = package_name

    def startJob(self, job_params):
        next_build_number = jenkins_server.get_job_info(self.package_name)['nextBuildNumber']
        logger.debug("next job number is %s" % next_build_number)

        jenkins_server.build_job(self.package_name, parameters=job_params)
        time.sleep(10)
        return next_build_number

    def checkJobResult(self, job_number):
        build_info = jenkins_server.get_build_info(self.package_name, job_number)
        build_result = build_info.get('result')
        logger.debug(build_result)

        while (build_result is None):
            time.sleep(10)

            build_info = jenkins_server.get_build_info(self.package_name, job_number)
            build_result = build_info.get('result')
            logger.debug(build_result)

        if 'SUCCESS'==build_result:
            logger.info('jobs runs success')
            return

        if 'ABORTED' == build_result:
            raise Exception("job runs aborted.")
        else:
            raise Exception('job runs with error %s' % build_result)

    def executeJob(self, job_params):
        job_number = self.startJob(job_params)
        self.checkJobResult(job_number)


def setup_logging():
    logger.setLevel(logging.DEBUG)
    logging.basicConfig()

if __name__ == "__main__":
    logger = logging.getLogger('jenkins_launcher')
    setup_logging()

    package_name = sys.argv[1]
    job_params = sys.argv[2:]

    jenkins_package = JenkinsPackage(package_name)
    jenkins_package.executeJob(job_params)
