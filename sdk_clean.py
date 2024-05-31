import os
import shutil


SDK_REPO = "c:/github/azure-sdk-for-java/sdk"


for dir in os.listdir(SDK_REPO):
    sdk_path = os.path.join(SDK_REPO, dir)
    if os.path.isdir(sdk_path):
        dirs = os.listdir(sdk_path)
        for package_dir in dirs:
            filepath = os.path.join(sdk_path, package_dir)
            if os.path.isdir(filepath) and package_dir.startswith("mgmt-"):
                shutil.rmtree(filepath)
            elif not os.path.isdir(filepath) and (package_dir == "ci.mgmt.yml" or package_dir == "pom.mgmt.xml"):
                os.remove(filepath)

        dirs = os.listdir(sdk_path)
        if len(dirs) == 0:
            os.removedirs(sdk_path)
