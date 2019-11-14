import re

RUNTIME_STACK = r'''
  "RUBY|2.3.8",
  "RUBY|2.4.5",
  "RUBY|2.5.5",
  "RUBY|2.6.2",
  "NODE|lts",
  "NODE|10-lts",
  "NODE|8-lts",
  "NODE|6-lts",
  "NODE|4.4",
  "NODE|4.5",
  "NODE|4.8",
  "NODE|6.2",
  "NODE|6.6",
  "NODE|6.9",
  "NODE|6.10",
  "NODE|6.11",
  "NODE|8.0",
  "NODE|8.1",
  "NODE|8.2",
  "NODE|8.8",
  "NODE|8.9",
  "NODE|8.11",
  "NODE|8.12",
  "NODE|9.4",
  "NODE|10.1",
  "NODE|10.10",
  "NODE|10.12",
  "NODE|10.14",
  "PHP|5.6",
  "PHP|7.0",
  "PHP|7.2",
  "PHP|7.3",
  "DOTNETCORE|1.0",
  "DOTNETCORE|1.1",
  "DOTNETCORE|2.0",
  "DOTNETCORE|2.1",
  "DOTNETCORE|2.2",
  "TOMCAT|8.5-jre8",
  "TOMCAT|9.0-jre8",
  "JAVA|8-jre8",
  "WILDFLY|14-jre8",
  "TOMCAT|8.5-java11",
  "TOMCAT|9.0-java11",
  "JAVA|11-java11",
  "PYTHON|3.7",
  "PYTHON|3.6",
  "PYTHON|2.7"
'''

TEMPLATE = r'''/** {docstring} */
public static final RuntimeStack {name} = new RuntimeStack("{stack}", "{version}");
'''

NAME_PATTERN = {
    'NODE': '{stack}JS_{version}',
    'DOTNETCORE': 'NETCORE_V{version}',
    '*': '{stack}_{version}'
}

NAME_PATTERN_DEFAULT = NAME_PATTERN['*']

DOCSTRING_PATTERN = {
    'WILDFLY': 'WildFly {version} image.',
    'TOMCAT': 'Tomcat {version} image with catalina root set to Azure wwwroot.',
    'NODE': 'Node.JS {version}.',
    'DOTNETCORE': '.NET Core v{version}.',
    '*': '{stack} {version}.'
}

DOCSTRING_PATTERN_DEFAULT = DOCSTRING_PATTERN['*']

DOCSTRING_POST_RE = [
    ('-lts', ' LTS'),
    ('JAVA 8-jre8', 'JAVA JRE 8'),
    ('JAVA 11-java11', 'JAVA JAVA 11'),
    ('WildFly 14-jre8', 'WildFly 14.0-jre8')
]


runtime_stacks = []
for line in RUNTIME_STACK.splitlines():
    if line:
        segments = line.split('|')
        runtime_stacks.append({
            'stack': segments[0].strip().strip('"'),
            'version': segments[1].strip().strip(',"')
        })

runtime_stacks.sort(key=lambda r: r['stack'] + '.'.join(map(lambda v: v.rjust(4), r['version'].replace('-', '.').split('.'))))

for runtime_stack in runtime_stacks:
    stack = runtime_stack['stack']
    version = runtime_stack['version']

    ver_segments = version.split('.')
    if len(ver_segments) > 2:
        version = '.'.join(ver_segments[0:2])

    name_pattern = NAME_PATTERN.get(stack, NAME_PATTERN_DEFAULT)
    docstring_pattern = DOCSTRING_PATTERN.get(stack, DOCSTRING_PATTERN_DEFAULT)

    version_in_name = version.replace('.', '_').replace('-', '_').upper()
    name = name_pattern.format(stack=stack, version=version_in_name)
    docstring = docstring_pattern.format(stack=stack, version=version)
    for post_re in DOCSTRING_POST_RE:
        docstring = re.sub(post_re[0], post_re[1], docstring)

    print(TEMPLATE.format(docstring=docstring, name=name, stack=stack, version=version))
