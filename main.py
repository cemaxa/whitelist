import requests
import re
import base64
import time
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

country_cache = {}

# Твой личный набор эмодзи для разнообразия
EMOJIS = ["🚀", "⚡", "🔥", "💎", "✨", "🛡️", "🔮", "🎯", "👑", "🛰️", "👾"]

def get_country_flag(ip):
    if not ip: return "🌐"
    if ip in country_cache: return country_cache[ip]
    
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=2).json()
        code = resp.get("countryCode", "UN")
        flag = "🌐" if code == "UN" else "".join(chr(127397 + ord(c)) for c in code)
        
        country_cache[ip] = flag
        time.sleep(1.4)
        return flag
    except:
        return "🌐"

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
    
    processed_list = []
    counter = 1 # Запускаем счетчик для нумерации серверов
    
    for key in unique_keys[:150]:
        try:
            base_part = key.split("#")[0]
            emoji = random.choice(EMOJIS) # Выбираем случайный эмодзи
            
            if key.startswith("vmess://"):
                new_name = f"🌐 VMESS {emoji} Семаха [{counter}]"
                processed_list.append(f"{base_part}#{quote(new_name)}")
                counter += 1
                continue
                
            parsed = urlparse(base_part)
            host = parsed.hostname
            
            flag = get_country_flag(host)
            proto = parsed.scheme.upper()
            
            # Собираем красивое и короткое имя
            new_name = f"{flag} {proto} {emoji} Семаха [{counter}]"
            processed_list.append(f"{base_part}#{quote(new_name)}")
            counter += 1
            
        except Exception:
            continue

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(processed_list))

if __name__ == "__main__":
    process()
