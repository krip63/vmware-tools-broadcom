import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import shutil
import logging

# 日志配置
logging.basicConfig(
    filename='sync.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BASE_URL = "https://packages-prod.broadcom.com/tools/"
DOWNLOAD_DIR = datetime.now().strftime("%Y-%m-%d")
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def get_file_links(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = []

        for link in soup.find_all("a"):
            href = link.get("href")
            if href and not href.startswith("?") and not href.startswith("/"):
                full_url = url + href
                if href.endswith("/"):
                    # 是目录则递归
                    links += get_file_links(full_url)
                else:
                    links.append(full_url)
        return links
    except Exception as e:
        logging.error(f"获取链接失败: {url} - {e}")
        return []

def download_file(url, base_dir):
    try:
        local_path = url.replace(BASE_URL, "")
        local_file_path = os.path.join(base_dir, local_path)

        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        if os.path.exists(local_file_path):
            logging.info(f"已存在，跳过: {local_file_path}")
            return

        r = requests.get(url, stream=True, headers=HEADERS)
        r.raise_for_status()

        with open(local_file_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)

        logging.info(f"下载完成: {local_file_path}")
    except Exception as e:
        logging.error(f"下载失败: {url} - {e}")

def main():
    logging.info("开始检查更新...")
    links = get_file_links(BASE_URL)

    if not links:
        logging.info("未发现任何文件，终止。")
        return

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    for file_url in links:
        download_file(file_url, DOWNLOAD_DIR)

    logging.info("同步完成。")

if __name__ == "__main__":
    main()
