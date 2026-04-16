import requests
import re
import base64
import time
import socket
from urllib.parse import urlparse, quote

SOURCES = [
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt"
]
OUTPUT_FILE = "public_scr.txt"
#output header
HEADER = "# profile-title: 🌐 Общедоступный VPN | PUBLIC | @freedomprotocol_bot\n"

def get_ping(host, port):
    try:
        start = time.time()
        socket.setdefaulttimeout(1.2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except:
        return 9999

def get_country_ru(ip, cache):
    if ip in cache: return cache[ip]
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?lang=ru", timeout=2).json()
        country = resp.get("country", "Неизвестно")
        cache[ip] = country
        time.sleep(1.4)
        return country
    except:
        return "Неизвестно"

def process():
    all_raw_text = ""
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10)
            text = r.text
            if "://" not in text:
                try: text = base64.b64decode(text).decode('utf-8')
                except: pass
            all_raw_text += "\n" + text
        except: continue

    found_keys = list(set(re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', all_raw_text)))
    results = []
    country_cache = {}

    print(f"Тестируем публичные серверы...")
    for key in found_keys[:250]:
        try:
            base_part = key.split("#")[0]
            parsed = urlparse(base_part)
            if not parsed.hostname: continue
            
            ping_time = get_ping(parsed.hostname, parsed.port or 443)
            if ping_time < 2000:
                results.append({"key": base_part, "ping": ping_time, "proto": parsed.scheme.upper(), "host": parsed.hostname})
        except: continue

    results.sort(key=lambda x: x["ping"])
    top_100 = results[:100]

    processed_list = []
    for item in top_100:
        country = get_country_ru(item["host"], country_cache)
        new_name = f"{item['proto']} Публичный Семаха | {country}"
        processed_list.append(f"{item['key']}#{quote(new_name)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        #pos
        f.write(HEADER + "\n".join(processed_list))

if __name__ == "__main__":
    process()
