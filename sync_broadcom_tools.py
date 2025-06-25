import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = 'https://packages-prod.broadcom.com/tools/'
SAVE_DIR = os.path.join('VMware Tools', 'tools')

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download_file(url, save_path):
    try:
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {url} -> {save_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def crawl(url, local_path):
    ensure_dir(local_path)
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"Failed to access {url}: {e}")
        return

    soup = BeautifulSoup(r.text, 'html.parser')

    for link in soup.find_all('a'):
        href = link.get('href')
        if not href or href.startswith('?') or href == '../':
            continue

        full_url = urljoin(url, href)
        # 判断链接是否是目录（以 / 结尾）还是文件
        if href.endswith('/'):
            # 目录，递归调用
            crawl(full_url, os.path.join(local_path, href.strip('/')))
        else:
            # 文件，下载覆盖
            file_path = os.path.join(local_path, href)
            download_file(full_url, file_path)

if __name__ == '__main__':
    print(f"Starting sync from {BASE_URL} to local folder '{SAVE_DIR}' ...")
    crawl(BASE_URL, SAVE_DIR)
    print("Sync completed.")
