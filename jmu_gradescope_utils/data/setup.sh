#!/usr/bin/env bash

apt-get install -y python3 python3-pip python3-dev

pip3 install -r /autograder/source/requirements.txt

pip3 install git+https://github.com/JMU-CS/jmu_python_gradescope_utils.git
