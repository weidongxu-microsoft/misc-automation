import dataclasses
import logging
import csv
import re
from typing import List
from urllib.request import urlopen


CSV_PATH = 'https://raw.githubusercontent.com/Azure/azure-sdk/master/_data/releases/latest/java-packages.csv'
TRACK1_PACKAGE_PREFIX = 'azure-mgmt-'
TRACK2_PACKAGE_PREFIX = 'azure-resourcemanager-'
CSV_FILENAME = 'compare_java_packages.csv'


@dataclasses.dataclass
class SdkInfo:
    sdk: str
    track1: bool = False
    track1_stable: bool = False
    track1_api_version: str = None
    track2: bool = False
    track2_stable: bool = False
    track2_api_version: str = None

    def to_row(self) -> List[str]:
        return [self.sdk,
                ('GA' if self.track1_stable else 'beta') if self.track1 else None,
                ('GA' if self.track2_stable else 'beta') if self.track2 else None,
                self.track1_api_version,
                self.track2_api_version]


def main():
    logging.basicConfig(level=logging.INFO)
    process_java_packages_csv()


def process_java_packages_csv():
    sdk_info = {}

    logging.info(f'query csv: {CSV_PATH}')
    csv_data = urlopen(CSV_PATH).read()
    csv_str = csv_data.decode('utf-8')
    csv_reader = csv.DictReader(csv_str.split('\n'), delimiter=',', quotechar='"')
    for row in csv_reader:
        package = row['Package']
        namespace = row['GroupId']
        version = row['VersionGA']
        if package.startswith(TRACK1_PACKAGE_PREFIX) and not version.startswith('0.'):
            sdk = package[len(TRACK1_PACKAGE_PREFIX):]
            if sdk not in sdk_info:
                sdk_info[sdk] = SdkInfo(sdk)
            sdk_info[sdk].track1 = True
            if not version == '':
                sdk_info[sdk].track1_stable = True
            # update version, take the latest
            sdk_info[sdk].track1_api_version = compare_version(namespace.split('.')[-1],
                                                               sdk_info[sdk].track1_api_version)
        if package.startswith(TRACK2_PACKAGE_PREFIX) and package != TRACK2_PACKAGE_PREFIX + 'parent':
            sdk = package[len(TRACK2_PACKAGE_PREFIX):]
            if sdk not in sdk_info:
                sdk_info[sdk] = SdkInfo(sdk)
            sdk_info[sdk].track2 = True
            if not version == '':
                sdk_info[sdk].track2_stable = True
            sdk_info[sdk].track2_api_version = get_track2_version(
                package,
                row['VersionPreview'] if version == '' else version)

    print('{0: <32}{1: <16}{2: <16}{3: <16}{4: <16}'.format(
        'service', 'track1', 'track2', 'track1 api', 'track2 api'))
    print()

    sdk_info_list = [item for item in sdk_info.values()]
    sdk_info_list.sort(key=lambda r: ('2.' if r.track2_api_version else '1.') + r.sdk)

    for item in sdk_info_list:
        print('{0: <32}{1: <16}{2: <16}{3: <16}{4: <16}'.format(
            item.sdk,
            ('GA' if item.track1_stable else 'beta') if item.track1 else ' ',
            ('GA' if item.track2_stable else 'beta') if item.track2 else ' ',
            item.track1_api_version if item.track1_api_version else ' ',
            item.track2_api_version if item.track2_api_version else ' '))

    logging.info(f'write csv: {CSV_FILENAME}')
    with open(CSV_FILENAME, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(['service', 'track1', 'track2', 'track1 api', 'track2 api'])
        for item in sdk_info_list:
            writer.writerow(item.to_row())


def get_track2_version(package: str, version: str) -> str or None:
    if re.match(r'^2.\d{1,2}.\d{1,2}$', version):
        return 'premium'

    group_url = 'https://repo1.maven.org/maven2/com/azure/resourcemanager'
    pom_url = f'{group_url}/{package}/{version}/{package}-{version}.pom'

    logging.info(f'query pom: {pom_url}')
    pom_data = urlopen(pom_url).read()
    pom_str = pom_data.decode('utf-8')

    matched = re.search(r'Package tag (.+)\.<', pom_str, re.MULTILINE)
    tag = None
    if matched:
        tag = matched.group(1)
    else:
        matched = re.search(r'Package tag (.+)\. For ', pom_str, re.MULTILINE)
        if matched:
            tag = matched.group(1)
    if tag:
        version = tag.replace('package-', '').replace('-', '_').replace('_preview', '')

        # delete prefix before year
        if re.match(r'.*_20\d{2}_\d{2}', version):
            loc = version.find('_20')
            version = version[loc+1:]

        if re.match(r'^\d{4}_\d{2}$', version):
            version = version + '_01'
        return version
    else:
        return None


def compare_version(current_ver: str, exist_ver: str) -> str:
    current_ver = current_ver.replace('_preview', '')

    if current_ver.startswith('v') and (not exist_ver or current_ver > exist_ver):
        return current_ver[1:]
    else:
        return exist_ver


main()
