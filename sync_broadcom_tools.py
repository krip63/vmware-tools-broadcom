import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

BASE_URL = "https://packages-prod.broadcom.com/tools/"
LOCAL_BASE_FOLDER = os.path.join("VMware Tools", "tools")

def format_size(size_bytes):
    """格式化字节数为合适单位字符串"""
    if size_bytes == 0:
        return "0B"
    units = ["B", "KB", "MB", "GB"]
    idx = 0
    size = float(size_bytes)
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024
        idx += 1
    return f"{size:.2f} {units[idx]}"

def download_file(url, local_path):
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        start_time = time.time()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(1024 * 32):
                if chunk:
                    f.write(chunk)
        end_time = time.time()

        duration = end_time - start_time
        duration = max(duration, 0.001)  # 防止除以0

        size_mb = total_size / (1024 * 1024)
        speed_mbps = (total_size * 8) / (duration * 1024 * 1024)  # 转换为 Mb/s

        print(f"Downloaded: {urlparse(url).path} | {format_size(total_size)} in {duration:.2f}s ({speed_mbps:.2f} Mb/s)")

    except Exception as e:
        print(f"Error downloading {url}: {e}")

def sync_folder(url, local_folder):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # 解析网页，找所有的a标签，判断是文件还是目录
        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if not href or href in ('../', './'):
                continue
            full_url = urljoin(url, href)
            path = urlparse(full_url).path
            # 判断是目录还是文件：
            # 如果href以“/”结尾，认为是目录，否则是文件
            if href.endswith('/'):
                # 目录，递归同步
                subfolder = os.path.join(local_folder, href.strip('/'))
                sync_folder(full_url, subfolder)
            else:
                # 文件，增量下载（覆盖）
                local_file_path = os.path.join(local_folder, href)
                download_file(full_url, local_file_path)
    except Exception as e:
        print(f"Error syncing folder {url}: {e}")

def main():
    print(f"Starting sync from {BASE_URL} to local folder '{LOCAL_BASE_FOLDER}' ...")
    sync_folder(BASE_URL, LOCAL_BASE_FOLDER)
    print("Sync complete.")

if __name__ == "__main__":
    main()
