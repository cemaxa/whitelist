import requests, re, base64, time, socket, random

SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/BardiaFA/Proxy-Collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/sub",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/vless.config",
    "https://raw.githubusercontent.com/Epodonios/vless-subscription/main/vless_sub.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
]

OUTPUT_FILE = "scr.txt"
HEADER = "# profile-title: 🏳️ Белый Семаха\n"
EMOJIS = ["🔮", "⚡", "🔥", "👾", "✨"]

def get_ping(host, port):
    try:
        socket.setdefaulttimeout(3.5) # Увеличили для надежности
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except: return 9999

def get_country_flag(ip, cache):
    if ip in cache: return cache[ip]
    try:
        time.sleep(1.2) # Чтобы API не забанило
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

    # Собираем уникальные ключи
    keys = list(set(re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', raw_data)))
    random.shuffle(keys) # Перемешиваем для разнообразия
    
    results = []
    cache = {}

    for key in keys:
        if len(results) >= 100: break
        if key.startswith("trojan://"): continue # Пропускаем троян
        
        try:
            clean = key.split("#")[0]
            # Извлекаем хост и порт для проверки
            if "@" in clean:
                addr = clean.split("@")[1].split("?")[0]
                host = addr.split(":")[0]
                port = int(addr.split(":")[1]) if ":" in addr else 443
                
                p = get_ping(host, port)
                if p < 3500:
                    proto = clean.split("://")[0].upper()
                    results.append({"key": clean, "proto": proto, "host": host})
                    print(f"Добавлен {len(results)}/100: {host}")
        except: continue

    final = []
    for i, item in enumerate(results, 1):
        flag = get_country_flag(item["host"], cache)
        # Название: [Флаг] [Протокол] [Эмодзи] Семаха [Номер]
        name = f"{flag} {item['proto']} {random.choice(EMOJIS)} Семаха [{i}]"
        final.append(f"{item['key']}#{name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(final))

if __name__ == "__main__":
    process()
