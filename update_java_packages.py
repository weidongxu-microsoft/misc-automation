import os
import logging
import csv
from typing import List
from typing import Dict
from urllib.request import urlopen


SDK_REPO = 'c:/github/azure-sdk'
CSV_PATH = '_data/releases/latest/java-packages.csv'


def main():
    logging.basicConfig(level=logging.INFO)
    process_java_packages_csv()


def process_java_packages_csv():
    csv_filename = os.path.join(SDK_REPO, CSV_PATH)
    with open(csv_filename, newline='') as f:
        csv_reader = csv.DictReader(f, delimiter=',', quotechar='"')
        fieldnames = csv_reader.fieldnames
        rows_all = []
        for row in csv_reader:
            rows_all.append(row)

    rows = collect_new_arm_packages(rows_all)

    update_new_arm_packages(rows, rows_all)

    # rows_all = update_support(rows_all)

    with open(csv_filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

        writer.writeheader()
        for row in rows_all:
            writer.writerow(row)


def update_support(rows_all: List[Dict]) -> List[Dict]:
    rows = []
    for row in rows_all:
        if row['Support'] == '':
            sdk_name = row['Package']
            if sdk_name.startswith('azure-mgmt-'):
                row['Support'] = 'maintenance'
            elif sdk_name.startswith('azure-resourcemanager'):
                row['Support'] = 'preview' if row['VersionGA'] == '' else 'active'
        rows.append(row)
    return rows


def collect_new_arm_packages(rows_all: List[Dict]) -> List[Dict]:
    rows = []
    for row in rows_all:
        if row['GroupId'] == 'com.azure.resourcemanager' and row['New'] == 'false' and row['Hide'] == '':
            rows.append(row)
    return rows


def update_new_arm_packages(rows: List[Dict], rows_all: List[Dict]):
    for row in rows:
        sdk_name = row['Package'][len('azure-resourcemanager-'):]

        row['New'] = 'true'
        row['Hide'] = 'false'
        row['Type'] = 'mgmt'
        if row['RepoPath'] == 'NA':
            row['RepoPath'] = sdk_name

        try:
            readme_data = urlopen(f'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/{sdk_name}/resource-manager/readme.md').read()
            readme_str = readme_data.decode('utf-8')
            lines = readme_str.split('\n')
            for line in lines:
                if line.startswith('# '):
                    service_name = line[2:]
                    break
        except Exception as e:
            logging.exception(e)
            service_name = sdk_name
        row['ServiceName'] = service_name
        row['DisplayName'] = 'Resource Management - ' + service_name
        row['Support'] = 'preview' if row['VersionGA'] == '' else 'active'


main()
