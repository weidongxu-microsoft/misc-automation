import dataclasses
import logging
import csv
from urllib.request import urlopen


CSV_PATH = 'https://raw.githubusercontent.com/Azure/azure-sdk/master/_data/releases/latest/java-packages.csv'
TRACK1_PACKAGE_PREFIX = 'azure-mgmt-'
TRACK2_PACKAGE_PREFIX = 'azure-resourcemanager-'


@dataclasses.dataclass
class SdkInfo:
    sdk: str
    track1: bool = False
    track1_stable: bool = False
    track2: bool = False
    track2_stable: bool = False


def main():
    logging.basicConfig(level=logging.INFO)
    process_java_packages_csv()


def process_java_packages_csv():
    sdk_info = {}

    csv_data = urlopen(CSV_PATH).read()
    csv_str = csv_data.decode('utf-8')
    csv_reader = csv.DictReader(csv_str.split('\n'), delimiter=',', quotechar='"')
    for row in csv_reader:
        package = row['Package']
        version = row['VersionGA']
        if package.startswith(TRACK1_PACKAGE_PREFIX) and not version.startswith('0.'):
            sdk = package[len(TRACK1_PACKAGE_PREFIX):]
            if sdk not in sdk_info:
                sdk_info[sdk] = SdkInfo(sdk)
            sdk_info[sdk].track1 = True
            if not version == '':
                sdk_info[sdk].track1_stable = True
        if package.startswith(TRACK2_PACKAGE_PREFIX) and package != TRACK2_PACKAGE_PREFIX + 'parent':
            sdk = package[len(TRACK2_PACKAGE_PREFIX):]
            if sdk not in sdk_info:
                sdk_info[sdk] = SdkInfo(sdk)
            sdk_info[sdk].track2 = True
            if not version == '':
                sdk_info[sdk].track2_stable = True

    for item in sdk_info.values():
        print('{0: <32}{1: <16}{2: <16}'.format(item.sdk,
                                                'GA' if item.track1_stable else 'beta' if item.track1 else ' ',
                                                'GA' if item.track2_stable else 'beta' if item.track2 else ' '))


main()
