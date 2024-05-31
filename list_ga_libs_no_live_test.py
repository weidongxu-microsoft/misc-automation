import os
import re

SDK_REPO = "c:/github/azure-sdk-for-java"

modules = {}
for service in os.listdir(os.path.join(SDK_REPO, "sdk")):
    path = os.path.join(SDK_REPO, "sdk", service)
    if os.path.isdir(path) and service not in ["resourcemanager", "resourcemanagerhybrid"]:
        for module in os.listdir(path):
            module_path = os.path.join(path, module)
            if os.path.isdir(module_path) and "-resourcemanager-" in module:
                with open(os.path.join(module_path, "CHANGELOG.md"), encoding="utf-8") as f:
                    changelog = f.read()
                    match = re.search(r"## 1.0.0 \((.*)\)", changelog)
                    if match and not os.path.exists(os.path.join(path, "tests.mgmt.yml")):
                        # GA sdk, with no 'tests.mgmt.yml'
                        date = match.group(1)
                        modules[module] = date
modules = sorted(modules, key=modules.get)
for item in modules:
    print("- [ ] " + item[len("azure-resourcemanager-") :])
