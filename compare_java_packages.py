import dataclasses
import logging
import csv
import re
import os
from typing import List
from urllib.request import urlopen


CSV_PATH = 'https://raw.githubusercontent.com/Azure/azure-sdk/master/_data/releases/latest/java-packages.csv'
TRACK1_PACKAGE_PREFIX = 'azure-mgmt-'
TRACK2_PACKAGE_PREFIX = 'azure-resourcemanager-'
CSV_FILENAME = 'compare_java_packages.csv'

SWAGGER_METADATA_FILENAME = 'swagger_metadata.csv'
KPI_LAST_30D_FILENAME = 'kpi_last_30d.csv'


@dataclasses.dataclass
class SdkInfo:
    sdk: str
    track1: bool = False
    track1_stable: bool = False
    track1_api_version: str = None
    track2: bool = False
    track2_stable: bool = False
    track2_api_version: str = None

    ring: str = None
    traffic: float = None
    completeness: float = None
    correctness: float = None

    def to_row(self) -> List[str]:
        return [self.sdk,
                ('GA' if self.track1_stable else 'beta') if self.track1 else None,
                ('GA' if self.track2_stable else 'beta') if self.track2 else None,
                self.track1_api_version,
                self.track2_api_version]


@dataclasses.dataclass
class KpiInfo:
    namespace: str
    name: str
    ring: str
    traffic: float = None
    completeness: float = None
    correctness: float = None


def run():
    logging.basicConfig(level=logging.INFO)
    sdk_info_list = process_java_packages_csv()
    join_kpi_csv(sdk_info_list)
    print_stdout(sdk_info_list)
    write_csv(sdk_info_list)


def process_java_packages_csv() -> List[SdkInfo]:
    sdk_info = {}

    logging.info(f'query csv: {CSV_PATH}')
    with urlopen(CSV_PATH) as csv_response:
        csv_data = csv_response.read()
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

    sdk_info_list = [item for item in sdk_info.values()]
    sdk_info_list.sort(key=lambda r: ('2.' if r.track2_api_version else '1.') + r.sdk)

    return sdk_info_list


def join_kpi_csv(sdk_info_list: List[SdkInfo]):
    if not os.path.isfile(SWAGGER_METADATA_FILENAME) or not os.path.isfile(KPI_LAST_30D_FILENAME):
        return

    swagger_info = {}
    with open(SWAGGER_METADATA_FILENAME, 'r', newline='', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for row in csv_reader:
            namespace = row['ProviderNamespace'].strip().upper()
            if namespace.startswith('MICROSOFT.'):
                swagger_info[row['specRootFolderName']] = namespace

    kpi_info = {}
    with open(KPI_LAST_30D_FILENAME, 'r', newline='', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for row in csv_reader:
            namespace = row['resourceProviderName'].strip().upper()
            if namespace.startswith('MICROSOFT.'):
                kpi_item = KpiInfo(namespace, row['ServiceName'].strip(), row['ServiceRing'].strip(),
                                   float(row['trafficCount']), float(row['completeness']), float(row['correctness']))
                if namespace not in kpi_info:
                    kpi_info[namespace] = []
                kpi_info[namespace].append(kpi_item)

    for item in sdk_info_list:
        if item.sdk in swagger_info:
            namespace = swagger_info[item.sdk]
            if namespace in kpi_info:
                kpi_items = kpi_info[namespace]

                found = False
                if len(kpi_items) > 1:
                    for kpi_item in kpi_items:
                        if item.sdk in kpi_item.name.lower().replace(' ', ''):
                            found = True
                            item.ring = kpi_item.ring
                            item.traffic = kpi_item.traffic
                            item.completeness = kpi_item.completeness
                            item.correctness = kpi_item.correctness
                            break

                    if not found:
                        logging.info('sdk: ' + item.sdk)
                        logging.info('multiple service candidates: ' + str([r.name for r in kpi_items]))

                if not found:
                    kpi_item = kpi_items[0]
                    item.ring = kpi_item.ring
                    item.traffic = kpi_item.traffic
                    item.completeness = kpi_item.completeness
                    item.correctness = kpi_item.correctness


def print_stdout(sdk_info_list: List[SdkInfo]):
    known_track1_alias = ['cosmosdb',       # cosmos
                          'eventhub',       # eventhubs
                          'features',
                          'graph-rbac',     # authentication
                          'locks',
                          'media',          # mediaservices
                          'policy',
                          'website'         # appservice
                          ]

    print(f'Number of track1 packages: '
          + str(len([item for item in sdk_info_list
                     if item.track1 and (item.track1_api_version or item.track1_stable)])))
    print(f'Number of track2 packages: '
          + str(len([item for item in sdk_info_list if item.track2])))
    print(f'Number of track1 packages not having track2: '
          + str(len([item for item in sdk_info_list
                     if item.track1 and (item.track1_api_version or item.track1_stable)
                     and (not item.track2 and item.sdk not in known_track1_alias)])))
    print()

    print('{0: <32}{1: <16}{2: <16}{3: <16}{4: <16}'.format(
        'service', 'track1', 'track2', 'track1 api', 'track2 api', 'ring', 'traffic', 'completeness', 'coverage'))
    print()

    xround = lambda r, n: None if r is None else round(r, n)
    xstr = lambda s: '' if s is None else str(s)

    for item in sdk_info_list:
        print('{0: <32}{1: <16}{2: <16}{3: <16}{4: <16}{5: <16}{6: <16}{7: <16}{8: <16}'.format(
            item.sdk,
            ('GA' if item.track1_stable else 'beta') if item.track1 else '',
            ('GA' if item.track2_stable else 'beta') if item.track2 else '',
            xstr(item.track1_api_version), xstr(item.track2_api_version),
            xstr(item.ring), xstr(xround(item.traffic, 0)),
            xstr(xround(item.completeness, 2)), xstr(xround(item.correctness, 2))))


def write_csv(sdk_info_list: List[SdkInfo]):
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


if __name__ == "__main__":
    run()
