import os
import logging
import json
import re


DOC_PACKAGE_FILENAME = "C:/github/azure-docs-sdk-java/package.json"


def main():
    logging.basicConfig(level=logging.INFO)

    with open(DOC_PACKAGE_FILENAME, "r", encoding="utf-8") as f:
        lines = f.readlines()

    exclude_package_defined = False
    implementation_package = None
    out_lines = []
    for line in lines:
        line_strip = line.strip()
        if line_strip == "{":
            exclude_package_defined = False
            implementation_package = None
        elif line_strip == "}," or line_strip == "}":
            if not exclude_package_defined and implementation_package:
                previous_line_no = len(out_lines) - 1
                out_lines[previous_line_no] = out_lines[previous_line_no].rstrip() + ",\n"
                out_lines.append(f'                "excludepackages": "{implementation_package}"\n')
        elif line_strip.startswith('"excludepackages": '):
            exclude_package_defined = True
        elif line_strip.startswith('"packageArtifactId": '):
            artifact_id = re.match('"packageArtifactId": "(.*)",?', line_strip).group(1)
            if artifact_id.startswith("azure-resourcemanager-"):
                package_suffix = artifact_id.removeprefix("azure-resourcemanager-")
                implementation_package = f"com.azure.resourcemanager.{package_suffix}.implementation"
        out_lines.append(line)

    with open(DOC_PACKAGE_FILENAME, "w", encoding="utf-8") as f:
        f.write("".join(out_lines))


main()
