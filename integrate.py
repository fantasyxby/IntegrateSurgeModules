import datetime
import os
import re

import requests


def getSection(resource, section):
    pattern = rf"\[{section}\](.*?)(?:\[(General|Rule|URL Rewrite|Map Local|Script|MITM)\]|$)"
    match = re.search(pattern, resource, re.DOTALL)
    if match:
        return "\n".join(
            line for line in match.group(1).strip().splitlines() if line.strip() and not line.strip().startswith("#"))
    return ""


def download(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading content from {url}: {e}")
        return None


def save(content, outputPath):
    try:
        with open(outputPath, 'w', encoding='utf-8') as f:
            f.write(content)
    except IOError as e:
        print(f"Error saving content to {outputPath}: {e}")


def integrate(resourceList):
    time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    content = f"""#!name=模块整合
#!desc=由GithubAction自动更新
#!author=fantasyxby[https://github.com/fantasyxby]
#!date={timestamp}

[General]

"""
    for resource in resourceList:
        lines = getSection(resource, "General")
        if lines:
            content += lines
            if not content.endswith("\n"):
                content += "\n"
    content += f"""

[Rule]

"""
    for resource in resourceList:
        lines = getSection(resource, "Rule")
        if lines:
            content += lines
            if not content.endswith("\n"):
                content += "\n"
    content += f"""

[URL Rewrite]

"""
    for resource in resourceList:
        lines = getSection(resource, "URL Rewrite")
        if lines:
            content += lines
            if not content.endswith("\n"):
                content += "\n"
    content += f"""  

[Map Local]

"""
    for resource in resourceList:
        lines = getSection(resource, "Map Local")
        if lines:
            content += lines
            if not content.endswith("\n"):
                content += "\n"
    content += f"""

[Script]

"""
    for resource in resourceList:
        lines = getSection(resource, "Script")
        if lines:
            content += lines
            if not content.endswith("\n"):
                content += "\n"

    list = []
    for resource in resourceList:
        lines = getSection(resource, "MITM")
        lines = re.search(r"%APPEND%\s*(.*)", lines).group(1)
        list.append(lines)
    mitmContent = ', '.join(list)

    content += f"""

[MITM]

hostname = %APPEND% {mitmContent}
"""
    return content


def process(urlList):
    resourceList = []

    for url in urlList:
        resource = download(url)
        if resource:
            resourceList.append(resource)
        else:
            print(f"Failed to download or process the content from {url}.")

    # sgmoduleDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sgmodule')
    # for filename in os.listdir(sgmoduleDir):
    #     if filename.endswith('.sgmodule'):
    #         with open(os.path.join(sgmoduleDir, filename), 'r', encoding='utf-8') as f:
    #             resourceList.append(f.read())

    content = integrate(resourceList)

    outputPath = '模块整合.sgmodule'
    save(content, outputPath)


if __name__ == "__main__":
    listPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sgmodule.list")

    try:
        with open(listPath, 'r', encoding='utf-8') as file:
            urlList = [line.strip() for line in file if line.strip() and not line.startswith("#")]
    except IOError as e:
        print(f"Error reading the input file: {e}")
        exit(1)

    process(urlList)
