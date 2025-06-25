import os
import requests
from bs4 import BeautifulSoup
import subprocess
import datetime
import json

BASE_URL = "https://packages-prod.broadcom.com/tools/"
STATE_FILE = "last_state.json"


def get_file_list(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    files = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and not href.endswith("/"):
            files.append(href)
    return files


def load_last_state():
    if not os.path.exists(STATE_FILE):
        return []
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_last_state(file_list):
    with open(STATE_FILE, "w") as f:
        json.dump(file_list, f)


def download_file(file_name, folder):
    url = BASE_URL + file_name
    local_path = os.path.join(folder, file_name)
    print(f"Downloading {url} -> {local_path}")

    headers = {}
    if os.path.exists(local_path):
        local_size = os.path.getsize(local_path)
        headers["Range"] = f"bytes={local_size}-"
    else:
        local_size = 0

    with requests.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        mode = "ab" if local_size > 0 else "wb"
        with open(local_path, mode) as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def git_commit_push(folder):
    print("Git add, commit and push ...")
    subprocess.run(["git", "add", folder], check=True)
    commit_msg = f"Update vmware tools backup {datetime.datetime.now().strftime('%Y-%m-%d')}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(["git", "push"], check=True)
    print("Done.")


def main():
    print("Start checking updates...")
    last_files = load_last_state()
    current_files = get_file_list(BASE_URL)

    if set(current_files) == set(last_files):
        print("No update detected.")
        return

    print("Update detected, downloading all files ...")
    date_folder = datetime.datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(date_folder):
        os.makedirs(date_folder)

    for file_name in current_files:
        download_file(file_name, date_folder)

    git_commit_push(date_folder)
    save_last_state(current_files)


if __name__ == "__main__":
    main()
