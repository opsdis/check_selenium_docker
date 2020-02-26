check_selenium_docker
-----------------------

- [Overview](#overview)
  * [Highlights](#highlights)
- [Workflow](#metrics-naming)
- [System requirements](#system-requirements)
  * [ITRS OP5 Monitor example](#itrs-op5-monitor-example)
- [Docker image](#docker-image)
- [Plugin](#plugin)
- [Add new test scenarios](#add-new-test-scenarios)
- [Execute the plugin](#execute-the-plugin)
- [License](#license)

# Overview #
Synthetic website monitoring with Selenium and Docker.

check_selenium_docker is a Nagios based plugin that spins up a Docker container, executes the test and, once the test is finished and the result has been reported back to the monitoring solution, removes the Docker container.

### Highlights ###

* Works with any Nagios compatible system such as ITRS OP5 Monitor, Icinga2 or Nagios.
* Every test is executed in a fresh environment. (https://www.selenium.dev/documentation/en/guidelines_and_recommendations/fresh_browser_per_test/)
* Will remove the Docker container as soon as the test is complete. Requires no manual cleanup of stopped containers.

# Workflow #

Install Selenium IDE for Chrome (https://selenium.dev/downloads).

Record your test.

Export the test and copy the .side file to the server that will run the docker image.

A Docker container will execute the test and report the test results back to the monitoring system.

![Workflow](img/selenium_docker.png)

# System requirements #
The following prerequisites must be installed on the server that will execute the plugin.

* Python 3 with the docker module
* docker-ce

## ITRS OP5 Monitor example ##

```
# Install docker-ce
yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2

yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

yum install docker-ce

# Add user 'monitor' to group 'docker'
usermod -aG docker monitor

# Start and enable docker
systemctl start docker && systemctl enable docker

# Install the docker Python 3 module
pip-3 install docker

# (Optional) Add versionlock to docker-ce
yum install yum-plugin-versionlock
yum versionlock docker-ce

# (Optional) Remove versionlock from docker-ce
yum versionlock clear
```


# Docker image #

Build the Docker image:

```
git clone https://github.com/opsdis/check_selenium_docker
cd check_selenium_docker/dockerimage/
docker build . --tag opsdis/selenium-chrome-node-with-side-runner
```


# Plugin #

Copy the plugin to the plugin directory and make it executable:

```
cp check_selenium_docker.py /opt/plugins/custom/
chmod +x /opt/plugins/custom/check_selenium_docker.py
```

Add a new check_command to Monitor:

```
check_selenium_docker
$USER1$/custom/check_selenium_docker.py $ARG1$
```


# Add new test scenarios #

Create a new main directory (/opt/plugins/custom/selenium) in the main directory create a new directory 
preferably named as the URL used in the test (/opt/plugins/custom/selenium/opsdis.com):

```
mkdir /opt/plugins/custom/selenium
mkdir /opt/plugins/custom/selenium/opsdis.com
```

Create two subdirectories, out and sides:

```
mkdir /opt/plugins/custom/selenium/opsdis.com/{out,sides}

```

Add the side-file to the sides subdirectory and modify the permissions:

```
chmod 777 /opt/plugins/custom/selenium/opsdis.com/out/
chmod 755 /opt/plugins/custom/selenium/opsdis.com/sides/opsdis.com.side
```

The directory structure should look like this:

```
├── opsdis.com
│   ├── out
│   └── sides
│       └── opsdis.com.side
```

# Execute the plugin #

```
/opt/plugins/custom/check_selenium_docker.py /opt/plugins/custom/selenium/opsdis.com
OK: Passed 1 of 1 tests. | 'passed'=1;;;; 'failed'=0;;;; 'exec_time'=6s;;;;

```

# License 
check_selenium_docker is licensed under GPL version 3.
