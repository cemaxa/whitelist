import requests, re, base64, time, socket, random
from urllib.parse import urlparse

#i love puppies <3
SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/E99_Sub_Merge.txt",
    "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/sashalsfk/V2Ray-Config/main/splited/vless.txt", # Свежий сплит
    "https://raw.githubusercontent.com/manyafit/Manya-V2ray-Collector/main/sub/mix" # Агрессивный скрапер
]

OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🌐 Публичный Семаха\n"

def get_ping(host, port):
    try:
        socket.setdefaulttimeout(4.0)
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except: return 9999

def get_country_flag(ip, cache):
    if ip in cache: return cache[ip]
    try:
        time.sleep(1.1)
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=status,countryCode", timeout=4).json()
        if resp.get('status') == 'success':
            code = resp.get('countryCode', 'UN')
            flag = "".join(chr(127397 + ord(c)) for c in code)
            cache[ip] = flag
            return flag
    except: pass
    return "🌐"

def process():
    raw_data = ""
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=25, verify=False)
            t = r.text
            if "://" not in t[:50]:
                try: t = base64.b64decode(t).decode('utf-8')
                except: pass
            raw_data += "\n" + t
        except: continue

    # Собираем всё, кроме Trojan
    all_keys = list(set(re.findall(r'(?:vless|vmess|ss)://[^\s]+', raw_data)))
    random.shuffle(all_keys)
    
    results = []
    cache = {}
    print(f"Поиск среди {len(all_keys)} ключей...")

    for key in all_keys:
        if len(results) >= 80: break # Сделаем 80, но качественных
        
        try:
            # Очищаем ссылку от мусора в названии
            clean_url = key.split("#")[0]
            parsed = urlparse(clean_url)
            host = parsed.hostname
            if not host or host.startswith('127.'): continue
            
            port = parsed.port if parsed.port else 443
            
            ping = get_ping(host, port)
            if ping < 3000: # Порог 3 сек — паблик быстрее редко работает
                results.append({"key": clean_url, "proto": parsed.scheme.upper(), "host": host})
                if len(results) % 5 == 0: print(f"Найдено: {len(results)}...")
        except: continue

    final = []
    for item in results:
        flag = get_country_flag(item["host"], cache)
        # Название делаем максимально коротким и понятным
        name = f"{flag} {item['proto']}-PUB"
        final.append(f"{item['key']}#{name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(final))
    print(f"Готово! В файле {len(final)} ключей.")

if __name__ == "__main__":
    process()
