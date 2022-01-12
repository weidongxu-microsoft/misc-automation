import dataclasses
import logging
import csv
import requests
from typing import List
from urllib.request import urlopen


CSV_URL = 'https://raw.githubusercontent.com/Azure/azure-sdk/master/_data/releases/latest/java-packages.csv'
TRACK1_PACKAGE_PREFIX = 'azure-mgmt-'
TRACK2_PACKAGE_PREFIX = 'azure-resourcemanager-'

MIGRATION_LINK = 'https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/resourcemanager/docs/MIGRATION_GUIDE.md'

CSV_FILENAME = 'deprecate_java_packages.csv'

SERVICE_NAME_MAP = {
    'cosmosdb': 'cosmos',
    'datalake-analytics': 'datalakeanalytics',
    'datalake-store': 'datalakestore',
    'datalake-store-uploader': 'datalakestore',
    'devices': 'deviceprovisioningservices',
    'devtestlab': 'devtestlabs',
    'documentdb': 'cosmos',
    'eventhub': 'eventhubs',
    'features': 'resources',
    'graph-rbac': 'authorization',
    'insights': 'monitor',
    'locks': 'resources',
    'machinelearning': 'machinelearningservices',
    'media': 'mediaservices',
    'dbformariadb': 'mariadb',
    'policy': 'resources',
    'powerbi': 'powerbidedicated',
    'samples': 'resources',
    'scheduler': 'resources',
    'subscriptions': 'resources',
    'traffic-manager': 'trafficmanager',
    'utility': 'resources',
    'website': 'appservice',
    'websites': 'appservice',
}


@dataclasses.dataclass
class Sdk:
    service: str
    package: str
    artifact: str


@dataclasses.dataclass
class SdkInfo:
    service: str
    t1_package: str
    t1_artifact: str
    t2_artifact: str

    def to_row(self) -> List[str]:
        return [self.service, 'Java', self.t1_maven_url(), self.t2_maven_url(), MIGRATION_LINK]

    def t1_maven_url(self):
        return f'https://mvnrepository.com/artifact/{self.t1_package}/{self.t1_artifact}'

    def t2_maven_url(self):
        return f'https://mvnrepository.com/artifact/com.azure.resourcemanager/{self.t2_artifact}'


def process_java_packages_csv() -> List[SdkInfo]:
    logging.info(f'query csv: {CSV_URL}')
    with urlopen(CSV_URL) as csv_response:
        csv_data = csv_response.read()
        csv_str = csv_data.decode('utf-8')
        csv_reader = csv.DictReader(csv_str.split('\n'), delimiter=',', quotechar='"')

    t1_sdks = []
    t2_sdks = {}
    for row in csv_reader:
        package = row['Package']
        namespace = row['GroupId']
        if package.startswith(TRACK1_PACKAGE_PREFIX):
            service = package[len(TRACK1_PACKAGE_PREFIX):]
            if service in SERVICE_NAME_MAP:
                service = SERVICE_NAME_MAP[service]
            sdk = Sdk(service, namespace, package)
            t1_sdks.append(sdk)
        elif package == 'azure':
            service = ''
            sdk = Sdk(service, namespace, package)
            t1_sdks.append(sdk)

        if package.startswith(TRACK2_PACKAGE_PREFIX) and package != TRACK2_PACKAGE_PREFIX + 'parent':
            service = package[len(TRACK2_PACKAGE_PREFIX):]
            sdk = Sdk(service, namespace, package)
            t2_sdks[service] = sdk
        elif package == 'azure-resourcemanager':
            service = ''
            sdk = Sdk(service, namespace, package)
            t2_sdks[service] = sdk

    t1_sdks.sort(key=lambda r: r.service)

    sdk_info_list = []
    for sdk in t1_sdks:
        t2_sdk = None
        if sdk.service in t2_sdks:
            t2_sdk = t2_sdks[sdk.service]
        if not t2_sdk:
            print(sdk.service)

        sdk_info = SdkInfo(sdk.service, sdk.package, sdk.artifact, t2_sdk.artifact if t2_sdk else '')
        sdk_info_list.append(sdk_info)

    # sdk_info_list.append(SdkInfo('', 'com.microsoft.azure', 'azure', 'azure-resourcemanager'))

    return sdk_info_list


def run():
    logging.basicConfig(level=logging.INFO)
    sdk_info_list = process_java_packages_csv()
    write_csv(sdk_info_list)

    validate_maven_packages(sdk_info_list)


def write_csv(sdk_info_list: List[SdkInfo]):
    logging.info(f'write csv: {CSV_FILENAME}')
    with open(CSV_FILENAME, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(['Service', 'Language',
                         'Legacy package (package being replaced)',
                         'New Packages that replace the legacy package on the left',
                         'Migration Guide link'])
        for item in sdk_info_list:
            writer.writerow(item.to_row())


def validate_maven_packages(sdk_info_list: List[SdkInfo]):
    for sdk_info in sdk_info_list:
        check_maven_url(sdk_info.t1_maven_url())
        check_maven_url(sdk_info.t2_maven_url())


def check_maven_url(url: str):
    url = url\
              .replace('mvnrepository.com', 'mvnrepository#com')\
              .replace('.', '/')\
              .replace('mvnrepository#com', 'mvnrepository.com')\
              .replace('https://mvnrepository.com/artifact/', 'https://repo1.maven.org/maven2/') + '/maven-metadata.xml'
    r = requests.get(url)
    logging.info(f'check url {url}, status code {r.status_code}')
    r.raise_for_status()


if __name__ == "__main__":
    run()
