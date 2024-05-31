import json
import os
import re

EXAMPLE_REPO = "c:/github/azure-rest-api-specs-examples/specification/"


def update_markdown(filepath: str):
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    code_end = None
    for index, line in enumerate(lines):
        if line == "```\n":
            code_end = index
            break

    if code_end:
        ext = None
        if "examples-java" in filepath:
            ext = ".java"
        if "examples-js" in filepath:
            ext = ".js"
        if "examples-go" in filepath:
            ext = ".go"

        if ext:
            code_lines = lines[1:code_end]

            ref_lines = lines[code_end + 1 :]
            match = re.search(r"\[SDK documentation]\((.*?\.md)\)", "".join(ref_lines))
            if match:
                with open(filepath.replace(".md", ext), "w", encoding="utf-8") as f:
                    f.write("".join(code_lines))

                ref_json = {"sdkUrl": match.group(1)}
                with open(filepath.replace(".md", ".json"), "w", encoding="utf-8") as f:
                    json.dump(ref_json, f)

                os.remove(filepath)
                return

    print("failed to process " + filepath)


def main():
    for subdir, dirs, files in os.walk(EXAMPLE_REPO):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(".md"):
                update_markdown(filepath)


main()
