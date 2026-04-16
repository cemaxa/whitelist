import requests, re, base64, time, socket, random
from urllib.parse import urlparse

# Твои каналы + резерв
TG_CHANNELS = ["V2RayRootFree", "outlineOpenKey"]
BACKUP_SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/E99_Sub_Merge.txt"
]

OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🌐 Публичный Семаха\n"

def get_tg_keys(channel):
    keys = []
    try:
        url = f"https://t.me/s/{channel}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=15)
        found = re.findall(r'(?:vless|vmess|ss)://[^\s<"\'&|]+', r.text)
        keys.extend(found)
    except: pass
    return keys

def get_ping(host, port):
    try:
        socket.setdefaulttimeout(3.5)
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except: return 9999

def get_country_flag(ip, cache):
    if ip in cache: return cache[ip]
    try:
        time.sleep(1.1) # Защита от бана API
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=status,countryCode", timeout=5).json()
        if resp.get('status') == 'success':
            code = resp.get('countryCode', 'UN')
            flag = "".join(chr(127397 + ord(c)) for c in code)
            cache[ip] = flag
            return flag
    except: pass
    return "🌐"

def process():
    all_raw_keys = []
    for chan in TG_CHANNELS:
        all_raw_keys.extend(get_tg_keys(chan))
    
    if len(all_raw_keys) < 30:
        for url in BACKUP_SOURCES:
            try:
                r = requests.get(url, timeout=15)
                content = r.text
                if "://" not in content[:50]:
                    content = base64.b64decode(content).decode('utf-8')
                all_raw_keys.extend(re.findall(r'(?:vless|vmess|ss)://[^\s]+', content))
            except: continue

    unique_keys = list(set(all_raw_keys))
    random.shuffle(unique_keys)
    
    valid_results = []
    cache = {}

    print(f"Проверка {len(unique_keys)} ключей...")

    for key in unique_keys:
        if len(valid_results) >= 40: break # Проверяем 40 штук, чтобы выбрать 10 лучших
        try:
            clean_url = key.split('#')[0]
            parsed = urlparse(clean_url)
            host = parsed.hostname
            if not host: continue
            
            port = parsed.port if parsed.port else 443
            ping = get_ping(host, port)
            
            if ping < 4000:
                proto = parsed.scheme.upper()
                valid_results.append({
                    "key": clean_url, "proto": proto, "host": host, "ping": ping
                })
        except: continue

    # Сортируем по пингу (от быстрых к медленным) и берем 10
    valid_results.sort(key=lambda x: x["ping"])
    top_10 = valid_results[:10]

    final_lines = []
    for i, item in enumerate(top_10, 1):
        flag = get_country_flag(item["host"], cache)
        # Формат: Флаг Протокол | Публичный Семаха [№]
        name = f"{flag} {item['proto']} | Публичный Семаха [{i}]"
        final_lines.append(f"{item['key']}#{name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(final_lines))
    print(f"Готово! В списке {len(final_lines)} топовых серверов.")

if __name__ == "__main__":
    process()
