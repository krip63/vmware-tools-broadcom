import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pathlib import Path
import time

BASE_URL = "https://packages-prod.broadcom.com/tools/"
LOCAL_BASE = "VMware Tools/tools"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    )
}

def download_file(url, dest_path):
    try:
        start = time.time()
        with requests.get(url, stream=True, headers=HEADERS, timeout=10) as r:
            r.raise_for_status()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, 'wb') as f:
                total = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total += len(chunk)
        elapsed = time.time() - start
        mb = total / 1024 / 1024
        speed = mb / elapsed if elapsed > 0 else 0
        print(f"Downloaded: {url.replace(BASE_URL, '/tools/')} | {mb:.2f}MB in {elapsed:.2f}s ({speed:.2f} Mb/s)")
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")

def sync_directory(url, local_dir):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        for link_tag in soup.find_all('a'):
            href = link_tag.get('href')
            if not href or href.startswith("?") or href.startswith("#"):
                continue
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)
            if not parsed.path.startswith("/tools/"):
                continue
            relative_path = parsed.path.lstrip("/tools/")
            local_path = Path(local_dir) / relative_path
            if href.endswith("/"):
                sync_directory(full_url, local_dir)
            else:
                if not local_path.exists() or local_path.stat().st_size == 0:
                    download_file(full_url, local_path)
    except Exception as e:
        print(f"❌ Failed to access {url}: {e}")

def main():
    print(f"Starting sync from {BASE_URL} to local folder '{LOCAL_BASE}' ...")
    sync_directory(BASE_URL, LOCAL_BASE)

if __name__ == "__main__":
    main()
