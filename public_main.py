import requests
import re
import base64
import time
from urllib.parse import urlparse, quote

#public key database | DM me if you are the copyright holder and do not allow this to be distributed. . .
SOURCES = [
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt"
]
OUTPUT_FILE = "public_scr.txt"

country_cache = {}

def get_country_ru(ip):
    if not ip: return "Неизвестно"
    if ip in country_cache: return country_cache[ip]
    
    try:
        #translate RU
        resp = requests.get(f"http://ip-api.com/json/{ip}?lang=ru", timeout=2).json()
        country = resp.get("country", "Неизвестно")
        
        country_cache[ip] = country
        time.sleep(1.4) #def
        return country
    except:
        return "Неизвестно"

def safe_decode(data):
    try:
        return base64.b64decode(data).decode('utf-8')
    except:
        return data

def process():
    all_raw_text = ""
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10)
            all_raw_text += "\n" + safe_decode(r.text)
        except:
            continue

    found_keys = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', all_raw_text)
    unique_keys = list(set(found_keys))
    
    print(f"Найдено уникальных ключей: {len(unique_keys)}")
    
    processed_list = []
    
    #checking first 150 servers
    for key in unique_keys[:150]:
        try:
            base_part = key.split("#")[0]
            
            if key.startswith("vmess://"):
                new_name = "VMESS Публичный Семаха | Неизвестно"
                processed_list.append(f"{base_part}#{quote(new_name)}")
                continue
                
            parsed = urlparse(base_part)
            host = parsed.hostname
            
            country_ru = get_country_ru(host)
            proto = parsed.scheme.upper()
            
            #output 
            new_name = f"{proto} Публичный Семаха | {country_ru}"
            processed_list.append(f"{base_part}#{quote(new_name)}")
            
        except Exception:
            continue

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(processed_list))
        
    print(f"Сохранено публичных серверов: {len(processed_list)}")

if __name__ == "__main__":
    process()
