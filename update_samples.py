import logging
import json
import re
import os.path as path

SDK_REPO = "c:/github/azure-sdk-for-java/sdk/management"


def main():
    logging.basicConfig(level=logging.INFO)

    with open(path.join(SDK_REPO, "samples/samples.json")) as f:
        samples_json = json.load(f)

    repo_to_file = dict()
    for item in samples_json["javaSamples"]:
        file_path = item["filePath"]
        github_path = item["githubPath"]
        repo_to_file[github_path] = file_path

    print(repo_to_file)

    sample_md_filename = path.join(SDK_REPO, "docs/SAMPLE.md")
    lines = read_lines(sample_md_filename)
    newlines = []
    for line in lines:
        if "<a href=" in line:
            match = re.search('<a href="https://github.com/(.+?)">', line)
            if match:
                url_before = "https://github.com/" + match.group(1)
                github_repo = match.group(1).replace("azure-samples", "Azure-Samples")
                if github_repo in repo_to_file:
                    file_path = (
                        repo_to_file[github_repo].replace("azure-samples/", "samples/").replace("/microsoft/", "/")
                    )

                    if not path.exists(path.join(SDK_REPO, file_path)):
                        logging.error("file not found: " + file_path)

                    url_after = "https://github.com/Azure/azure-sdk-for-java/blob/master/sdk/management/" + file_path

                    line = line.replace(url_before, url_after)
                else:
                    logging.error("repo not found: " + github_repo)
        newlines.append(line)
    write_lines(sample_md_filename, newlines)


def read_lines(filename):
    with open(filename, mode="r", encoding="utf-8") as f:
        return f.readlines()


def write_lines(filename, lines):
    with open(filename, mode="w") as f:
        f.writelines(lines)


main()
