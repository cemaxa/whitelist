import requests, re, base64, time, socket, random
from urllib.parse import urlparse

SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/BardiaFA/Proxy-Collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/sub",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/E99_Sub_Merge.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
    "https://raw.githubusercontent.com/shifureader/v2ray-config/main/all.txt",
    "https://raw.githubusercontent.com/sarinaesmailzadeh/V2ray-Configs/main/All_Configs_Sub.txt"
]

OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🌐 Public VPN | @freedomprotocol_bot\n"

def get_ping(host, port):
    try:
        # Увеличили до 5 секунд, так как паблик-сервера часто тормозят
        socket.setdefaulttimeout(5.0)
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except: return 9999

def get_country_flag(ip, cache):
    if ip in cache: return cache[ip]
    try:
        time.sleep(1.3) # Защита от бана ip-api
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=status,countryCode", timeout=5).json()
        if resp.get('status') == 'success':
            code = resp.get('countryCode', 'UN')
            flag = "".join(chr(127397 + ord(c)) for c in code)
            cache[ip] = flag
            return flag
    except: pass
    return "🌐"

def process():
    raw_data = ""
    # Перемешиваем источники, чтобы не зависеть от одного автора
    random.shuffle(SOURCES)
    
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=20, verify=False) # Игнорим ошибки SSL источников
            t = r.text
            if "://" not in t[:50]:
                try: t = base64.b64decode(t).decode('utf-8')
                except: pass
            raw_data += "\n" + t
        except: continue

    # Извлекаем все ключи (кроме Trojan)
    all_keys = list(set(re.findall(r'(?:vless|vmess|ss)://[^\s]+', raw_data)))
    random.shuffle(all_keys)
    
    results = []
    cache = {}
    print(f"Публичные: Найдено {len(all_keys)} ключей. Начинаю поиск живых...")

    for key in all_keys:
        if len(results) >= 100: break
        
        try:
            clean = key.split("#")[0]
            parsed = urlparse(clean)
            host = parsed.hostname
            if not host: continue
            
            # Если порта нет, ставим стандартный 443
            port = parsed.port if parsed.port else 443
            
            ping = get_ping(host, port)
            if ping < 5000: # Берем всё, что ответило до 5 секунд
                results.append({"key": clean, "proto": parsed.scheme.upper(), "host": host})
                if len(results) % 10 == 0: print(f"Найдено живых: {len(results)}/100")
        except: continue

    final = []
    for item in results:
        flag = get_country_flag(item["host"], cache)
        name = f"{flag} {item['proto']} | Public | @freedomprotocol_bot"
        final.append(f"{item['key']}#{name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(final))
    print(f"Успех! Файл {OUTPUT_FILE} обновлен.")

if __name__ == "__main__":
    process()
