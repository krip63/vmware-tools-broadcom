import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    filename='sync.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

BASE_URL = 'https://packages-prod.broadcom.com/tools/'
LOCAL_ROOT = '.'  # 当前目录根目录存放
LOG_FILE = 'sync.log'

def fetch_index(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logging.error(f'Error fetching index page: {url} - {e}')
        return None

def parse_file_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        # 过滤目录链接和上级链接
        if href.endswith('/') or href in ('../',):
            continue
        links.append(href)
    return links

def download_file(url, save_path):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info(f'Downloaded {url} -> {save_path}')
        return True
    except Exception as e:
        logging.error(f'Error downloading file {url}: {e}')
        return False

def main():
    logging.info('--- Start sync_broadcom_tools.py ---')

    html = fetch_index(BASE_URL)
    if html is None:
        logging.error('Failed to fetch base index page. Abort.')
        return

    files = parse_file_links(html)
    if not files:
        logging.info('No files found to download. Abort.')
        return

    today = datetime.utcnow().strftime('%Y-%m-%d')
    dest_folder = os.path.join(LOCAL_ROOT, today)

    # 判断今天目录是否存在且非空，避免重复下载
    if os.path.exists(dest_folder) and os.listdir(dest_folder):
        logging.info(f'Today\'s folder "{dest_folder}" already exists and is not empty. Skipping download.')
        return

    # 下载所有文件
    success_count = 0
    for filename in files:
        file_url = BASE_URL + filename
        save_path = os.path.join(dest_folder, filename)
        if download_file(file_url, save_path):
            success_count += 1

    logging.info(f'Download complete. {success_count}/{len(files)} files downloaded.')

    logging.info('--- End sync_broadcom_tools.py ---')

if __name__ == '__main__':
    main()
