import os
import logging
import json
from typing import Dict


SDK_REPO = 'c:/github/azure-libraries-for-java'


def main():
    logging.basicConfig(level=logging.INFO)
    process_session_records()


def process_session_records():
    for root, dirs, files in os.walk(SDK_REPO):
        for name in files:
            file_path = os.path.join(root, name)
            if os.path.splitext(file_path)[1] == '.json' \
                    and 'session-records' in file_path and 'target' not in file_path:
                with open(file_path, encoding='utf-8') as f:
                    try:
                        record = json.load(f)
                        found = analysis(record)
                        if found:
                            print(file_path)
                    except Exception as e:
                        logging.error(f'error {e}')


def analysis(record: Dict) -> bool:
    found = False
    records = record['networkCallRecords']
    for item in records:
        if item['Method'] == 'PUT' and item['Response']['StatusCode'] == '200' and 'azure-asyncoperation' in item['Response']:
            found = True
            break
    return found


main()
