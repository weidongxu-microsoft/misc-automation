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
    logging.basicConfig(level=logging.INFO)
    process_sdk()
    process_package_md()


def process_package_md():
    lines = read_lines(path.join(SDK_REPO, 'packages.md'))
    modified_lines = []
    for line in lines:
        if line.find(r'/resource-manager/v20') != -1:
            match = re.search(r'.*\]\( (.*) \)\|.*', line)
            if match:
                origin = match.group(1)
                segs = origin.split('/')
                if len(segs) == 4:
                    sdk_name = segs[0]
                    module_name = segs[2]
                    pom_name = segs[3]
                    replace = 'sdk/' + sdk_name + '/mgmt-' + module_name + '/' + pom_name
                    line = re.sub(origin, replace, line)

                    if not path.isfile(path.join(SDK_REPO, replace)):
                        logging.warning('pom not found {}'.format(replace))
                else:
                    logging.warning('unexpected line {}'.format(line))
        modified_lines.append(line)
    write_lines(path.join(SDK_REPO, 'packages.md'), modified_lines)


def process_sdk():
    if CLEAN_REPO:
        logging.info('git ckeckout clean')
        subprocess.Popen(['git', 'checkout', '.'], cwd=SDK_REPO).communicate()
        subprocess.Popen(['git', 'clean', '-fd'], cwd=SDK_REPO).communicate()

    os.remove(path.join(SDK_REPO, 'sdk/containerservice/azure-mgmt-containerservice/pom.xml'))

    sdk_processed = []
    dir_skipped = []

    for sdk_name in os.listdir(path.join(SDK_REPO, 'sdk')):
        sdk_dir = path.join(SDK_REPO, 'sdk', sdk_name)
        if path.isdir(sdk_dir):
            processed = process_sdk_dir(sdk_dir, sdk_name)
            if processed:
                sdk_processed.append(sdk_name)
            else:
                dir_skipped.append(sdk_name)

    hybrid_pom_files = ['profiles/2018-03-01-hybrid/pom.xml', 'profiles/2019-03-01-hybrid/pom.xml']
    for hybrid_pom_file in hybrid_pom_files:
        hybrid_pom_filename = path.join(SDK_REPO, hybrid_pom_file)
        lines = read_lines(hybrid_pom_filename)
        modified_lines = []
        for line in lines:
            if line.find(r'<module>../../sdk/') != -1:
                segs = line.strip().replace(r'<module>', '').replace(r'</module>', '').split('/')
                sdk_name = segs[3]
                module_name = segs[5]
                line = r'    <module>../../sdk/' + sdk_name + '/mgmt-' + module_name + r'</module>' + '\n'
            modified_lines.append(line)
        write_lines(hybrid_pom_filename, modified_lines)

    logging.WARNING('skipped dir {}'.format(str(dir_skipped)))


def process_sdk_dir(sdk_dir, sdk_name):
    root_dir = path.join(SDK_REPO, 'sdk', sdk_name)
    source_dir = path.join(root_dir, 'azure-mgmt-' + sdk_name)

    if not path.isdir(source_dir):
        return False

    sdk_dirs = []
    # copy files
    dirs = os.listdir(source_dir)
    for directory in dirs:
        source_module_dir = path.join(source_dir, directory)
        if path.isdir(source_module_dir):
            target_module_dir = path.join(root_dir, 'mgmt-' + directory)
        logging.info('copy file/directory from {} to {}'.format(source_module_dir, root_dir))
        shutil.move(source_module_dir, target_module_dir)
        if path.isdir(target_module_dir):
            sdk_dirs.append(target_module_dir)
    # clean up
    dir_to_cleanup = path.abspath(source_dir)
    dirs = os.listdir(dir_to_cleanup)
    if len(dirs) != 0:
        logging.warning('sdk directory is not empty {}'.format(dir_to_cleanup))
    else:
        shutil.rmtree(dir_to_cleanup)

    # nested pom.xml
    for sdk_dir in sdk_dirs:
        pom_filename = path.join(sdk_dir, 'pom.xml')
        if path.isfile(pom_filename):
            logging.info('modify pom {}'.format(pom_filename))
            lines = read_lines(pom_filename)
            lines = [line.replace(r'<relativePath>../../../../pom.management.xml</relativePath>', r'<relativePath>../../../pom.management.xml</relativePath>') for line in lines]
            write_lines(pom_filename, lines)
        else:
            logging.warning('pom not found {}'.format(pom_filename))

    # ci.yaml or ci.data.yaml
    candidate_ci_files = ['ci.yml', 'ci.data.yml']
    for ci_filename in candidate_ci_files:
        ci_filename = path.join(root_dir, ci_filename)
        if path.isfile(ci_filename):
            logging.info('modify yaml {}'.format(ci_filename))
            lines = read_lines(ci_filename)
            lines = [line.replace('- sdk/{}/azure-mgmt-'.format(sdk_name), '- sdk/{}/mgmt-'.format(sdk_name)) for line in lines]
            write_lines(ci_filename, lines)

    # pom.mgmt.xml
    mgmt_pom = path.join(root_dir, 'pom.mgmt.xml')
    lines = read_lines(mgmt_pom)
    lines = [line.replace('<module>azure-mgmt-{}/'.format(sdk_name), '<module>mgmt-') for line in lines]
    write_lines(mgmt_pom, lines)

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
