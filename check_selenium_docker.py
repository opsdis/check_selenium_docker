#!/usr/bin/env python3
"""
    Copyright (C) 2020  Opsdis Consulting AB <https://opsdis.com/>
    This file is part of check_selenium_docker.
    check_selenium_docker is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    check_selenium_docker is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with check_selenium_docker.  If not, see <http://www.gnu.org/licenses/>.
"""

import docker
import os, sys, time
import json
import argparse
import glob

# Parse commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument("--timeout", type=int, default=300, help="results waiting timeout in sec, default 300")
parser.add_argument("path", type=str, help="path to selenium test")
args = parser.parse_args()
path = args.path
timeout = abs(args.timeout)
os.chdir(path)

# Find side file and parse it to get the project name
side = glob.glob(path + '/sides/*.side')
side_file = open(side[0],'r')
side_json = json.loads(side_file.read())
side_file.close()
result = path + '/out/' + side_json['name'] + '.json'

# Remove old result json file if it exists
if os.path.isfile(result):
    os.remove(result)

# Start selenium docker container
client = docker.from_env()
container = client.containers.run("opsdis/selenium-chrome-node-with-side-runner", auto_remove=True, shm_size="2G",
                                  volumes={ path + '/out': {'bind': '/selenium-side-runner/out', 'mode': 'rw'},
                                            path + '/sides': {'bind': '/sides', 'mode': 'rw'}}, detach=True)

# Wait for result file to be written
waitedfor = 0
while not os.path.isfile(result) and waitedfor <= timeout:
    time.sleep(1)
    waitedfor += 1

# If no result was received after timeout exit with status unknown
if waitedfor >= timeout:
    container.stop()
    print("UNKNOWN: Test timed out. Investigate issues.")
    sys.exit(3)

# Open and read result file
file = open(result,'r')
json_input = json.loads(file.read())
file.close()

# Stop and remove container
container.stop()

# Calculate execution time
exec_time = 0 if len(json_input['testResults']) == 0 else \
    int(str(json_input['testResults'][0]['endTime'])[:-3]) - int(str(json_input['startTime'])[:-3])

# Exit logic with performance data
if json_input['numFailedTests'] == 0:
    print("OK: Passed " + str(json_input['numPassedTests']) + " of " + str(json_input['numTotalTests']) +
          " tests. | 'passed'=" + str(json_input['numPassedTests']) + ";;;; 'failed'=" +
          str(json_input['numFailedTests']) + ";;;; " + "'exec_time'=" + str(exec_time) + "s;;;;")
    sys.exit(0)

elif json_input['numFailedTests'] > 0:
    print("CRITICAL: Failed " +str(json_input['numFailedTests']) + " of " + str(json_input['numTotalTests']) +
          " tests. Error message: " + str(json_input['testResults'][0]['message']) +
          " | 'passed'=" + str(json_input['numPassedTests']) + ";;;; 'failed'=" + str(json_input['numFailedTests']) +
          ";;;; " + "'exec_time'=" + str(exec_time) + "s;;;;")
    sys.exit(2)

else:
    print("UNKNOWN: Investigate issues")
    sys.exit(3)
