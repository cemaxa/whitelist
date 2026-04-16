import requests
import re
import base64
import time
import socket
import random

# Источники с высоким приоритетом VLESS
SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/BardiaFA/Proxy-Collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/vless.config",
    "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/sub",
    "https://raw.githubusercontent.com/Epodonios/vless-subscription/main/vless_sub.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
]

OUTPUT_FILE = "scr.txt"
HEADER = "# profile-title: 🏳️ Белые списки | PUBLIC | @freedomprotocol_bot\n"
EMOJIS = ["👾", "⚡", "🔥", "🔮", "✨"]

def get_ping(host, port):
    try:
        start = time.time()
        socket.setdefaulttimeout(2.5) # Смягчили таймаут
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
        flag = "".join(chr(127397 + ord(c)) for c in code) if code != "UN" else "🌐"
        cache[ip] = flag
        time.sleep(1.2) # Пауза, чтобы API не заблокировало
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

    # Ищем все протоколы
    found_keys = list(set(re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', all_raw_text)))
    print(f"Найдено всего ключей: {len(found_keys)}. Начинаю проверку...")
    
    results = []
    country_cache = {}

    for key in found_keys:
        if len(results) >= 130: break # Собираем с запасом
        try:
            # ФИЛЬТР: Никаких Trojan
            if key.startswith("trojan://"):
                continue

            clean_key = key.split("#")[0]
            
            # Парсим хост и порт
            if "@" in clean_key:
                addr_part = clean_key.split("@")[1].split("?")[0]
                host = addr_part.split(":")[0]
                port = int(addr_part.split(":")[1]) if ":" in addr_part else 443
            else: continue

            ping_time = get_ping(host, port)
            if ping_time < 4500: # Берем все, что подает признаки жизни
                proto = clean_key.split("://")[0].upper()
                results.append({"key": clean_key, "ping": ping_time, "proto": proto, "host": host})
        except: continue

    # Сортируем по скорости и берем 100 лучших
    results.sort(key=lambda x: x["ping"])
    top_100 = results[:100]

    processed_list = []
    for i, item in enumerate(top_100, 1):
        flag = get_country_flag(item["host"], country_cache)
        emoji = random.choice(EMOJIS)
        # Формат: [Флаг] [Протокол] [Эмодзи] Семаха [Номер]
        new_name = f"{flag} {item['proto']} {emoji} Семаха [{i}]"
        processed_list.append(f"{item['key']}#{new_name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(processed_list))
    
    print(f"Готово! Сохранено рабочих ключей: {len(processed_list)}")

if __name__ == "__main__":
    process()
