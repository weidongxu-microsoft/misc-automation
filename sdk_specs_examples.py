import dataclasses
import os
import json
import re
import logging
from typing import List, Dict


SPECS_REPO = "c:/github/azure-rest-api-specs"
SDK_REPO = "c:/github/azure-sdk-for-java"
SDK_EXAMPLES_REPO = "c:/github_lab/azure-rest-api-specs-examples"

SPECS_SERVICE = "datafactory"
SDK_EXAMPLES = (
    "sdk/datafactory/azure-resourcemanager-datafactory/src/samples/java/com/azure/resourcemanager/datafactory/examples/"
)

# SPECS_SERVICE = 'compute'
# SDK_EXAMPLES = 'sdk/resourcemanager/azure-resourcemanager/src/samples/java/com/azure/resourcemanager/compute/examples/'


@dataclasses.dataclass(eq=True, frozen=True)
class ExampleReference:
    operation_id: str
    api_version: str
    name: str


def main():
    logging.basicConfig(level=logging.INFO)
    process_sdk_examples()


def process_sdk_examples():
    example_references = {}
    service_path = os.path.join(SPECS_REPO, "specification", SPECS_SERVICE, "resource-manager")
    for root, dirs, files in os.walk(service_path):
        for name in files:
            filepath = os.path.join(root, name)
            if os.path.splitext(filepath)[1] == ".json" and not os.path.split(filepath)[0].endswith("examples"):
                with open(filepath, encoding="utf-8") as f:
                    try:
                        swagger = json.load(f)
                        example_references.update(find_example_references(filepath, swagger))
                    except Exception as e:
                        logging.error(f"error {e}")
    # logging.info(example_references)
    rename_java_examples(example_references)


def find_example_references(filepath: str, swagger: Dict) -> Dict[ExampleReference, str]:
    example_references = {}
    if "info" in swagger and "version" in swagger["info"]:
        api_version = swagger["info"]["version"]
        if "paths" in swagger:
            for path in swagger["paths"].values():
                for operation in path.values():
                    if "operationId" in operation and "x-ms-examples" in operation:
                        operation_id = operation["operationId"].lower()
                        for example_name, example_ref in operation["x-ms-examples"].items():
                            if "$ref" in example_ref:
                                relative_path = example_ref["$ref"]
                                full_path = os.path.join(os.path.split(filepath)[0], relative_path)
                                example_ref_value = os.path.normpath(os.path.relpath(full_path, SPECS_REPO))
                                example_ref_key = ExampleReference(operation_id, api_version, example_name)
                                example_references[example_ref_key] = example_ref_value
    return example_references


def rename_java_examples(example_references: Dict[ExampleReference, str]):
    sdk_examples_path = os.path.join(SDK_REPO, SDK_EXAMPLES)
    for root, dirs, files in os.walk(sdk_examples_path):
        for name in files:
            filepath = os.path.join(root, name)
            if os.path.splitext(filepath)[1] == ".java":
                with open(filepath, encoding="utf-8") as f:
                    lines = f.readlines()
                example_reference = get_java_example_reference(lines)
                example_filepath = example_references[example_reference]
                example_dir, example_filename = os.path.split(example_filepath)

                old_class_name = name.split(".")[0]
                new_class_name = example_filename.split(".")[0]
                md_filename = new_class_name + ".md"
                new_class_name = re.sub(r"[_\-]+", "", new_class_name)
                md_str = get_md_from_java(lines, old_class_name, new_class_name)
                if new_class_name[0].islower():
                    new_class_name = new_class_name[0].upper() + new_class_name[1:]

                md_dir = example_dir + "-java"
                md_dir_path = os.path.join(SDK_EXAMPLES_REPO, md_dir)
                os.makedirs(md_dir_path, exist_ok=True)

                md_file_path = os.path.join(md_dir_path, md_filename)
                with open(md_file_path, "w", encoding="utf-8") as f:
                    f.write(md_str)


def get_md_from_java(lines: List[str], old_class_name: str, new_class_name: str):
    md_lines = []
    md_lines.append("```java")
    skip_head = True
    for line in lines:
        if not skip_head:
            line = line.replace(old_class_name, new_class_name)
            md_lines.append(line)

        if line.startswith("package"):
            skip_head = False
    md_lines.append("```")
    return "".join(md_lines)


def get_java_example_reference(lines: List[str]) -> ExampleReference:
    operation_id_key = "* operationId: "
    api_version_key = "* api-version: "
    example_name_key = "* x-ms-examples: "

    operation_id = None
    api_version = None
    example_name = None
    for line in lines:
        if line.strip().startswith(operation_id_key):
            operation_id = line.strip()[len(operation_id_key) :].lower()
        elif line.strip().startswith(api_version_key):
            api_version = line.strip()[len(api_version_key) :]
        elif line.strip().startswith(example_name_key):
            example_name = line.strip()[len(example_name_key) :]
    # TODO error if None
    return ExampleReference(operation_id, api_version, example_name)


main()
