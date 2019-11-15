from java_sdk_config import *
import os
import logging
import re
import shutil
import subprocess
import os.path as path


JAVA_OUTPUT_MATCH = 'output-folder: $(azure-libraries-for-java-folder)/'
JAVA_OUTPUT_REPLACE = 'output-folder: $(azure-libraries-for-java-folder)/sdk/'


def main():
    logging.basicConfig(level=logging.WARNING)
    process_swagger()
    #process_swagger_all()
    process_sdk()


def process_swagger_all():
    if CLEAN_REPO:
        logging.info('git ckeckout clean')
        subprocess.Popen(['git', 'checkout', '.'], cwd=SDK_REPO).communicate()
        subprocess.Popen(['git', 'clean', '-fd'], cwd=SDK_REPO).communicate()

    sdk_dirs_processed = []

    for root, dirs, files in os.walk(path.join(SPEC_REPO, 'specification')):
        (head, tail) = path.split(root)
        if tail == 'resource-manager':
            (head1, sdk_dir) = path.split(head)
            for filename in files:
                if filename == 'readme.java.md' or filename == 'readme.md':
                    processed = process_readme_all(path.join(root, filename))
                    if processed:
                        sdk_dirs_processed.append(sdk_dir)

    logging.info('processed sdk dirs {}'.format(str(sdk_dirs_processed)))


def process_readme_all(filename):
    logging.info('process {}'.format(filename))

    modified = False
    modified_lines = []
    lines = read_lines(filename)
    for line in lines:
        if line.find(JAVA_OUTPUT_MATCH) != -1 and line.find('/resource-manager/v20') != -1:
            match = re.search(r'.*' + re.escape(JAVA_OUTPUT_MATCH) + r'(\w+)' + r'/resource-manager/v20.*', line)
            if match:
                modified = True
                sdk_name = match.group(1)
                modified_line = line.replace(JAVA_OUTPUT_MATCH + sdk_name + '/resource-manager', JAVA_OUTPUT_REPLACE + sdk_name + '/azure-mgmt-' + sdk_name)
                if modified_line != line:
                    line = modified_line
        modified_lines.append(line)
    if modified:
        logging.info('modify readme {}'.format(filename))
        write_lines(filename, modified_lines)
    return modified


def process_swagger():
    if CLEAN_REPO:
        logging.info('git ckeckout clean')
        subprocess.Popen(['git', 'checkout', '.'], cwd=SDK_REPO).communicate()
        subprocess.Popen(['git', 'clean', '-fd'], cwd=SDK_REPO).communicate()

    sdk_found = []
    sdk_processed = []

    for root, dirs, files in os.walk(path.join(SPEC_REPO, 'specification')):
        (head, tail) = path.split(root)
        if tail == 'resource-manager':
            (head1, sdk_dir) = path.split(head)
            if sdk_dir in SDK_SPEC_MAP.values():
                for sdk_name, sdk_dir1 in SDK_SPEC_MAP.items():
                    if sdk_dir1 == sdk_dir and sdk_name in SDK_TO_UPDATE:
                        sdk_found.append(sdk_name)
                        for filename in files:
                            if sdk_name not in sdk_processed and (filename == 'readme.java.md' or filename == 'readme.md'):
                                processed = process_readme(path.join(root, filename), sdk_name)
                                if processed:
                                    sdk_processed.append(sdk_name)
            else:
                sdk_name = sdk_dir
                if sdk_name in SDK_TO_UPDATE:
                    sdk_found.append(sdk_name)
                    for filename in files:
                        if sdk_name not in sdk_processed and (filename == 'readme.java.md' or filename == 'readme.md'):
                            processed = process_readme(path.join(root, filename), sdk_name)
                            if processed:
                                sdk_processed.append(sdk_name)

    sdk_not_processed = [item for item in SDK_TO_UPDATE if item not in sdk_processed]
    if sdk_not_processed:
        logging.warning('failed to process spec {}'.format(str(sdk_not_processed)))


def process_readme(filename, sdk_name):
    logging.info('process {} for {}'.format(filename, sdk_name))

    modified = False
    modified_lines = []
    lines = read_lines(filename)
    for line in lines:
        if line.find(JAVA_OUTPUT_MATCH + sdk_name + '/resource-manager') != -1:
            modified = True
            modified_line = line.replace(JAVA_OUTPUT_MATCH + sdk_name + '/resource-manager', JAVA_OUTPUT_REPLACE + sdk_name + '/azure-mgmt-' + sdk_name)
            if modified_line != line:
                line = modified_line
        modified_lines.append(line)
    if modified:
        logging.info('modify readme {}'.format(filename))
        write_lines(filename, modified_lines)
    return modified


def process_sdk():
    if CLEAN_REPO:
        logging.info('git ckeckout clean')
        subprocess.Popen(['git', 'checkout', '.'], cwd=SDK_REPO).communicate()
        subprocess.Popen(['git', 'clean', '-fd'], cwd=SDK_REPO).communicate()

    sdk_found = []
    sdk_processed = []

    sdk_list = []

    for root, dirs, files in os.walk(SDK_REPO):
        (head, tail) = path.split(root)
        if tail == 'resource-manager':
            (head1, sdk_name) = path.split(head)
            if sdk_name in SDK_TO_UPDATE:
                sdk_found.append(sdk_name)
                sdk_list.append((root, sdk_name))

    for (root, sdk_name) in sdk_list:
        processed = process_sdk_dir(root, sdk_name)
        if processed:
            sdk_processed.append(sdk_name)

    hybrid_pom_files = ['profiles/2018-03-01-hybrid/pom.xml', 'profiles/2019-03-01-hybrid/pom.xml']
    for hybrid_pom_file in hybrid_pom_files:
        hybrid_pom_filename = path.join(SDK_REPO, hybrid_pom_file)
        lines = read_lines(hybrid_pom_filename)
        modified_lines = []
        for line in lines:
            if line.find('resource-manager') != -1:
                sdk = line.split('/')[2]
                if sdk in sdk_processed:
                    line = line.replace(sdk + '/resource-manager/', 'sdk/' + sdk + '/azure-mgmt-' + sdk + '/')
            modified_lines.append(line)
        write_lines(hybrid_pom_filename, modified_lines)

    sdk_not_processed = [item for item in SDK_TO_UPDATE if item not in sdk_processed]
    if sdk_not_processed:
        logging.warning('failed to process sdk {}'.format(str(sdk_not_processed)))


def process_sdk_dir(sdk_dir, sdk_name):
    target_root_dir = path.join(SDK_REPO, 'sdk', sdk_name)
    target_dir = path.join(target_root_dir, 'azure-mgmt-' + sdk_name)
    os.makedirs(target_dir)

    sdk_dirs = []
    # copy files
    dirs = os.listdir(sdk_dir)
    for directory in dirs:
        source_dir = path.join(sdk_dir, directory)
        target_sdk_dir = path.join(target_dir, directory)
        logging.info('copy file/directory from {} to {}'.format(source_dir, target_sdk_dir))
        shutil.move(source_dir, target_sdk_dir)
        if path.isdir(target_sdk_dir):
            sdk_dirs.append(target_sdk_dir)
    # clean up
    dir_to_cleanup = path.abspath(path.join(sdk_dir, '..'))
    dirs = os.listdir(dir_to_cleanup)
    if len(dirs) != 1:
        logging.warning('sdk directory is not empty {}'.format(dir_to_cleanup))
        shutil.rmtree(path.join(dir_to_cleanup, 'resource-manager'))
    else:
        logging.info('delete directory {}'.format(dir_to_cleanup))
        shutil.rmtree(dir_to_cleanup)

    # nested pom.xml
    for sdk_dir in sdk_dirs:
        pom_filename = path.join(sdk_dir, 'pom.xml')
        if path.isfile(pom_filename):
            logging.info('modify pom {}'.format(pom_filename))
            lines = read_lines(pom_filename)
            lines = [line.replace(r'<relativePath>../../../pom.management.xml</relativePath>', r'<relativePath>../../../../pom.management.xml</relativePath>') for line in lines]
            write_lines(pom_filename, lines)
        else:
            logging.warning('pom not found {}'.format(pom_filename))

    # ci.yaml or ci.data.yaml
    candidate_ci_files = ['ci.yml', 'ci.data.yml']
    for ci_filename in candidate_ci_files:
        ci_filename = path.join(target_root_dir, ci_filename)
        if path.isfile(ci_filename):
            logging.info('modify yaml {}'.format(ci_filename))
            lines = read_lines(ci_filename)
            contain_exclude_clause = [line for line in lines if line.find('exclude:') != -1]
            if contain_exclude_clause:
                # append to exclude clause
                modified_lines = []
                paths_tag = False
                exclude_tag = False
                for line in lines:
                    if not paths_tag and line.find('paths:') != -1:
                        paths_tag = True
                    elif paths_tag and not exclude_tag and line.find('exclude:') != -1:
                        exclude_tag = True
                    elif paths_tag and exclude_tag and line.find('-') == -1:
                        paths_tag = False
                        exclude_tag = False
                        modified_lines.append('      - sdk/{service}/azure-mgmt-\n'.format(service=sdk_name))
                    modified_lines.append(line)
                write_lines(ci_filename, modified_lines)
            else:
                # new exclude clause, after include clause
                modified_lines = []
                paths_tag = False
                include_tag = False
                for line in lines:
                    if not paths_tag and line.find('paths:') != -1:
                        paths_tag = True
                    elif paths_tag and not include_tag and line.find('include:') != -1:
                        include_tag = True
                    elif paths_tag and include_tag and line.find('-') == -1:
                        paths_tag = False
                        include_tag = False
                        modified_lines.append('    exclude:\n')
                        modified_lines.append('      - sdk/{service}/azure-mgmt-\n'.format(service=sdk_name))
                    modified_lines.append(line)
                write_lines(ci_filename, modified_lines)

    # ci.mgmt.yaml
    exclude_dirs = ['microsoft-azure']
    dirs = os.listdir(target_root_dir)
    for directory in dirs:
        if path.isdir(path.join(target_root_dir, directory)):
            for exclude_dir_prefix in EXCLUDE_DIRS_PREFIX:
                if directory.startswith(exclude_dir_prefix) and exclude_dir_prefix not in exclude_dirs:
                    exclude_dirs.append(exclude_dir_prefix)
    yaml_filename = path.join(target_root_dir, 'ci.mgmt.yml')
    exclude_block = ''
    if exclude_dirs:
        exclude_block += '    exclude:\n'
        for exclude_dir in exclude_dirs:
            exclude_block += '      - sdk/{service}/{exclude_dir}\n'.format(service=sdk_name, exclude_dir=exclude_dir)
    yaml_output = YAML_TEMPLATE.format(service=sdk_name, excludes=exclude_block)
    logging.info('generate yaml {}'.format(yaml_filename))
    write_string(yaml_filename, yaml_output)

    # pom.mgmt.xml
    pom_filename = path.join(target_root_dir, 'pom.mgmt.xml')
    module_block = ''
    for sdk_dir in sdk_dirs:
        (head, tail) = path.split(sdk_dir)
        (head1, tail1) = path.split(head)
        module_block += '    <module>{dir}</module>\n'.format(dir=path.join(tail1, tail))
    pom_output = POM_TEMPLATE.format(service=sdk_name, modules=module_block)
    logging.info('generate pom {}'.format(pom_filename))
    write_string(pom_filename, pom_output)

    return True


def fix_exclude():
    for sdk_dir in os.listdir(path.join(SDK_REPO, 'sdk')):
        if ('azure-mgmt-' + sdk_dir) in os.listdir(path.join(SDK_REPO, 'sdk', sdk_dir)):
            candidate_ci_files = ['ci.yml', 'ci.data.yml']
            for ci_filename in candidate_ci_files:
                ci_filename = path.join(SDK_REPO, 'sdk', sdk_dir, ci_filename)
                if path.isfile(ci_filename):
                    logging.info('modify yaml {}'.format(ci_filename))
                    lines = read_lines(ci_filename)
                    lines = [line.replace('sdk/keyvault/azure-mgmt-', 'sdk/' + sdk_dir + '/azure-mgmt-') for line in lines]
                    write_lines(ci_filename, lines)


def read_lines(filename):
    with open(filename, 'r') as f:
        return f.readlines()


def write_lines(filename, lines):
    with open(filename, 'w') as f:
        f.writelines(lines)


def write_string(filename, text):
    with open(filename, 'w') as f:
        f.write(text)


main()
