import requests
import re
import base64
import time
import socket
from urllib.parse import urlparse, quote

#public keys | DM me (if it possible) if you are the copyright holder and do not allow this to be distributed.
SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/BardiaFA/Proxy-Collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/vless.config",
    "https://raw.githubusercontent.com/peasoat/Proxies/main/proxies.txt",
    "https://raw.githubusercontent.com/sarinaesmailzadeh/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/mizhenqiang/v2ray-free/master/v2",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub"
]

OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🌐 Общедоступный VPN | PUBLIC | @freedomprotocol_bot\n"

def get_ping(host, port):
    try:
        start = time.time()
        #timer up to 2s
        socket.setdefaulttimeout(2.0)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except:
        return 9999

def get_country_ru(ip, cache):
    if ip in cache: return cache[ip]
    try:
        #russian lang
        resp = requests.get(f"http://ip-api.com/json/{ip}?lang=ru", timeout=2).json()
        country = resp.get("country", "Неизвестно")
        cache[ip] = country
        time.sleep(1.2) #api pause
        return country
    except:
        return "Неизвестно"

def process():
    all_raw_text = ""
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15)
            text = r.text
            # Проверка на Base64 (часто подписки закодированы)
            if "://" not in text[:50]:
                try:
                    text = base64.b64decode(text).decode('utf-8')
                except: pass
            all_raw_text += "\n" + text
        except: continue

    #vless prioritet
    all_keys = list(set(re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', all_raw_text)))
    
    # Сначала берем VLESS, потом остальные
    vless_keys = [k for k in all_keys if k.startswith("vless://")]
    other_keys = [k for k in all_keys if not k.startswith("vless://")]
    sorted_keys = vless_keys + other_keys

    results = []
    country_cache = {}

    print(f"Найдено ключей: {len(sorted_keys)}. Начинаю глубокую проверку...")
    
    #up limits
    for key in sorted_keys[:500]:
        try:
            base_part = key.split("#")[0]
            parsed = urlparse(base_part)
            if not parsed.hostname: continue
            
            port = parsed.port if parsed.port else 443
            ping_time = get_ping(parsed.hostname, port)
            
            if ping_time < 3000: # Берем всё, что отвечает быстрее 3 сек
                results.append({
                    "key": base_part, 
                    "ping": ping_time, 
                    "proto": parsed.scheme.upper(), 
                    "host": parsed.hostname
                })
        except: continue
        
        #autostop if serv count = 100
        if len(results) >= 150: break

    # Сортируем по качеству (пингу)
    results.sort(key=lambda x: x["ping"])
    top_100 = results[:100]

    processed_list = []
    for item in top_100:
        country = get_country_ru(item["host"], country_cache)
        # Название по твоему ТЗ
        new_name = f"{item['proto']} Публичный Семаха | {country}"
        processed_list.append(f"{item['key']}#{quote(new_name)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(processed_list))
    
    print(f"Готово! В списке {len(processed_list)} серверов.")

if __name__ == "__main__":
    process()
