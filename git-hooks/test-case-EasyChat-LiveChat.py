#!/usr/bin/env python

import sys
import subprocess
import re

import ast
import os
from tqdm import tqdm
import inspect

rootdir = './'


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print(Bcolors.HEADER + "\nRunning Pre-commit checks...\n" + Bcolors.ENDC)

print(Bcolors.BOLD + "\nChecking whether project working or not\n" + Bcolors.ENDC)

projectcheck = tqdm(position=0, leave=True, total=1)
val0 = subprocess.run('python ./manage.py check',
                      shell=True, stdout=subprocess.DEVNULL)
working_check = val0.returncode
projectcheck.update(1)

print(Bcolors.BOLD + "\nRunning Project TestCases\n" + Bcolors.ENDC)

print(Bcolors.BOLD + "\nRunning EasyChat TestCases\n" + Bcolors.ENDC)

projecttestscheck = tqdm(position=0, leave=True, total=1)
val8 = subprocess.run('python -W ignore ./manage.py test EasyChatApp.tests',
                      shell=True, stdout=subprocess.DEVNULL)

print(Bcolors.BOLD + "\nRunning EasyTMS TestCases\n" + Bcolors.ENDC)

test_tms = subprocess.run('python -W ignore ./manage.py test EasyTMSApp/tests/',
                          shell=True, stdout=subprocess.DEVNULL)

print(Bcolors.BOLD + "\nRunning LiveChat TestCases\n" + Bcolors.ENDC)

test_livechat = subprocess.run('python -W ignore ./manage.py test LiveChatApp/tests/',
                               shell=True, stdout=subprocess.DEVNULL)

print(Bcolors.BOLD + "\nRunning EasySearch TestCases\n" + Bcolors.ENDC)

test_search = subprocess.run('python -W ignore ./manage.py test EasySearchApp/tests/',
                             shell=True, stdout=subprocess.DEVNULL)

test_cases_check = val8.returncode + test_tms.returncode + \
    test_livechat.returncode + test_search.returncode

projecttestscheck.update(1)

if working_check != 0:
    print(Bcolors.OKBLUE + "\nProject working check... " +
          Bcolors.FAIL + Bcolors.BOLD + "FAILED" + Bcolors.ENDC)
else:
    print(Bcolors.OKBLUE + "\nProject working check... " +
          Bcolors.OKGREEN + Bcolors.BOLD + "PASSED" + Bcolors.ENDC)

if test_cases_check != 0:
    print(Bcolors.OKBLUE + "\nProject TestCases check... " +
          Bcolors.FAIL + Bcolors.BOLD + "FAILED" + Bcolors.ENDC)
else:
    print(Bcolors.OKBLUE + "\nProject TestCases check... " +
          Bcolors.OKGREEN + Bcolors.BOLD + "PASSED" + Bcolors.ENDC)

if (working_check + test_cases_check) != 0:
    print(Bcolors.FAIL + Bcolors.BOLD +
          "\nPlease do the appropriete changes in the code" + Bcolors.ENDC)
    sys.exit(1)
else:
    print(Bcolors.OKGREEN + Bcolors.BOLD +
          "\nHurray!!! ALL CHECKS PASSED" + Bcolors.ENDC)
    sys.exit(0)
