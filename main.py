import requests
import re
import base64
import time
import socket
import random
from urllib.parse import urlparse, quote

SOURCES = [
    "https://raw.githubusercontent.com/Temnuk/naabuzil/main/whitelist_full",
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt",
    "https://raw.githubusercontent.com/Epodonios/vless-subscription/main/vless_sub.txt",
    "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
]
OUTPUT_FILE = "scr.txt"
EMOJIS = ["🚀", "⚡", "🔥", "💎", "✨", "🛡️", "🔮", "🎯", "👑", "🛰️"]

def get_ping(host, port):
    """Замеряет время отклика сервера в миллисекундах"""
    try:
        start = time.time()
        socket.setdefaulttimeout(2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except:
        return 9999

def get_country_flag(ip, cache):
    if ip in cache: return cache[ip]
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=2).json()
        code = resp.get("countryCode", "UN")
        flag = "".join(chr(127397 + ord(c)) for c in code) if code != "UN" else "🌐"
        cache[ip] = flag
        time.sleep(1.4)
        return flag
    except:
        return "🌐"

def process():
    all_raw_text = ""
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10)
            all_raw_text += "\n" + (base64.b64decode(r.text).decode('utf-8') if "://" not in r.text else r.text)
        except: continue

    found_keys = list(set(re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', all_raw_text)))
    results = []
    country_cache = {}

    print(f"Проверка {len(found_keys)} ключей...")
    for key in found_keys[:300]: # Берем с запасом для проверки
        try:
            base_part = key.split("#")[0]
            parsed = urlparse(base_part)
            if not parsed.hostname: continue
            
            ping_time = get_ping(parsed.hostname, parsed.port or 443)
            if ping_time < 2500: # Если сервер вообще ответил
                results.append({"key": base_part, "ping": ping_time, "proto": parsed.scheme.upper(), "host": parsed.hostname})
        except: continue

    # Сортируем по пингу (от меньшего к большему) и берем ТОП-100
    results.sort(key=lambda x: x["ping"])
    top_100 = results[:100]

    processed_list = []
    for i, item in enumerate(top_100, 1):
        flag = get_country_flag(item["host"], country_cache)
        emoji = random.choice(EMOJIS)
        new_name = f"{flag} {item['proto']} {emoji} Белый Семаха [{i}]"
        processed_list.append(f"{item['key']}#{quote(new_name)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(processed_list))

if __name__ == "__main__":
    process()
