import requests
import re
import base64
import time
import socket
from urllib.parse import urlparse

#public keys | DM me (if it possible) if you are the copyright holder and do not allow this to be distributed.
SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/BardiaFA/Proxy-Collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/vless.config",
    "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/sub",
    "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes",
    "https://raw.githubusercontent.com/sarinaesmailzadeh/V2ray-Configs/main/All_Configs_Sub.txt"
]

OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🌐 Общедоступный VPN | PUBLIC | @freedomprotocol_bot\n"

def get_ping(host, port):
    try:
        start = time.time()
        # Смягчили таймаут до 2.5 секунд
        socket.setdefaulttimeout(2.5)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except:
        return 9999

def get_country_flag(ip, cache):
    if ip in cache: return cache[ip]
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        code = resp.get("countryCode", "UN")
        # Превращаем код страны в эмодзи флага
        flag = "".join(chr(127397 + ord(c)) for c in code) if code != "UN" else "🌐"
        cache[ip] = flag
        time.sleep(1.1) 
        return flag
    except:
        return "🌐"

def process():
    all_raw_text = ""
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15)
            text = r.text
            if "://" not in text[:50]:
                try: text = base64.b64decode(text).decode('utf-8')
                except: pass
            all_raw_text += "\n" + text
        except: continue

    # Собираем все ключи
    all_keys = list(set(re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', all_raw_text)))
    
    results = []
    country_cache = {}

    print(f"Найдено {len(all_keys)} ключей. Начинаю отбор лучших...")
    
    # Проверяем до 600 ключей, чтобы точно набрать 100 рабочих
    for key in all_keys[:600]:
        try:
            base_part = key.split("#")[0]
            parsed = urlparse(base_part)
            
            # ФИЛЬТР: Полностью удаляем Trojan
            if parsed.scheme.lower() == "trojan":
                continue
                
            if not parsed.hostname: continue
            
            port = parsed.port if parsed.port else 443
            ping_time = get_ping(parsed.hostname, port)
            
            # Если сервер ответил, добавляем в список
            if ping_time < 4000:
                results.append({
                    "key": base_part, 
                    "ping": ping_time, 
                    "proto": parsed.scheme.upper(), 
                    "host": parsed.hostname
                })
        except: continue
        
        if len(results) >= 150: break

    # Сортируем по качеству соединения
    results.sort(key=lambda x: x["ping"])
    top_100 = results[:100]

    processed_list = []
    for item in top_100:
        flag = get_country_flag(item["host"], country_cache)
        # НОВЫЙ ФОРМАТ: [Флаг] [Протокол] | Public | @freedomprotocol_bot
        new_name = f"{flag} {item['proto']} | Public | @freedomprotocol_bot"
        processed_list.append(f"{item['key']}#{new_name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(processed_list))
    
    print(f"Готово! В списке {len(processed_list)} серверов.")

if __name__ == "__main__":
    process()
