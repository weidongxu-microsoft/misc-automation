import os
import logging


SDK_REPO = 'c:/github/azure-sdk-for-java/sdk/resourcemanager'
KEYWORD = '.mapPage('


def refactor_java(file_path: str):
    lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    found = False
    locations = []
    for location, line in enumerate(lines):
        if KEYWORD in line:
            found = True
            locations.append(location)

    if found:
        logging.info(f'refactor java at {file_path}')

        for location in reversed(locations):
            line = lines[location]
            if line.strip() == KEYWORD:
                lines.pop(location)
            elif line.strip().startswith(KEYWORD):
                lines[location] = line.replace(KEYWORD, '')
                lines[location-1] = lines[location-1].rstrip() + ',\n'
            else:
                lines[location] = line.replace(KEYWORD, ', ')

            for rel in range(0, -10, -1):
                line = lines[location+rel]
                if line.strip().startswith('return '):
                    lines[location+rel] = line.replace('return ', 'return PagedConverter.mapPage(')
                    break

        importInsertLocation = -1
        for reversed_location, line in enumerate(reversed(lines)):
            if line.strip() == 'import com.azure.resourcemanager.resources.fluentcore.utils.PagedConverter;':
                importInsertLocation = -1
                break
            if line.startswith('import ') and importInsertLocation == -1:
                importInsertLocation = len(lines) - reversed_location

        if importInsertLocation >= 0:
            lines.insert(importInsertLocation,
                         'import com.azure.resourcemanager.resources.fluentcore.utils.PagedConverter;\n')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(''.join(lines))


def main():
    for root, dirs, files in os.walk(SDK_REPO):
        for name in files:
            file_path = os.path.join(root, name)
            if os.path.splitext(file_path)[1] == '.java' and 'PagedConverter' not in file_path:
                refactor_java(file_path)


main()