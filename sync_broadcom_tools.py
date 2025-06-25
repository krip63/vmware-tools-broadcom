import os
import requests
import time
from urllib.parse import urljoin, urlparse

BASE_URL = "https://packages-prod.broadcom.com/tools/"
LOCAL_ROOT = os.path.join("VMware Tools", "tools")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
}
LOG_FILE = "sync_log.txt"

def save_log(message: str):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{message}\n")

def download_file(url, local_path):
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with requests.get(url, headers=HEADERS, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            if os.path.exists(local_path) and os.path.getsize(local_path) == total_size and total_size > 0:
                return False  # Skip unchanged

            start = time.time()
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            end = time.time()

            elapsed = end - start
            mb = total_size / (1024 * 1024)
            speed = mb / elapsed if elapsed > 0 else 0
            msg = f"Downloaded: {urlparse(url).path} | {mb:.2f} MB in {elapsed:.2f}s ({speed:.2f} Mb/s)"
            print(msg)
            save_log(msg)
            return True
    except Exception as e:
        msg = f"❌ Error downloading {url}: {e}"
        print(msg)
        save_log(msg)
        return False

def crawl_directory(url, local_dir):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html = response.text

        for line in html.splitlines():
            if 'href="' in line:
                start = line.find('href="') + 6
                end = line.find('"', start)
                href = line[start:end]
                if not href or href.startswith("?") or href.startswith("#"):
                    continue

                full_url = urljoin(url, href)
                if href.endswith("/"):
                    crawl_directory(full_url, os.path.join(local_dir, href))
                else:
                    local_path = os.path.join(local_dir, href)
                    download_file(full_url, local_path)
    except Exception as e:
        msg = f"❌ Error accessing {url}: {e}"
        print(msg)
        save_log(msg)

if __name__ == "__main__":
    print(f"Starting sync from {BASE_URL} to local folder '{LOCAL_ROOT}' ...")
    save_log(f"\n🕒 Sync started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    crawl_directory(BASE_URL, LOCAL_ROOT)
    save_log(f"✅ Sync completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("✔️ Sync completed.")
