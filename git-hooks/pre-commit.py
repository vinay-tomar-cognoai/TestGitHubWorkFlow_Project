#!/usr/bin/env python

import sys
import subprocess
import re

import ast
import os
from tqdm import tqdm
import inspect

_variable_names_blacklist = [
    'val',
    'vals',
    'var',
    'vars',
    'variable',
    'contents',
    'handle',
    'file',
    'objs',
    'some',
    'do',
    'no',
    'true',
    'false',
    'foo',
    'bar',
    'baz',
    'temp',
    'tmp'
]


def get_varname_errors(var_name, var_ast_node, filename, variable_name_error):
    errors = []
    warnings = []
    if (
        len(var_name) == 1
    ):
        errors.append((
            filename,
            var_ast_node.lineno,
            # var_ast_node.col_offset,
            "ERROR: SINGLE LETTER ERROR single letter variable names like '{0}' are not allowed".format(
                var_name),
        ))
    if var_name in _variable_names_blacklist:
        warnings.append((
            filename,
            var_ast_node.lineno,
            # var_ast_node.col_offset,
            "WARNING: Variable name '{0}' should be clarified, either replace it or clarify in PULL REQUEST".format(
                var_name),
        ))
    if var_name == 'print':
        errors.append((
            filename,
            var_ast_node.lineno,
            # var_ast_node.col_offset,
            "PRINT USED: Print statement used, please remove this",
        ))

    if(errors != None and errors != []):
        variable_name_error = 1
        for item in errors:
            error_message = ""
            for values in item:
                error_message += str(values) + ": "
            print(error_message)

    if(warnings != None and warnings != []):
        for item in warnings:
            warning_message = ""
            for values in item:
                warning_message += str(values) + ": "
            print(warning_message)

    return variable_name_error


def flat(some_list):
    flattened_list = []
    for sublist in some_list:
        for item in sublist:
            flattened_list.append(item)
    return flattened_list


def get_var_names_from_assignment(assignment_node: ast.AnnAssign):
    if isinstance(assignment_node, ast.AnnAssign):
        if isinstance(assignment_node.target, ast.Name):
            return [(assignment_node.target.id, assignment_node.target)]
    elif isinstance(assignment_node, ast.Assign):
        names = []
        for target in assignment_node.targets:
            if isinstance(target, ast.Name):
                names.append(target)

        variable_name_object = []
        for items in names:
            variable_name_object.append((items.id, items))
        return variable_name_object

    return []


def get_var_names_from_funcdef(funcdef_node: ast.FunctionDef):
    vars_info = []
    for arg in funcdef_node.args.args:
        vars_info.append(
            (arg.arg, arg),
        )
    return vars_info


def get_var_names_from_print(funcdef_node: ast.AST):
    vars_info = []
    for node in ast.walk(funcdef_node):
        if isinstance(node, ast.Name) and node.id == 'print':
            vars_info.append((node.id, node))
    return vars_info


def get_var_names_from_for(for_node: ast.For):
    if isinstance(for_node.target, ast.Name):
        return [(for_node.target.id, for_node.target)]
    elif isinstance(for_node.target, ast.Tuple):
        for_loop_var_names = []

        for node in for_node.target.elts:
            if isinstance(node, ast.Name):
                for_loop_var_names.append((node.id, node))
        return for_loop_var_names
    return []


def extract_all_variable_names(ast_tree: ast.AST):
    var_info = []
    assignments = [node for node in ast.walk(
        ast_tree) if isinstance(node, ast.Assign)]
    var_info += flat([get_var_names_from_assignment(assigned_var)
                      for assigned_var in assignments])
    ann_assignments = [node for node in ast.walk(
        ast_tree) if isinstance(node, ast.AnnAssign)]
    var_info += flat([get_var_names_from_assignment(assigned_var)
                      for assigned_var in ann_assignments])
    funcdefs = [node for node in ast.walk(
        ast_tree) if isinstance(node, ast.FunctionDef)]
    var_info += flat([get_var_names_from_funcdef(function_name)
                      for function_name in funcdefs])
    for_loop = [node for node in ast.walk(
        ast_tree) if isinstance(node, ast.For)]
    var_info += flat([get_var_names_from_for(for_name)
                      for for_name in for_loop])
    var_info += flat([get_var_names_from_print(ast_tree)])

    return var_info


def run(tree, filename, variable_name_error):
    variables_names = extract_all_variable_names(tree)
    for var_name, var_name_ast_node in variables_names:
        variable_name_error = variable_name_error or get_varname_errors(
            var_name, var_name_ast_node, filename, variable_name_error)

    return "", variable_name_error


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


def top_level_functions(body):
    return (f for f in body if isinstance(f, ast.FunctionDef))


def top_level_classes(body):
    return (f for f in body if isinstance(f, ast.ClassDef))


def check_for_logger_regex(filename):
    temp_str = ""
    # with open(filename, "r") as file:
    #     content = file.readlines()
    # content = [x.strip() for x in content]
    # for i, j in enumerate(content):
    #     if "except Exception as e" in j:
    #         if "exc_type, exc_obj, exc_tb = sys.exc_info()" not in content[i+1]:
    #             temp_str = "No logger found in file: " + \
    #                 str(filename)+" at line no. "+str(i+1)
    #             return False, temp_str
    #         elif ("logger.error" not in content[i+2]) and ("logger.warning" not in content[i+2]):
    #             temp_str = "No logger found in file: " + \
    #                 str(filename)+" at line no. "+str(i+1)
    #             return False, temp_str
    #         elif ("exc_tb.tb_lineno" not in content[i+2]) and ("exc_tb.tb_lineno" not in content[i+3]):
    #             temp_str = "No logger found in file: " + \
    #                 str(filename)+" at line no. "+str(i+1)
    #             return False, temp_str
    # return True, temp_str

    # print ([x.strip() for x in content])
    return True, temp_str


def parse_ast(filename):
    with open(filename, "rt") as file:
        return ast.parse(file.read(), filename=filename)


print(Bcolors.HEADER + "\nRunning Pre-commit checks...\n" + Bcolors.ENDC)

val5 = 0
val9 = 0
filename_lowercase_exception_str = ""
filename_format_exception_str = ""
function_name_length_exception_str = ""
class_name_length_exception_str = ""
logger_format_exception_str = ""
variable_name_error = 0

print(Bcolors.BOLD + "Running file/function name validators...\n" + Bcolors.ENDC)

for subdir, dirs, files in tqdm(list(os.walk(rootdir)), position=0, leave=True):
    for file in files:
        exclude_list = ["trumbowyg", "logtailer", "ace",
                        "migrations", "git-hooks", "cronjob_scripts", "DBMigrations"]
        if not len(set(subdir.split("/")) & set(exclude_list)) > 0:
            if file.endswith('.py'):
                if file.startswith('test') == False:

                    tree = parse_ast(os.path.join(
                        subdir, file))

                    filename = os.path.join(subdir, file)
                    result, variable_name_error = run(
                        tree, filename, variable_name_error)

            if file.endswith('.py') or file.endswith('.html'):

                if not file.islower():
                    if file not in ["jquery.dataTables.min.css", "Treant.css", "jquery.dataTables.css", "Chart.min.js", "Chart.js", "jquery.dataTables.min.js"]:
                        filename_lowercase_exception_str += os.path.join(
                            subdir, file) + "\n"
                        val5 = 1

                if not re.match("^[a-zA-Z0-9._-]+$", file):
                    if file not in ["style1.css", "style2.css", "style3.css", "json2.js", "index1.html", "wordcloud2.js", "font-awesome.min.css", "font-awesome.css", "theme3.html", "theme3_bot.html", "theme3.css", "theme3_embed.js", "theme3_embed.css", "theme3.js"]:
                        exclude_format_list = [
                            "jquery", "select2.min", "embed_chatbot"]
                        if not any(word in file.lower() for word in exclude_format_list):
                            filename_format_exception_str += os.path.join(
                                subdir, file) + "\n"
                            val5 = 1

                if file.endswith('.py'):

                    tree = parse_ast(os.path.join(
                        subdir, file))

                    logger_check_flag, logger_check_strg = check_for_logger_regex(os.path.join(
                        subdir, file))

                    if (not logger_check_flag):
                        val9 = 1
                        logger_format_exception_str += logger_check_strg + "\n"

                    for func in top_level_functions(tree.body):
                        if func.name == "DecryptVariable":
                            continue
                        if func.name.islower() or 'request' in [a.arg for a in func.args.args]:
                            if 'request' not in [a.arg for a in func.args.args]:
                                if len(func.name) > 30 and "_" not in func.name:
                                    function_name_length_exception_str += func.name + " in " + os.path.join(
                                        subdir, file) + "\n"
                                    val5 = 1
                        else:
                            function_name_length_exception_str += func.name + " in " + os.path.join(
                                subdir, file) + "\n"
                            val5 = 1

                    for clas in top_level_classes(tree.body):
                        if clas.name.islower() or "_" in clas.name:
                            class_name_length_exception_str += clas.name + " in " + os.path.join(
                                subdir, file) + "\n"
                            val5 = 1

print(Bcolors.BOLD + "\nChecking whether project working or not\n" + Bcolors.ENDC)

projectcheck = tqdm(position=0, leave=True, total=1)
val0 = subprocess.run('python ./manage.py check',
                      shell=True, stdout=subprocess.DEVNULL)
working_check = val0.returncode
projectcheck.update(1)

print(Bcolors.BOLD + "\nRunning Project TestCases\n" + Bcolors.ENDC)

projecttestscheck = tqdm(position=0, leave=True, total=1)
val8 = subprocess.run('python -W ignore ./manage.py test EasyChatApp.tests',
                      shell=True, stdout=subprocess.DEVNULL)

test_tms = subprocess.run('python -W ignore ./manage.py test EasyTMSApp/tests/',
                          shell=True, stdout=subprocess.DEVNULL)

test_livechat = subprocess.run('python -W ignore ./manage.py test LiveChatApp/tests/',
                               shell=True, stdout=subprocess.DEVNULL)

test_search = subprocess.run('python -W ignore ./manage.py test EasySearchApp/tests/',
                             shell=True, stdout=subprocess.DEVNULL)

test_assist = subprocess.run('python -W ignore ./manage.py test EasyAssistApp/tests/',
                             shell=True, stdout=subprocess.DEVNULL)

test_campaign = subprocess.run('python -W ignore ./manage.py test CampaignApp/tests/',
                                shell=True, stdout=subprocess.DEVNULL)

test_cases_check = val8.returncode + test_tms.returncode + \
    test_livechat.returncode + test_search.returncode + \
    test_assist.returncode + test_campaign.returncode
projecttestscheck.update(1)

print(Bcolors.BOLD + "\n\nChecking PEP8 format" + Bcolors.ENDC)

pep8check = tqdm(position=0, leave=True, total=4)

whitelisted_flake8_codes = "E722,N806,N813,E266,F402,F403,F404,F405,F406,F407,W504,W291,E501,E305,E711,E712,W293,W605,E127,F401,F601,N802,N803,E402"

val1 = subprocess.run('flake8 --ignore=F401 ./*.py', shell=True)

pep8check.update(1)

easychatapp_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + " ./EasyChatApp/*.py", shell=True)
easytmsapp_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + " ./EasyTMSApp/*.py", shell=True)
easysearchapp_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + " ./EasySearchApp/*.py", shell=True)
livechatapp_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + " ./LiveChatApp/*.py", shell=True)
easyassistapp_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + " ./EasyAssistApp/*.py", shell=True)
easyassist_salesforce_app_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + " ./EasyAssistSalesforceApp/*.py", shell=True)
audit_trail_app_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + " ./AuditTrailApp/*.py", shell=True)
campaignapp_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + " ./CampaignApp/*.py", shell=True)
developer_console_app_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + " ./DeveloperConsoleApp/*.py", shell=True)
oauthapp_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + " ./OAuthApp/*.py", shell=True)

pep8check.update(1)

easychatapp_tests_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + ",N806,F811,F841" + " ./EasyChatApp/tests/*.py", shell=True)
easytmsapp_tests_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + ",N806,F811,F841" + " ./EasyTMSApp/tests/*.py", shell=True)
easysearchapp_tests_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + ",N806,F811,F841" + " ./EasySearchApp/tests/*.py", shell=True)
livechatapp_tests_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + ",N806,F811,F841" + " ./LiveChatApp/test-folder/*.py", shell=True)
easyassistapp_tests_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + ",N806,F811,F841" + " ./EasyAssistApp/tests/*.py", shell=True)
campaignapp_tests_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + ",N806,F811,F841" + " ./CampaignApp/tests/*.py", shell=True)

pep8check.update(1)

easychatapp_scripts_check = subprocess.run(
    "flake8 --ignore=" + whitelisted_flake8_codes + " ./cronjob_scripts/*.py", shell=True)

pep8check.update(1)

pep8formattingcheck = val1.returncode + easychatapp_check.returncode + \
    easytmsapp_check.returncode + easysearchapp_check.returncode + \
    livechatapp_check.returncode + easychatapp_tests_check.returncode + easychatapp_scripts_check.returncode +\
    easysearchapp_tests_check.returncode + \
    easytmsapp_tests_check.returncode + livechatapp_tests_check.returncode + easyassistapp_check.returncode +\
    easyassistapp_tests_check.returncode + campaignapp_check.returncode + \
    oauthapp_check.returncode + campaignapp_tests_check.returncode + easyassist_salesforce_app_check.returncode + \
    audit_trail_app_check.returncode + developer_console_app_check.returncode

print(Bcolors.BOLD + "\n\n\nCounting no of modifications in a commit" + Bcolors.ENDC)

commitlimitcheck = tqdm(position=1, leave=True, total=2)

try:
    commitlimitcheck.update()
    val6 = subprocess.check_output(
        ' git diff HEAD --stat | grep ".py"', shell=True)
    val7 = subprocess.check_output(
        ' git diff HEAD --numstat | grep ".py"', shell=True)
    python_no_modifiactions = sum(
        [int(s) for s in val6.decode('utf-8').split() if s.isdigit()])
    python_no_insertions = sum(
        [int(s) for s in val7.decode('utf-8').split() if s.isdigit()][::2])
except subprocess.CalledProcessError:
    commitlimitcheck.update()
    python_no_modifiactions = 0
    python_no_insertions = 0
    commitlimitcheck.write(
        Bcolors.FAIL + "\nPython Files: No changes to commit " + Bcolors.ENDC)
try:
    commitlimitcheck.update()
    val6 = subprocess.check_output(
        ' git diff HEAD --stat | grep ".html\|.js\|.css"', shell=True)
    val7 = subprocess.check_output(
        ' git diff HEAD --numstat | grep ".html\|.js\|.css"', shell=True)
    staticfile_no_modifiactions = sum(
        [int(s) for s in val6.decode('utf-8').split() if s.isdigit()])
    staticfile_no_insertions = sum(
        [int(s) for s in val7.decode('utf-8').split() if s.isdigit()][::2])
except subprocess.CalledProcessError:
    commitlimitcheck.update()
    staticfile_no_modifiactions = 0
    staticfile_no_insertions = 0
    commitlimitcheck.write(
        Bcolors.FAIL + "Static Files(html/js/css): No changes to commit " + Bcolors.ENDC)
print("\n")

print("Python Files: Total modifications: {0}, Total Insertions: {1}".format(
    python_no_modifiactions, python_no_insertions))
print("Static Files(html/js/css): Total modifications: {0}, Total Insertions: {1}".format(
    staticfile_no_modifiactions, staticfile_no_insertions))
commit_changes_count_check = 0
if python_no_modifiactions > 150 or python_no_insertions > 70:
    print(Bcolors.FAIL +
          "\nPython Files: You can cannot commit more than 50 lines of changes" + Bcolors.ENDC)
    commit_changes_count_check = 1
if staticfile_no_modifiactions > 300 or staticfile_no_insertions > 200:
    print(Bcolors.FAIL +
          "\nStatic Files(html/js/css): You can cannot commit more than 150 lines of changes" + Bcolors.ENDC)
    commit_changes_count_check = 1

if (filename_lowercase_exception_str == "" and
        filename_format_exception_str == "" and
        function_name_length_exception_str == "" and
        class_name_length_exception_str == "" and variable_name_error == 0):
    print(Bcolors.OKBLUE + "\nfile/function name check... " +
          Bcolors.OKGREEN + Bcolors.BOLD + "PASSED" + Bcolors.ENDC)
else:
    print(Bcolors.OKBLUE + "\nfile/function name check... " +
          Bcolors.FAIL + Bcolors.BOLD + "FAILED" + Bcolors.ENDC)
if filename_lowercase_exception_str != "":
    print(Bcolors.FAIL + "\nPlease make sure that file name is in lowercase. Following files found to be wrong format" + Bcolors.ENDC)
    print("\n" + filename_lowercase_exception_str + "\n")

if filename_format_exception_str != "":
    print(Bcolors.FAIL + "\nPlease make sure that file name does not contains anything other than letters and underscore. Following files found to be wrong format" + Bcolors.ENDC)
    print("\n" + filename_format_exception_str + "\n")


if function_name_length_exception_str != "":
    print(Bcolors.FAIL + "\nFollowing function names in files found to be of length more than the limit(30)" + Bcolors.ENDC)
    print("\n" + function_name_length_exception_str + "\n")

if class_name_length_exception_str != "":
    print(Bcolors.FAIL + "\nFollowing class names in files found to be in wrong format" + Bcolors.ENDC)
    print("\n" + class_name_length_exception_str + "\n")

if val9 != 0:
    print(Bcolors.FAIL + "\nFollowing File contains logger in wrong format" + Bcolors.ENDC)
    print("\n" + logger_format_exception_str + "\n")

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

if val9 != 0:
    print(Bcolors.OKBLUE + "\nProject logger format check... " +
          Bcolors.FAIL + Bcolors.BOLD + "FAILED" + Bcolors.ENDC)
else:
    print(Bcolors.OKBLUE + "\nProject logger format check... " +
          Bcolors.OKGREEN + Bcolors.BOLD + "PASSED" + Bcolors.ENDC)

if pep8formattingcheck != 0:
    print(Bcolors.OKBLUE + "\nPEP8 Formatting check... " +
          Bcolors.FAIL + Bcolors.BOLD + "FAILED" + Bcolors.ENDC)
else:
    print(Bcolors.OKBLUE + "\nPEP8 Formatting check... " +
          Bcolors.OKGREEN + Bcolors.BOLD + "PASSED" + Bcolors.ENDC)

commit_changes_count_check = 0

if commit_changes_count_check != 0:
    print(Bcolors.OKBLUE + "\nCommit Changes Count check... " +
          Bcolors.FAIL + Bcolors.BOLD + "FAILED" + Bcolors.ENDC)
else:
    print(Bcolors.OKBLUE + "\nCommit Changes Count check... " +
          Bcolors.OKGREEN + Bcolors.BOLD + "PASSED" + Bcolors.ENDC)


if (pep8formattingcheck + val5 + working_check + commit_changes_count_check + test_cases_check + val9) != 0:
    print(Bcolors.FAIL + Bcolors.BOLD +
          "\nPlease do the appropriete changes in the code" + Bcolors.ENDC)
    sys.exit(1)
else:
    print(Bcolors.OKGREEN + Bcolors.BOLD +
          "\nHurray!!! ALL CHECKS PASSED" + Bcolors.ENDC)
    sys.exit(0)
