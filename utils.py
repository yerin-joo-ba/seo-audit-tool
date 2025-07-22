import tkinter as tk # Add this line if log_output is used here
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json

def extract_brand_country_and_lancode(url):
    brand_mapping = {"sulwhasoo": "SWS", "laneige": "LNG", "hera": "HERA", "aestura": "AES"}
    parsed = urlparse(url)
    brand = next((v for k, v in brand_mapping.items()
                  if k in parsed.netloc or k in parsed.path), "UNKNOWN")
    parts = parsed.path.strip("/").split("/")
    
    country = "UNKNOWN"
    if parsed.netloc.split('.')[0].lower() in ['hk', 'sg', 'my', 'ph', 'th', 'tw', 'vn', 'jp', 'kr']:
        country = parsed.netloc.split('.')[0].upper()
    elif parts and len(parts[0]) == 2 and parts[0].isalpha():
        country = parts[0].upper()
    elif len(parsed.netloc.split('.')) > 1 and len(parsed.netloc.split('.')[-2]) == 2 and parsed.netloc.split('.')[-2].isalpha():
        country = parsed.netloc.split('.')[-2].upper()

    lan = ""
    for p in parts:
        if re.match(r"^[a-z]{2}_[a-z]$", p) or (len(p) == 2 and p.isalpha() and p in ['ko', 'en', 'zh', 'ja']):
            lan = p
            break
    
    if len(parts) >= 2 and len(parts[0]) == 2 and len(parts[1]) == 2 and parts[0].isalpha() and parts[1].isalpha():
        if f"{parts[0]}/{parts[1]}" in ['kr/ko', 'int/en', 'jp/ja']:
            lan = f"{parts[0]}-{parts[1]}"

    return brand, country, lan

def is_hidden(tag):
    style = tag.get("style", "")
    cls = tag.get("class", [])
    hidden_attr = tag.has_attr("hidden")
    
    return (
        "display:none" in style.replace(" ", "").lower()
        or "visibility:hidden" in style.replace(" ", "").lower()
        or hidden_attr
        or ("hidden" in cls if isinstance(cls, list) else False)
    )

def collect_alt_texts(url, log_output):
    alt_data_for_url = []
    page_seen_images = set()

    try:
        res = requests.get(url, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")
        if log_output:
            log_output.insert(tk.END, f"[INFO] Collecting Alt Texts for: {url}\n")
            log_output.see(tk.END)

        for img in soup.find_all("img"):
            if is_hidden(img):
                continue
            raw_src = img.get("data-amsrc") or img.get("src", "")
            if not raw_src:
                continue
            full_img_url = raw_src if raw_src.startswith("http") else urljoin(url, raw_src)
            if full_img_url in page_seen_images:
                continue
            page_seen_images.add(full_img_url)
            alt_data_for_url.append({
                "Page URL": url,
                "Image URL": full_img_url,
                "Alt Text (AS-IS)": img.get("alt", "")
            })

        for script in soup.find_all("script", type="text/x-magento-init"):
            txt = script.get_text()
            try:
                cfg = json.loads(txt)
            except json.JSONDecodeError:
                continue

            for val in cfg.values():
                items = val.get("mage/gallery/gallery", {}).get("data", [])
                for item in items:
                    raw_src = item.get("img") or item.get("full")
                    if not raw_src:
                        continue
                    full_img_url = raw_src if raw_src.startswith("http") else urljoin(url, raw_src)
                    if full_img_url in page_seen_images:
                        continue
                    page_seen_images.add(full_img_url)
                    alt_data_for_url.append({
                        "Page URL": url,
                        "Image URL": full_img_url,
                        "Alt Text (AS-IS)": item.get("caption", "")
                    })
    except requests.exceptions.RequestException as e:
        if log_output:
            log_output.insert(tk.END, f"[ERROR] Failed to collect alt texts for {url}: {e}\n")
            log_output.see(tk.END)
    except Exception as e:
        if log_output:
            log_output.insert(tk.END, f"[ERROR] An unexpected error occurred while collecting alt texts for {url}: {e}\n")
            log_output.see(tk.END)
    
    return alt_data_for_url