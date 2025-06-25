import os
import requests
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import hashlib
import logging
import sys
import datetime

# Configuration
BASE_URL = "https://packages-prod.broadcom.com/tools/"
LOCAL_ROOT = os.path.join("VMware Tools", "tools")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5"
}
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
LOG_FILE = "sync_log.txt"

# 设置日志系统 - 详细记录到文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

def log(message, level=logging.INFO):
    """统一日志记录函数"""
    logger.log(level, message)
    # 确保立即刷新到文件
    logging.getLogger().handlers[0].flush()

def fetch_url(url):
    """获取URL内容，支持重试"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                log(f"重试 {attempt+1}/{MAX_RETRIES} - {url}", logging.WARNING)
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                log(f"❌ 无法获取 {url}: {e}", logging.ERROR)
                return None

def calculate_file_hash(file_path):
    """计算文件的SHA-256哈希值"""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        log(f"❌ 计算哈希值时出错 {file_path}: {e}", logging.ERROR)
        return None

def download_file(url, local_path):
    """下载文件（仅当需要更新时）"""
    # 创建目录结构
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    # 检查是否需要下载
    file_changed = False
    skip_reason = "未检查"
    
    if os.path.exists(local_path):
        try:
            # 获取本地文件信息
            local_size = os.path.getsize(local_path)
            local_mtime = os.path.getmtime(local_path)
            local_hash = calculate_file_hash(local_path)
            
            # 获取远程文件信息
            response = requests.head(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            
            remote_size = int(response.headers.get("Content-Length", 0))
            last_modified = response.headers.get("Last-Modified")
            etag = response.headers.get("ETag", "").strip('"')
            
            # 记录文件比较信息
            log(f"🔍 检查文件: {os.path.basename(local_path)}")
            log(f"  本地大小: {local_size} | 远程大小: {remote_size}")
            
            if local_size != remote_size:
                file_changed = True
                log(f"  文件大小变化: {local_size} → {remote_size}")
            elif etag and local_hash and etag != local_hash:
                file_changed = True
                log(f"  哈希值不匹配: 本地={local_hash[:8]}... 远程={etag[:8]}...")
            elif last_modified:
                # 比较修改时间
                remote_time = time.mktime(datetime.datetime.strptime(
                    last_modified, "%a, %d %b %Y %H:%M:%S %Z").timetuple())
                if remote_time > local_mtime:
                    file_changed = True
                    log(f"  远程文件更新: {time.ctime(local_mtime)} → {time.ctime(remote_time)}")
            else:
                skip_reason = "文件未变更"
                log(f"  文件未变更")
        except Exception as e:
            log(f"⚠️ 无法验证远程文件: {url} - {e}", logging.WARNING)
            file_changed = True  # 出错时下载以确保更新
    else:
        file_changed = True
        log(f"  新文件")
    
    # 如果不需要下载
    if not file_changed:
        log(f"⏭️ 跳过: {url} ({skip_reason})")
        return False
    
    # 执行下载
    temp_path = f"{local_path}.tmp"
    start_time = time.time()
    
    for attempt in range(MAX_RETRIES):
        try:
            log(f"⬇️ 开始下载: {url}")
            with requests.get(url, headers=HEADERS, stream=True, timeout=60) as r:
                r.raise_for_status()
                total_size = int(r.headers.get("Content-Length", 0))
                downloaded = 0
                
                with open(temp_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 进度日志
                            if total_size > 0 and attempt == 0:  # 只在第一次尝试时记录进度
                                percent = (downloaded / total_size) * 100
                                if percent % 10 == 0:  # 每10%记录一次进度
                                    log(f"  进度: {percent:.0f}% ({downloaded}/{total_size} 字节)")
            
            # 验证下载
            downloaded_size = os.path.getsize(temp_path)
            if total_size > 0 and downloaded_size != total_size:
                raise IOError(f"大小不匹配: 预期 {total_size}, 实际 {downloaded_size}")
            
            # 设置文件修改时间为远程时间
            if last_modified:
                remote_time = time.mktime(datetime.datetime.strptime(
                    last_modified, "%a, %d %b %Y %H:%M:%S %Z").timetuple())
                os.utime(temp_path, (remote_time, remote_time))
            
            # 替换旧文件
            if os.path.exists(local_path):
                os.remove(local_path)
            os.rename(temp_path, local_path)
            
            # 记录统计信息
            dl_time = time.time() - start_time
            size_mb = downloaded_size / (1024 * 1024)
            speed = size_mb / dl_time if dl_time > 0 else 0
            log(f"✅ 下载完成: {url}")
            log(f"  大小: {size_mb:.2f} MB | 用时: {dl_time:.2f}秒 | 速度: {speed:.2f} MB/s")
            return True
        
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                log(f"🔄 重试 {attempt+1}/{MAX_RETRIES} - {url}: {e}", logging.WARNING)
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                log(f"❌ 下载失败: {url}: {e}", logging.ERROR)
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    return False

def process_directory(url, local_dir):
    """处理目录及其内容"""
    log(f"\n📂 处理目录: {url}")
    response = fetch_url(url)
    if not response:
        return 0, 0
    
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        processed_items = 0
        skipped_items = 0
        
        for link in soup.find_all('a'):
            href = link.get('href')
            if not href or href in ["../", "./"] or href.startswith(("?", "#", "javascript:")):
                continue
            
            full_url = urljoin(url, href)
            item_name = href.rstrip('/')
            
            # 处理目录
            if href.endswith('/'):
                sub_dir = os.path.join(local_dir, item_name)
                os.makedirs(sub_dir, exist_ok=True)
                log(f"  ├─ 进入子目录: {item_name}/")
                sub_processed, sub_skipped = process_directory(full_url, sub_dir)
                processed_items += sub_processed
                skipped_items += sub_skipped
            # 处理文件
            else:
                local_path = os.path.join(local_dir, item_name)
                if download_file(full_url, local_path):
                    processed_items += 1
                else:
                    skipped_items += 1
        
        log(f"📊 目录统计: {url}")
        log(f"  已处理: {processed_items} | 已跳过: {skipped_items}")
        return processed_items, skipped_items
    
    except Exception as e:
        log(f"❌ 处理目录出错 {url}: {e}", logging.ERROR)
        return 0, 0

if __name__ == "__main__":
    log(f"\n{'=' * 80}")
    log(f"🚀 开始同步: {BASE_URL} -> {LOCAL_ROOT}")
    log(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"{'=' * 80}\n")
    
    start_time = time.time()
    total_processed, total_skipped = process_directory(BASE_URL, LOCAL_ROOT)
    
    duration = time.time() - start_time
    log(f"\n{'=' * 80}")
    log(f"✅ 同步完成! 用时: {duration:.2f} 秒")
    log(f"📊 总计: 已处理 {total_processed} 个文件 | 已跳过 {total_skipped} 个文件")
    log(f"⏰ 结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"{'=' * 80}")
    
    # 添加空行分隔每次运行
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write("\n\n")
