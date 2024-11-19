import os
import shutil

import git

gitRepo = "https://github.com/v2fly/domain-list-community.git"

processFlag = {}
gitDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "domain-list-community-tmp")
dateDir = os.path.join(gitDir, "data")
surgeRulesDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "surge-rules")


def main():
    shutil.rmtree(gitDir, ignore_errors=True)

    if not cloneGitRepo(gitDir, gitRepo):
        print("Error cloning Git repository")
        return

    os.makedirs(surgeRulesDir, exist_ok=True)

    try:
        files = os.listdir(dateDir)
    except OSError as e:
        print(f"Error reading directory: {e}")
        return

    for file in files:
        process(os.path.join(dateDir, file), os.path.join(surgeRulesDir, file + ".list"))

    shutil.rmtree(gitDir, ignore_errors=True)


def cloneGitRepo(dir, repo):
    try:
        git.Repo.clone_from(repo, dir)
        return True
    except git.GitCommandError as e:
        print(f"Error cloning Git repository: {e}")
        return False


def process(inputFilePath, outputFilePath):
    if processFlag.get(inputFilePath):
        return

    try:
        with open(inputFilePath, 'r', encoding='utf-8') as inputFile, open(outputFilePath, 'w',
                                                                            encoding='utf-8') as outputFile:
            for line in inputFile:
                line = removeAtAndAfter(line)
                trimLine = line.strip()
                if trimLine:
                    if trimLine.startswith("#"):
                        pass
                    elif trimLine.startswith("full:"):
                        line = line.replace("full:", "DOMAIN, ")
                    elif trimLine.startswith("regexp:"):
                        line = line.replace("regexp:", "URL-REGEX, ")
                    elif trimLine.startswith("include:"):
                        subInputFilePath, subOutputFilePath = genInputAndOutputFileName(
                            trimLine[len("include:"):].split()[0])
                        process(subInputFilePath, subOutputFilePath)
                        with open(subOutputFilePath, 'r', encoding='utf-8') as subOutputFile:
                            line = subOutputFile.read()
                    else:
                        line = "DOMAIN-SUFFIX, " + line
                outputFile.write(line + "\n")
            processFlag[inputFilePath] = True
    except OSError as e:
        print(f"Error processing file: {e}")


def removeAtAndAfter(input):
    input = input.strip()
    idx = input.find(" @")
    if idx != -1:
        return input[:idx]
    return input


def genInputAndOutputFileName(key):
    return os.path.join(dateDir, key), os.path.join(surgeRulesDir, key + ".list")


if __name__ == "__main__":
    main()