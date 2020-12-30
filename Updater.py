import shutil
from ConfigManager import ConfigManager
import requests
import json
import argparse
import tarfile
import os
import sys

user = "wrp1002"
repo = "motion-detection-server"
CONFIG_FILE_NAME = "config.json"

githubApiUrl = "https://api.github.com/repos/" + user + "/" + repo + "/releases/latest"
extension = ".tar.gz"
scriptDir = os.path.realpath(os.path.dirname(sys.argv[0]))
print("Current directory:", scriptDir)

def Update(url, version, tarFileName):
    updateDir = os.path.join(scriptDir, "Update", "")
    serverDir = os.path.join(updateDir, "Motion Detection Server")

    print("Making update directory...")

    try:
        if os.path.exists(updateDir):
            shutil.rmtree(updateDir)
        os.mkdir(updateDir)
        os.chdir(updateDir)
    except Exception as e:
        print()
        print("Couln't delete Update folder. Is there a program that's using it?")
        print("Error:", e)
        print()
        return

    print("Downloading update...")
    content = requests.get(url).content
    with open(tarFileName, 'wb') as file:
        file.write(content)

    print("Extracting update...")
    tar = tarfile.open(tarFileName, "r:gz")
    extractedDir = os.path.join(updateDir, tar.getnames()[0])
    tar.extractall()
    tar.close()

    print("Copying files to new server...")
    os.rename(extractedDir, serverDir)
    shutil.copy(os.path.join(scriptDir, CONFIG_FILE_NAME), os.path.join(updateDir, serverDir, CONFIG_FILE_NAME))

    #print("Updating config...")
    #config = ConfigManager(serverDir, CONFIG_FILE_NAME)
    #config.SetValue("updated", True)

    print("Moving new server files...")
    os.chdir(scriptDir)
    files = os.listdir(updateDir)
    for file in files:
        shutil.copy(file, scriptDir)


    print("Done!")


def ShowVersions():
    info = json.loads(requests.get(githubApiUrl).text)
    config = ConfigManager(scriptDir, CONFIG_FILE_NAME).LoadConfig()

    latestVersion = info["tag_name"]
    version = config["version"]

    print("Current Version:", version)
    print("Latest version:", latestVersion)


def main():
    parser = argparse.ArgumentParser(description="Update script for Motion Detection Server")
    parser.add_argument("--version", help="Display the local version of the server and the latest one", action="store_true")
    args = parser.parse_args()

    if args.version:
        ShowVersions()
        return

    info = json.loads(requests.get(githubApiUrl).text)
    try:
        url = info["tarball_url"]
        version = info["tag_name"]
        repo_name = url.split("/")[-3]
        file_name = repo_name + "-" + version + extension
    except KeyError:
        print()
        print("Error getting release info from github")
        print("Response:", info)
        print()
        return

    print("Release URL:", url)
    print("Latest version:", version)
    print(file_name)

    Update(url, version, file_name)



if __name__ == "__main__":
    main()