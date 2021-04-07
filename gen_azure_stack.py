import dataclasses
import os
import logging
import platform
import re
import json
import subprocess
from typing import List


# controls
TOGGLE_PATCH_README = True
TOGGLE_GENERATE_SDK = True
TOGGLE_GENERATE_ARM_CODE = True


SPEC_REPO = 'c:/github/azure-rest-api-specs'
PROFILE_PATH = 'profile/2020-09-01-hybrid.json'

TAG_PROFILE = 'package-profile-2020-09-01-hybrid'

SDK_OUTPUT_PATH = 'c:/github_lab/azure-stack-java-samples/azure-resourcemanager-hybrid'
SDK_AZS_NAMESPACE = 'hybrid'

AUTOREST_JAVA_PATH = 'c:/github_fork/autorest.java'
AUTOREST_CORE_VERSION = '3.1.3'
OS_WINDOWS = platform.system().lower() == 'windows'


@dataclasses.dataclass
class SpecInfo:
    type: str
    api_version: str
    spec_path: str


@dataclasses.dataclass
class SpecInfoCollection:
    provider: str
    spec_info_list: List[SpecInfo] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class SpecTag:
    sdk_name: str
    sdk_namespace: str = dataclasses.field(compare=False)
    readme_path: str = dataclasses.field(compare=False)
    tag: str = dataclasses.field(default=TAG_PROFILE, compare=False)


@dataclasses.dataclass
class Manager:
    class_name: str
    variable_name: str
    method_name: str


def main():
    logging.basicConfig(level=logging.INFO)
    process_profile()


def process_profile():
    spec_info_collection_dict = {}

    profile_path = os.path.join(SPEC_REPO, PROFILE_PATH)
    with open(profile_path, encoding='utf-8') as f:
        profile_dict = json.load(f)
        resource_manager_dict = profile_dict['resource-manager']
        for entry in resource_manager_dict.items():
            resource_provider = entry[0]
            if resource_provider not in spec_info_collection_dict:
                spec_info_collection_dict[resource_provider] = SpecInfoCollection(resource_provider)
            resource_version_dict = entry[1]
            for entry1 in resource_version_dict.items():
                resource_version = entry1[0]
                resource_type_array = entry1[1]
                for item in resource_type_array:
                    resource_type = item['resourceType']
                    spec_path = item['path']
                    spec_info_collection_dict[resource_provider].spec_info_list.append(SpecInfo(resource_type,
                                                                                                resource_version,
                                                                                                spec_path))

    spec_tag_list = []
    for item in spec_info_collection_dict.values():
        spec_tag = process_spec(item)
        spec_tag_list.append(spec_tag)

    if TOGGLE_GENERATE_SDK:
        for item in spec_tag_list:
            codegen(item, SDK_OUTPUT_PATH)

    if TOGGLE_GENERATE_ARM_CODE:
        generate_arm_code(spec_tag_list)


def process_spec(spec_info_collection: SpecInfoCollection) -> SpecTag:
    provider_name = spec_info_collection.provider.split(".")[1]
    sdk_name_set = set()
    sdk_name = None
    for item in spec_info_collection.spec_info_list:
        sdk_name = re.match('.*/specification/(.*)/resource-manager/.*', item.spec_path).group(1)
        sdk_name_set.add(sdk_name)
    if len(sdk_name_set) == 1:
        sdk_name = sdk_name_set.pop()
    else:
        for name in sdk_name_set:
            if name == provider_name:
                sdk_name = name
                break

    # hack
    sdk_namespace = sdk_name
    if sdk_name == 'web':
        sdk_namespace = 'appservice'
    elif sdk_name == 'eventhub':
        sdk_namespace = 'eventhubs'

    readme_path = os.path.join(SPEC_REPO, 'specification', sdk_name, 'resource-manager/readme.md')

    if TOGGLE_PATCH_README:
        spec_path_list = [item.spec_path for item in spec_info_collection.spec_info_list]
        spec_path_list = list(set(spec_path_list))
        patch_readme(readme_path, spec_path_list)

    return SpecTag(sdk_name, sdk_namespace, readme_path, TAG_PROFILE)


def patch_readme(readme_path: str, spec_path_list: List[str]):
    logging.info(f'patch readme.md file {readme_path} for tag {TAG_PROFILE}')

    lines = []
    with open(readme_path, 'r', encoding='utf-8') as f:
        lines.extend(f.readlines())

    lines.append("```yaml $(tag) == '" + TAG_PROFILE + "'\n")
    lines.append('input-file:\n')
    for spec_path in spec_path_list:
        lines.append('  - ' + spec_path + '\n')

    with open(readme_path, 'w', encoding='utf-8') as f:
        content = ''.join(lines)
        f.write(content)


def codegen(spec_tag: SpecTag, output_sdk_dir: str) -> subprocess.CompletedProcess:
    logging.info(f'generate code for RP: {spec_tag.sdk_name}')

    namespace = f'com.azure.resourcemanager.{SDK_AZS_NAMESPACE}.{spec_tag.sdk_namespace}'.lower()
    namespace = re.sub('[^a-z.]', '', namespace)

    command = [
        'autorest' + ('.cmd' if OS_WINDOWS else ''),
        # '--verbose',
        '--version=' + AUTOREST_CORE_VERSION,
        '--java',
        '--use=' + AUTOREST_JAVA_PATH,
        '--tag=' + TAG_PROFILE,
        '--regenerate-pom=false',
        '--pipeline.modelerfour.additional-checks=false',
        '--pipeline.modelerfour.lenient-model-deduplication=true',
        '--azure-arm',
        '--fluent=lite',
        '--java.fluent=lite',
        '--java.license-header=MICROSOFT_MIT_SMALL',
        '--java.output-folder=' + output_sdk_dir,
        '--java.namespace=' + namespace,
        spec_tag.readme_path]

    # hack
    if spec_tag.sdk_name == 'resources':
        command.append('--title=ResourceManagementClient')
    if spec_tag.sdk_name == 'authorization':
        command.append('--title=AuthorizationManagementClient')

    logging.info(' '.join(command))
    result = subprocess.run(command, capture_output=False, text=True, encoding='utf-8')
    return result


def generate_arm_code(spec_tag_list: List[SpecTag]):
    manager_list = []
    for spec_tag in spec_tag_list:
        code_path = os.path.join(SDK_OUTPUT_PATH, 'src/main/java/com/azure/resourcemanager',
                                 SDK_AZS_NAMESPACE, spec_tag.sdk_namespace)
        for file in os.listdir(code_path):
            if file.endswith('Manager.java'):
                class_name = file.split('.')[0]
                variable_name = class_name[0].lower() + class_name[1:]
                method_name = variable_name[0:len(variable_name) - len('Manager')]
                manager_list.append(Manager(class_name, variable_name, method_name))
                break

    # variables
    for manager in manager_list:
        print(f'private final {manager.class_name} {manager.variable_name};\n')

    # methods
    for manager in manager_list:
        print((f'/** @return the {{@link {manager.class_name}}}. */\n'
               f'public {manager.class_name} {manager.method_name}() {{\n'
               f'    return {manager.variable_name};\n'
               f'}}\n'))

    # initialization
    for manager in manager_list:
        print(f'{manager.class_name}.Configurable {manager.variable_name}Configurable = {manager.class_name}.configure();')
    print()
    print('''HttpClient httpClient = configurable.httpClient;
if (httpClient == null) {
    httpClient = HttpClient.createDefault();
}
if (httpClient != null) {''')
    for manager in manager_list:
        print(f'   {manager.variable_name}Configurable.withHttpClient(httpClient);')
    print('''}
if (configurable.httpLogOptions != null) {''')
    for manager in manager_list:
        print(f'   {manager.variable_name}Configurable.withLogOptions(configurable.httpLogOptions);')
    print('''}
if (configurable.retryPolicy != null) {''')
    for manager in manager_list:
        print(f'   {manager.variable_name}Configurable.withRetryPolicy(configurable.retryPolicy);')
    print('''}
for (HttpPipelinePolicy policy : configurable.policies) {''')
    for manager in manager_list:
        print(f'   {manager.variable_name}Configurable.withPolicy(policy);')
    print('''}
if (configurable.defaultPollInterval != null) {''')
    for manager in manager_list:
        print(f'   {manager.variable_name}Configurable.withDefaultPollInterval(configurable.defaultPollInterval);')
    print('}')
    print()
    for manager in manager_list:
        print(f'this.{manager.variable_name} = {manager.variable_name}Configurable.authenticate(credential, profile);')


main()
