import requests, re, base64, time, socket
from urllib.parse import urlparse

SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/BardiaFA/Proxy-Collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/sub",
    "https://raw.githubusercontent.com/sarinaesmailzadeh/V2ray-Configs/main/All_Configs_Sub.txt"
]

OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🌐 Публичные ключи\n"

def get_ping(host, port):
    try:
        # Уменьшили таймаут, чтобы отсекать медленные/мертвые сервера сразу
        socket.setdefaulttimeout(1.8)
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except: return 9999

def get_country_flag(ip, cache):
    if ip in cache: return cache[ip]
    # Если IP локальный или пустой - скипаем
    if not ip or ip.startswith("127."): return "🌐"
    try:
        # Увеличили паузу, чтобы не ловить бан от API
        time.sleep(1.5) 
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=status,countryCode", timeout=4).json()
        if resp.get("status") == "success":
            code = resp.get("countryCode", "UN")
            flag = "".join(chr(127397 + ord(c)) for c in code)
            cache[ip] = flag
            return flag
    except: pass
    return "🌐"

def process():
    raw_data = ""
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15)
            t = r.text
            if "://" not in t[:50]:
                try: t = base64.b64decode(t).decode('utf-8')
                except: pass
            raw_data += "\n" + t
        except: continue

    keys = list(set(re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', raw_data)))
    results = []
    cache = {}

    print(f"Публичные: Найдено {len(keys)} потенциальных ключей.")

    for key in keys:
        if len(results) >= 100: break # Нам нужно ровно 100
        if key.startswith("trojan://"): continue # Trojan не берем
        
        try:
            clean = key.split("#")[0]
            parsed = urlparse(clean)
            host = parsed.hostname
            if not host: continue
            
            port = parsed.port if parsed.port else 443
            ping = get_ping(host, port)
            
            # Если сервер реально ответил быстрее чем за 1.8 сек
            if ping < 1800:
                proto = parsed.scheme.upper()
                results.append({"key": clean, "ping": ping, "proto": proto, "host": host})
        except: continue

    results.sort(key=lambda x: x["ping"])
    
    final = []
    for item in results:
        flag = get_country_flag(item["host"], cache)
        # Формат: [Флаг] [Протокол] | Public | @freedomprotocol_bot
        name = f"{flag} {item['proto']} | Public | @freedomprotocol_bot"
        final.append(f"{item['key']}#{name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(final))
    print(f"Public: Готово, сохранено {len(final)} ключей.")

if __name__ == "__main__":
    process()
