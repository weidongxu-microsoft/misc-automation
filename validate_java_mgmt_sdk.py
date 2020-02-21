from java_sdk_config import *
import os
import logging
import subprocess
import os.path as path


def main():
    logging.basicConfig(level=logging.INFO)
    process_sdk()


def process_sdk():
    if CLEAN_REPO:
        logging.info('git ckeckout clean')
        subprocess.Popen(['git', 'checkout', '.'], cwd=SDK_REPO).communicate()
        subprocess.Popen(['git', 'clean', '-fd'], cwd=SDK_REPO).communicate()

    for sdk_name in os.listdir(path.join(SDK_REPO, 'sdk')):
        sdk_dir = path.join(SDK_REPO, 'sdk', sdk_name)
        if path.isdir(sdk_dir):
            process_sdk_dir(sdk_dir, sdk_name)


def process_sdk_dir(sdk_dir, sdk_name):
    mgmt_modules = []
    for module_dir in os.listdir(sdk_dir):
        if module_dir.startswith("mgmt-v"):
            mgmt_modules.append(module_dir)

    if mgmt_modules:
        # ci.mgmt.yaml
        yaml_filename = path.join(sdk_dir, 'ci.mgmt.yml')
        yaml_output = YAML_TEMPLATE.format(service=sdk_name)
        logging.info('generate yaml {}'.format(yaml_filename))
        write_string(yaml_filename, yaml_output)

        # pom.mgmt.xml
        pom_filename = path.join(sdk_dir, 'pom.mgmt.xml')
        module_block = ''
        for module_name in mgmt_modules:
            (head, tail) = path.split(sdk_dir)
            (head1, tail1) = path.split(head)
            module_block += '    <module>{dir}</module>\n'.format(dir=module_name)
        pom_output = POM_TEMPLATE.format(service=sdk_name, modules=module_block)
        logging.info('generate pom {}'.format(pom_filename))
        write_string(pom_filename, pom_output)


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
