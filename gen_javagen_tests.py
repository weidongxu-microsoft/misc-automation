import os
import os.path as path
import subprocess


AUTOREST_JAVA_REPO = r"C:/github_fork/autorest.java"
TESTSERVER_REPO = r"C:/github/autorest.testserver"

INCLUDE_CLASS = ["bodydate", "bodydatetime", "bodydatetimerfc1123"]


def main():
    swagger_dir = path.join(TESTSERVER_REPO, "swagger")
    for file in os.listdir(swagger_dir):
        clazz = path.splitext(file)[0].replace("-", "").lower()
        if INCLUDE_CLASS and clazz in INCLUDE_CLASS:
            swagger_file = path.join(swagger_dir, file)
            args = [
                "autorest-beta",
                '--use:"{}"'.format(AUTOREST_JAVA_REPO),
                "--java",
                "--sync-methods=all",
                '--input-file:"{}"'.format(swagger_file),
                '--output-folder:"tests"',
                "--namespace:fixtures.{}".format(clazz),
            ]
            print("calling:\n")
            print(" ".join(args))
            subprocess.Popen(" ".join(args), cwd=AUTOREST_JAVA_REPO, shell=True).communicate()


main()
