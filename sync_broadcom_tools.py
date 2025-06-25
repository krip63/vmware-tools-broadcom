import os
import requests
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import hashlib
import logging
import sys
import datetime
import concurrent.futures
import re
from pathlib import Path
import argparse
import platform

# 配置
BASE_URL = "https://packages-prod.broadcom.com/tools/"
DEFAULT_LOCAL_ROOT = os.path.join("VMware Tools", "tools")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5"
}
MAX_RETRIES = 3
RETRY_DELAY = 5  # 秒
DEFAULT_LOG_FILE = "vmware_tools_sync.log"

# 设置日志系统
def setup_logger(log_file):
    logger = logging.getLogger('VMwareToolsSync')
    logger.setLevel(logging.INFO)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 格式化
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_remote_file_info(url, session):
    """获取远程文件信息"""
    file_info = {'size': 0, 'last_modified': None, 'etag': None}
    try:
        response = session.head(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        # 获取文件大小
        file_info['size'] = int(response.headers.get("Content-Length", 0))
        
        # 获取最后修改时间
        last_modified = response.headers.get("Last-Modified")
        if last_modified:
            try:
                file_info['last_modified'] = time.mktime(
                    datetime.datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z").timetuple())
            except Exception:
                pass
        
        # 获取ETag
        file_info['etag'] = response.headers.get("ETag", "").strip('"')
    
    except requests.RequestException as e:
        logger.warning(f"⚠️ 无法获取远程文件信息: {url} - {e}")
    
    return file_info

def should_download(url, local_path, remote_info, session):
    """检查是否需要下载文件"""
    # 新文件
    if not os.path.exists(local_path):
        logger.info(f"  新文件")
        return True
    
    try:
        # 获取本地文件信息
        local_size = os.path.getsize(local_path)
        local_mtime = os.path.getmtime(local_path)
        
        logger.info(f"🔍 检查文件: {os.path.basename(local_path)}")
        logger.info(f"  本地大小: {local_size} | 远程大小: {remote_info['size']}")
        
        # 大小检查
        if local_size != remote_info['size'] and remote_info['size'] > 0:
            logger.info(f"  文件大小变化: {local_size} → {remote_info['size']}")
            return True
        
        # 修改时间检查
        if remote_info['last_modified'] and remote_info['last_modified'] > local_mtime:
            logger.info(f"  远程文件更新: {time.ctime(local_mtime)} → {time.ctime(remote_info['last_modified'])}")
            return True
        
        # 哈希检查（如果ETag可用）
        if remote_info['etag']:
            local_hash = calculate_file_hash(local_path)
            if local_hash and remote_info['etag'] != local_hash:
                logger.info(f"  哈希值不匹配: 本地={local_hash[:8]}... 远程={remote_info['etag'][:8]}...")
                return True
        
        logger.info(f"  文件未变更")
        return False
    
    except Exception as e:
        logger.warning(f"⚠️ 文件检查出错: {url} - {e}")
        return True  # 出错时下载以确保更新

def calculate_file_hash(file_path):
    """计算文件的SHA-256哈希值"""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logger.error(f"❌ 计算哈希值时出错 {file_path}: {e}")
        return None

def download_file(task):
    """下载单个文件（线程安全）"""
    url, local_path, remote_info, session = task
    temp_path = f"{local_path}.tmp"
    
    try:
        logger.info(f"⬇️ 开始下载: {url}")
        start_time = time.time()
        
        with session.get(url, headers=HEADERS, stream=True, timeout=60) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("Content-Length", remote_info['size']))
            
            # 确保目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(temp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 获取最后修改时间
            last_modified_header = r.headers.get('Last-Modified')
        
        # 验证下载
        downloaded_size = os.path.getsize(temp_path)
        if total_size > 0 and downloaded_size != total_size:
            raise IOError(f"大小不匹配: 预期 {total_size}, 实际 {downloaded_size}")
        
        # 替换旧文件
        if os.path.exists(local_path):
            os.remove(local_path)
        os.rename(temp_path, local_path)
        
        # 设置文件修改时间
        if last_modified_header:
            try:
                remote_time = time.mktime(
                    datetime.datetime.strptime(last_modified_header, "%a, %d %b %Y %H:%M:%S %Z").timetuple())
                os.utime(local_path, (remote_time, remote_time))
                logger.debug(f"  文件修改时间已设置为: {last_modified_header}")
            except Exception as e:
                logger.warning(f"⚠️ 设置修改时间失败: {e}")
        
        # 记录统计信息
        dl_time = time.time() - start_time
        size_mb = downloaded_size / (1024 * 1024)
        speed = size_mb / dl_time if dl_time > 0 else 0
        logger.info(f"✅ 下载完成: {url}")
        logger.info(f"  大小: {size_mb:.2f} MB | 用时: {dl_time:.2f}秒 | 速度: {speed:.2f} MB/s")
        return True
    
    except Exception as e:
        logger.error(f"❌ 下载失败: {url}: {str(e)[:200]}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return False

def process_directory(url, local_dir, session):
    """处理目录及其内容（返回需要下载的文件列表）"""
    logger.info(f"\n📂 处理目录: {url}")
    download_tasks = []
    
    try:
        response = session.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
                logger.info(f"  ├─ 进入子目录: {item_name}/")
                download_tasks.extend(process_directory(full_url, sub_dir, session))
            # 处理文件
            else:
                local_path = os.path.join(local_dir, item_name)
                remote_info = get_remote_file_info(full_url, session)
                
                # 检查是否需要下载
                if should_download(full_url, local_path, remote_info, session):
                    download_tasks.append((full_url, local_path, remote_info, session))
    
    except Exception as e:
        logger.error(f"❌ 处理目录出错 {url}: {e}")
    
    return download_tasks

def get_cpu_count():
    """获取CPU核心数，用于确定线程数"""
    try:
        return os.cpu_count() or 4
    except:
        return 4

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='VMware Tools 同步工具')
    parser.add_argument('--local-dir', type=str, default=DEFAULT_LOCAL_ROOT, 
                        help=f'本地存储目录 (默认: {DEFAULT_LOCAL_ROOT})')
    parser.add_argument('--log-file', type=str, default=DEFAULT_LOG_FILE, 
                        help=f'日志文件路径 (默认: {DEFAULT_LOG_FILE})')
    parser.add_argument('--threads', type=int, default=0, 
                        help='线程数 (默认: 根据CPU核心数自动设置)')
    parser.add_argument('--retries', type=int, default=MAX_RETRIES, 
                        help=f'重试次数 (默认: {MAX_RETRIES})')
    parser.add_argument('--delay', type=int, default=RETRY_DELAY, 
                        help=f'重试延迟 (秒) (默认: {RETRY_DELAY})')
    parser.add_argument('--full-sync', action='store_true', 
                        help='强制完全同步 (忽略本地文件)')
    
    args = parser.parse_args()
    
    # 设置全局logger
    global logger
    logger = setup_logger(args.log_file)
    
    # 显示系统信息
    logger.info(f"\n{'=' * 80}")
    logger.info(f"🚀 开始 VMware Tools 同步")
    logger.info(f"🖥️ 系统: {platform.system()} {platform.release()} ({platform.machine()})")
    logger.info(f"💻 CPU: {os.cpu_count()} 核心")
    logger.info(f"📁 本地目录: {os.path.abspath(args.local_dir)}")
    logger.info(f"📝 日志文件: {os.path.abspath(args.log_file)}")
    logger.info(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'=' * 80}\n")
    
    start_time = time.time()
    
    # 创建会话对象
    session = requests.Session()
    
    # 收集所有需要下载的文件
    all_tasks = process_directory(BASE_URL, args.local_dir, session)
    
    if args.full_sync:
        logger.info("🔁 强制完全同步模式 - 所有文件将被下载")
    
    # 准备下载任务
    download_tasks = []
    for task in all_tasks:
        url, local_path, remote_info, session_ref = task
        if args.full_sync or should_download(url, local_path, remote_info, session):
            download_tasks.append((url, local_path, remote_info, session))
    
    logger.info(f"📋 发现 {len(download_tasks)} 个文件需要下载")
    
    # 设置线程数
    thread_count = args.threads or min(get_cpu_count() * 2, 16)  # 最多16线程
    logger.info(f"🧵 使用 {thread_count} 线程进行下载")
    
    # 多线程下载
    completed = 0
    failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        # 提交所有任务
        future_to_task = {executor.submit(download_file, task): task for task in download_tasks}
        
        # 处理结果
        for future in concurrent.futures.as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result()
                if result:
                    completed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"❌ 任务执行出错: {e}")
                failed += 1
    
    # 统计结果
    duration = time.time() - start_time
    logger.info(f"\n{'=' * 80}")
    logger.info(f"✅ 同步完成! 用时: {duration:.2f} 秒")
    logger.info(f"📊 统计:")
    logger.info(f"  总文件数: {len(all_tasks)}")
    logger.info(f"  需要下载: {len(download_tasks)}")
    logger.info(f"  成功下载: {completed}")
    logger.info(f"  下载失败: {failed}")
    logger.info(f"⏰ 结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'=' * 80}")
    
    # 添加空行分隔每次运行
    with open(args.log_file, "a", encoding="utf-8") as log_file:
        log_file.write("\n\n")

if __name__ == "__main__":
    main()
