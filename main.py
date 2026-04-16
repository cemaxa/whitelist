import requests
import re
import base64
import time
import socket
import random

#public sources . . . DM me (if it possible) if you are the copyright holder and do not allow this to be distributed.
SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/BardiaFA/Proxy-Collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/vless.config",
    "https://raw.githubusercontent.com/Epodonios/vless-subscription/main/vless_sub.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
]

OUTPUT_FILE = "scr.txt"
HEADER = "# profile-title: 🏳️ Белый Семаха\n"
EMOJIS = ["🎊", "⚡", "🔥", "🔮", "✨"]

def get_ping(host, port):
    try:
        start = time.time()
        socket.setdefaulttimeout(1.5)
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
        time.sleep(1.2)
        return flag
    except:
        return "🌐"

def process():
    all_raw_text = ""
    for url in SOURCES:
        try:
            print(f"Загружаю: {url}")
            r = requests.get(url, timeout=15)
            text = r.text
            if "://" not in text[:50]:
                try: text = base64.b64decode(text).decode('utf-8')
                except: pass
            all_raw_text += "\n" + text
        except: continue

    found_keys = list(set(re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', all_raw_text)))
    print(f"Найдено ключей: {len(found_keys)}. Начинаю проверку...")
    
    results = []
    country_cache = {}

    # Проверяем первые 300, чтобы найти 100 лучших
    for key in found_keys[:300]:
        try:
            # Очищаем ключ от старого названия
            clean_key = key.split("#")[0]
            
            # Извлекаем хост и порт для пинга
            if "@" in clean_key:
                server_part = clean_key.split("@")[1].split("?")[0]
                host = server_part.split(":")[0]
                port = int(server_part.split(":")[1]) if ":" in server_part else 443
            else:
                continue

            ping_time = get_ping(host, port)
            if ping_time < 3000:
                proto = clean_key.split("://")[0].upper()
                results.append({"key": clean_key, "ping": ping_time, "proto": proto, "host": host})
        except: continue

    results.sort(key=lambda x: x["ping"])
    top_100 = results[:100]

    processed_list = []
    for i, item in enumerate(top_100, 1):
        flag = get_country_flag(item["host"], country_cache)
        emoji = random.choice(EMOJIS)
        # Теперь название формируется БЕЗ quote(), чтобы оно было читаемым
        new_name = f"{flag} {item['proto']} {emoji} Семаха [{i}]"
        processed_list.append(f"{item['key']}#{new_name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(processed_list))
    
    print(f"Готово! Сохранено рабочих ключей: {len(processed_list)}")

if __name__ == "__main__":
    process()
