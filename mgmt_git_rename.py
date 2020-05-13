import os
import fnmatch
import re
import subprocess
import os.path as path

SERVICE = 'containerregistry'

for root, dir, files in os.walk("..\\" + SERVICE):
    for item in fnmatch.filter(files, "*.java"):
        file = root + '\\' + item
        filename = item[0:-5]
        clazz = ''
        with open(file, 'r', encoding='utf8') as f:
            lines = f.readlines()
            for line in lines:
                m = re.search('class (\\S+)', line)
                if m:
                    clazz = m.group(1)
            if clazz and len(filename) == len(clazz) and not filename == clazz:
                #print(filename + " - " + clazz)
                newfile = file.replace(filename, clazz)
                #print(newfile)
                #subprocess.Popen(['git', 'mv', '-f', file, newfile], cwd='.').communicate()
                print('git mv -f ' + file + ' ' + newfile)
