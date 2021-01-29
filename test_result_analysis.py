from xml.etree import cElementTree as ElementTree
from collections import defaultdict


REPORT_FILE = r'C:\github\azure-sdk-for-java\sdk\resourcemanager\Test Results - All_in_azure-resourcemanager-compute.xml'


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


tree = ElementTree.parse(REPORT_FILE)
root = tree.getroot()
report = etree_to_dict(root)

error_suite_names = []
pass_suite_names = []

for suite in report['testrun']['suite']:
    if suite['@status'] == 'error':
        error_suite_names.append(suite['@name'])
    else:
        pass_suite_names.append(suite['@name'])

print('<includes>')
for suite_name in error_suite_names:
    print(f'  <include>**/{suite_name}.java</include>')
print('</includes>')

print('<excludes>')
for suite_name in pass_suite_names:
    print(f'  <exclude>**/{suite_name}.java</exclude>')
print('</excludes>')
