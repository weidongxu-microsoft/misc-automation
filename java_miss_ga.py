import os
import glob
import logging

SDK_REPO = "c:/github/azure-sdk-for-java"
SPEC_REPO = "c:/github/azure-rest-api-specs"

version_file = os.path.join(SDK_REPO, "eng/versioning/version_client.txt")

sdk_in_preview = []
need_manual_check = []
need_release = []

with open(version_file, "r") as fin:
    lines = fin.read().splitlines()
    version_index = -1
    for i, version_line in enumerate(lines):
        version_line = version_line.strip()
        if not version_line or version_line.startswith("#"):
            continue
        versions = version_line.split(";")
        module = versions[0].split(":")[1]
        if "azure-resourcemanager-" in module and not (
            module.endswith("-perf") or module.endswith("-samples") or module.endswith("-test")
        ):
            if len(versions) != 3:
                logging.error('[VERSION][Fallback] Unexpected version format "{0}"'.format(version_line))
            else:
                if "-beta." in versions[1]:
                    sdk_in_preview.append(module)

for module in sdk_in_preview:
    service = module.split("-")[2]
    specs_path = os.path.join(SPEC_REPO, "specification", service, "resource-manager")
    if os.path.exists(specs_path):
        result = glob.glob(os.path.join(specs_path, "*", "stable"))
        if len(result) > 0:
            need_release.append(module)
    else:
        need_manual_check.append(module)

for m in need_release:
    print(m)
print(len(need_release))

# print(need_manual_check)
# print(len(need_manual_check))
