import requests, re, base64, time, socket, random
from urllib.parse import urlparse, parse_qs

#public keys 
SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/BardiaFA/Proxy-Collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/sub",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/vless.config",
    "https://raw.githubusercontent.com/Epodonios/vless-subscription/main/vless_sub.txt",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/E99_Sub_Merge.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
    "https://raw.githubusercontent.com/Aisuko/V2ray-Config/main/sub",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
]

OUTPUT_FILE = "scr.txt"
HEADER = "# profile-title: 🏳️ Белый Семаха\n"
EMOJIS = ["🚀", "⚡", "🔥", "💎", "✨"]

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
        time.sleep(1.2)
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=status,countryCode", timeout=5).json()
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
            r = requests.get(url, timeout=20)
            t = r.text
            if "://" not in t[:50]:
                try: t = base64.b64decode(t).decode('utf-8')
                except: pass
            raw_data += "\n" + t
        except: continue

    # Ищем VLESS, SS, Hysteria и Hysteria2
    all_keys = list(set(re.findall(r'(?:vless|ss|hysteria2?)://[^\s]+', raw_data)))
    random.shuffle(all_keys)
    
    results = []
    cache = {}
    
    print(f"Белый список: Начинаем отбор из {len(all_keys)} ключей...")

    for key in all_keys:
        if len(results) >= 100: break
        
        clean = key.split("#")[0]
        
        try:
            parsed = urlparse(clean)
            scheme = parsed.scheme.lower()
            
            # --- 1. ПРОВЕРКА SNI ДЛЯ VLESS ---
            if scheme == "vless":
                params = parse_qs(parsed.query)
                sni = params.get('sni', [''])[0].lower()
                # Регулярка ищет окончание на .ru, .рф, .ру или .su
                if not re.search(r'\.(ru|рф|ру|su)$', sni):
                    continue # Скипаем, если домен не российский
            
            # --- 2. ИЗВЛЕЧЕНИЕ ХОСТА И ПОРТА ДЛЯ ПИНГА ---
            host, port = None, None
            netloc = parsed.netloc
            
            if scheme == 'ss':
                # У Shadowsocks параметры могут быть в Base64
                if '@' in netloc:
                    hp = netloc.split('@')[-1]
                else:
                    padding = "=" * ((4 - len(netloc) % 4) % 4)
                    dec = base64.urlsafe_b64decode(netloc + padding).decode('utf-8')
                    hp = dec.split('@')[-1] if '@' in dec else None
                
                if hp and ':' in hp:
                    host, port = hp.rsplit(':', 1)
                    port = int(port)
            else:
                # Для VLESS и Hysteria
                if '@' in netloc:
                    hp = netloc.split('@')[-1]
                    if ':' in hp:
                        host, port = hp.rsplit(':', 1)
                        port = int(port)
            
            if not host or not port: continue
            
            # --- 3. ФИНАЛЬНЫЙ ПИНГ ---
            if get_ping(host, port) < 3500:
                results.append({"key": clean, "proto": scheme.upper(), "host": host})
                if len(results) % 10 == 0: 
                    print(f"Годен: {scheme.upper()} ({host}) | {len(results)}/100")
                    
        except Exception as e:
            continue

    final = []
    for i, item in enumerate(results, 1):
        flag = get_country_flag(item["host"], cache)
        emoji = random.choice(EMOJIS)
        name = f"{flag} {item['proto']} {emoji} Семаха [{i}]"
        final.append(f"{item['key']}#{name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(final))
    print(f"Готово! В Белый Семаха добавлено {len(final)} ключей с маскировкой под РФ.")

if __name__ == "__main__":
    process()
