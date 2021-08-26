import base64
import os
import re
import logging


# SDK_REPO = 'c:/github/azure-sdk-for-java/sdk/resourcemanager'
SDK_REPO = 'c:/github/azure-libraries-for-net'
RESOURCE_PROVIDER = 'Microsoft.Resources'
VERSION_CHANGES = {
    '2019-08-01': '2021-01-01'
}


def main():
    logging.basicConfig(level=logging.INFO)
    process_session_records()


def process_session_records():
    for root, dirs, files in os.walk(SDK_REPO):
        for name in files:
            filepath = os.path.join(root, name)
            if os.path.splitext(filepath)[1] == '.json' \
                    and 'SessionRecords' in filepath and 'netcoreapp2.0' not in filepath:
                update(filepath)


def update(filepath: str):
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    uri = None
    out_lines = []
    for line in lines:
        if '"RequestUri"' in line and f'/providers/{RESOURCE_PROVIDER}/' in line:
            for before, after in VERSION_CHANGES.items():
                if f'api-version={before}' in line:
                    modified = True

                    line = line.replace(f'api-version={before}', f'api-version={after}')
        elif RESOURCE_PROVIDER == 'Microsoft.Resources':
            # resource groups
            if re.match(r' {6}"RequestUri": "/subscriptions/[-a-z0-9]*/resource[Gg]roups/[-\w._()]+\?api-version=[-0-9]+",', line) \
                    or re.match(r' {6}"RequestUri": "/subscriptions/[-a-z0-9]*/resource[Gg]roups\?api-version=[-0-9]+",', line)\
                    or re.match(r' {6}"RequestUri": "/subscriptions/[-a-z0-9]*/resource[Gg]roups/[-\w._()]+/resources\?api-version=[-0-9]+",', line):
                for before, after in VERSION_CHANGES.items():
                    if f'api-version={before}' in line:
                        modified = True

                        line = line.replace(f'api-version={before}', f'api-version={after}')

        if '"RequestUri"' in line:
            m = re.search(' {6}"RequestUri": "(.+?)",\n', line)
            if m:
                uri = m.group(1)
        else:
            if uri and '"EncodedRequestUri"' in line:
                encoded_uri = str(base64.b64encode(uri.encode('utf-8')), 'utf-8')
                line = f'      "EncodedRequestUri": "{encoded_uri}",\n'
                modified = True
            uri = None

        out_lines.append(line)

    if modified:
        logging.info(f'update session record {filepath}')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(''.join(out_lines))


main()
