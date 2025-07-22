import tkinter as tk # Add this line if log_output is used here
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import json
import os

SITEMAP_FILE = "sitemap_mapping.json"

# 기본 매핑 데이터 (파일이 없을 경우 사용)
default_sitemap_mapping = {
    "https://hk.sulwhasoo.com/tc_s/": "https://hk.sulwhasoo.com/media/sulwhasoo_hk.xml", # 이 값은 비어있으므로 필요시 채워주세요.
    "https://hk.sulwhasoo.com/en_s/": "https://hk.sulwhasoo.com/media/sulwhasoo_hk.xml",
    "https://my.sulwhasoo.com/": "https://my.sulwhasoo.com/sitemap.xml",
    "https://sg.sulwhasoo.com/": "https://sg.sulwhasoo.com/sitemap.xml",
    "https://th.sulwhasoo.com/": "https://th.sulwhasoo.com/sitemap.xml",
    "https://tw.sulwhasoo.com/": "https://tw.sulwhasoo.com/media/sulwhasoo_sitemap.xml",
    "https://vn.sulwhasoo.com/": "https://vn.sulwhasoo.com/sitemap.xml",
    "https://hk.laneige.com/tc_l/": "https://hk.laneige.com/media/laneige_hk.xml",
    "https://my.laneige.com/": "https://my.laneige.com/sitemap.xml",
    "https://www.laneige.com.vn/": "https://www.laneige.com.vn/media/vn_laneige_sitemap.xml",
    "https://ph.laneige.com/": "https://ph.laneige.com/sitemap.xml",
    "https://sg.laneige.com/": "https://sg.laneige.com/sitemap.xml",
    "https://th.laneige.com/": "https://th.laneige.com/sitemap.xml",
    "https://tw.laneige.com/": "https://tw.laneige.com/media/laneige_sitemap.xml",
    "https://www.laneige.com/jp/ja/": "https://www.laneige.com/jp/ja/sitemap.xml",
    "https://jp.hera.com/": "https://jp.hera.com/sitemap.xml",
    "https://hk.ap-beauty.com/tc_a/": "https://hk.amorepacific.com/media/amorepacific_hk.xml",
    "https://www.sulwhasoo.com/int/en/": 'https://www.sulwhasoo.com/int/en/sitemap.xml',
    "https://www.sulwhasoo.com/kr/ko/": "https://www.sulwhasoo.com/kr/ko/sitemap.xml",
    "https://www.laneige.com/kr/ko/": "https://www.laneige.com/kr/ko/sitemap.xml",
    "https://www.hera.com/kr/ko/": "https://www.hera.com/kr/ko/sitemap.xml",
}

# 사이트맵 매핑 파일을 로드하거나, 파일이 없으면 기본 매핑을 반환
def load_sitemap_mapping():
    if os.path.exists(SITEMAP_FILE):
        with open(SITEMAP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_sitemap_mapping

# 사이트맵 매핑을 파일로 저장
def save_sitemap_mapping(mapping_data):
    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping_data, f, indent=2, ensure_ascii=False)

def extract_base_url(url):
    parsed = urlparse(url)
    netloc = parsed.netloc
    path = parsed.path.rstrip('/')

    if netloc.startswith("www."):
        path_parts = path.strip("/").split("/")
        if len(path_parts) >= 2 and len(path_parts[0]) == 2 and len(path_parts[1]) == 2:
            base_url = f"{parsed.scheme}://{netloc}/{path_parts[0]}/{path_parts[1]}/"
        else:
            base_url = f"{parsed.scheme}://{netloc}/"
    else:
        base_url = f"{parsed.scheme}://{netloc}/"
    
    return base_url

def remove_language_code(url):
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")
    if path_parts and re.match(r"^[a-z]{2}_[a-z]{1}$", path_parts[0]):
        new_path = "/" + "/".join(path_parts[1:]) if len(path_parts) > 1 else "/"
    else:
        new_path = parsed.path
    return f"{parsed.scheme}://{parsed.netloc}{new_path}"

def find_sitemap_url(base_url, current_sitemap_mapping, log_output):
    normalized_base = remove_language_code(base_url)
    for key in current_sitemap_mapping:
        normalized_key = remove_language_code(key)
        if normalized_base.startswith(normalized_key):
            if log_output:
                log_output.insert(tk.END, f"[INFO] Sitemap mapping found for {base_url}: {current_sitemap_mapping[key]}\n")
                log_output.see(tk.END)
            return current_sitemap_mapping[key]
    if log_output:
        log_output.insert(tk.END, f"[WARN] No sitemap mapping found for base URL: {base_url}\n")
        log_output.see(tk.END)
    return None

def normalize_url(url):
    parsed = urlparse(url.strip())
    normalized = parsed.geturl()
    return normalized

def is_url_in_sitemaps(sitemap_url, full_url, visited_sitemaps=None, log_output=None):
    if visited_sitemaps is None:
        visited_sitemaps = set()
    if sitemap_url in visited_sitemaps:
        return None
    visited_sitemaps.add(sitemap_url)

    try:
        if log_output:
            log_output.insert(tk.END, f"[INFO] Accessing sitemap: {sitemap_url}\n")
            log_output.see(tk.END)
        response = requests.get(sitemap_url, timeout=10)
        if response.status_code != 200:
            if log_output:
                log_output.insert(tk.END, f"[ERROR] Failed to fetch sitemap ({response.status_code}): {sitemap_url}\n")
                log_output.see(tk.END)
            return None

        soup = BeautifulSoup(response.content, 'xml')

        sitemap_tags = soup.find_all('sitemap')
        if sitemap_tags:
            for sitemap in sitemap_tags:
                loc = sitemap.find('loc')
                if loc:
                    nested_sitemap_url = loc.get_text(strip=True)
                    found_in_sitemap = is_url_in_sitemaps(nested_sitemap_url, full_url, visited_sitemaps, log_output)
                    if found_in_sitemap:
                        return found_in_sitemap
            return None

        url_tags = soup.find_all('url')
        loc_tags = [url.find('loc') for url in url_tags if url.find('loc')]
        for loc in loc_tags:
            sitemap_url_in_loc = loc.get_text(strip=True).strip()
            if full_url == sitemap_url_in_loc:
                if log_output:
                    log_output.insert(tk.END, f"[INFO] URL found in sitemap: {sitemap_url}\n")
                    log_output.see(tk.END)
                return sitemap_url
        return None
    except Exception as e:
        if log_output:
            log_output.insert(tk.END, f"[ERROR] Error fetching sitemap {sitemap_url}: {e}\n")
            log_output.see(tk.END)
        return None

def check_sitemap_inclusion(full_url, current_sitemap_mapping, log_output):
    base_url = extract_base_url(full_url)
    # find_sitemap_url 호출 시 log_output 전달
    sitemap_url = find_sitemap_url(base_url, current_sitemap_mapping, log_output)
    if not sitemap_url:
        log_output.insert(tk.END, f"[WARN] Sitemap URL not found for {full_url}.\n", "WARN")
        log_output.see(tk.END)
        return {
            "현황": "Sitemap URL 없음",
            "Comment": "Sitemap 데이터 없음",
            "SEO 수정안": "Sitemap 추가 필요"
        }

    # is_url_in_sitemaps 호출 시 log_output 전달
    found_in_sitemap = is_url_in_sitemaps(sitemap_url, full_url, log_output=log_output)
    if found_in_sitemap:
        log_output.insert(tk.END, f"[INFO] URL included in Sitemap: {full_url}\n", "INFO")
        log_output.see(tk.END)
        return {
            "현황": "Sitemap 포함",
            "Comment": "이슈 없음",
            "SEO 수정안": "N/A"
        }
    else:
        log_output.insert(tk.END, f"[WARN] URL NOT included in Sitemap: {full_url}\n", "WARN")
        log_output.see(tk.END)
        return {
            "현황": "Sitemap 미포함",
            "Comment": "URL 추가 필요",
            "SEO 수정안": f"{full_url} 추가 필요"
        }

# 초기 sitemap_mapping.json 파일 생성 (프로그램 최초 실행 시 필요)
# 이 스크립트가 단독으로 실행될 때만 실행되도록 보호
if __name__ == "__main__":
    if not os.path.exists(SITEMAP_FILE):
        save_sitemap_mapping(default_sitemap_mapping)
        print(f"'{SITEMAP_FILE}' 파일이 생성되었습니다.")
    else:
        print(f"'{SITEMAP_FILE}' 파일이 이미 존재합니다.")