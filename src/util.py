################################################################################
#  Python Package to Support 42crunch System Deployment
#
#    Author: Sam Li <yang.li@owasp.org>
#
#       2022 - 2023
################################################################################
import re, os, subprocess
import json, ruamel.yaml, unicodedata

# Execute shell command in subprocess and return code, stdout, stderr
def run_command(cmd):
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, universal_newlines=True) as proc:
        code = proc.returncode
        std_out, std_err = proc.communicate()
    return  code, std_out, std_err

# check if it's a valid file
def is_file(file_name):
    return os.path.isfile(file_name)

def is_directory(dir_name):
# check if it's a valid directory
    return os.path.exists(dir_name) and os.path.isdir(dir_name)

# string formatter from 42crunch
def strip_non_alpha_num(text):
    encodedText = unicodedata.normalize('NFKD', text)
    return re.sub('[^A-Za-z0-9\\-_]+', '', encodedText)

# Given repo info and repo base, perform git operation specific to the repo
def git_op(repo, base, verbose):
    path = base + repo['repo-path']
    cmd = "cd " + path + "; git stash; git checkout " + repo['repo-branch'] + "; git pull"
    code, stdout, stderr = run_command(cmd)
    if verbose:
        print("Return code: ", code, " Stdout: ", stdout, " Stderr: ", stderr)
    return code

# Given swagger file, return swagger data in dict
def get_swagger_dict(file, is_yaml):
    if is_yaml:
        with open(file, 'r', encoding='utf-8') as f:
            swagger_data = ruamel.yaml.load(f, Loader=ruamel.yaml.Loader)
    else:
        with open(file, 'rb') as f:
            swagger_data = json.load(f)
    return swagger_data
