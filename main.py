import requests, re, base64, time, socket, random
from urllib.parse import urlparse, parse_qs

# Расширенные источники (много VLESS/Reality)
SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/BardiaFA/Proxy-Collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/sub",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/vless.config",
    "https://raw.githubusercontent.com/Epodonios/vless-subscription/main/vless_sub.txt",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/E99_Sub_Merge.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
    "https://raw.githubusercontent.com/Aisuko/V2ray-Config/main/sub"
]

OUTPUT_FILE = "scr.txt"
HEADER = "# profile-title: 🏳️ Белый Семаха\n"
EMOJIS = ["🔮", "⚡", "🔥", "👾", "✨"]

def is_anti_dpi(key_url):
    """
    Проверяет, использует ли ключ технологии маскировки от ТСПУ.
    Если это простой TCP/TLS - возвращает False.
    """
    try:
        parsed = urlparse(key_url)
        params = parse_qs(parsed.query)
        
        # Получаем параметры безопасности и типа сети
        security = params.get('security', [''])[0].lower()
        net_type = params.get('type', [''])[0].lower()
        flow = params.get('flow', [''])[0].lower()
        
        # XTLS-Vision, Reality, gRPC и WebSocket (WS) хорошо живут в РФ
        if security == 'reality': return True
        if 'vision' in flow: return True
        if net_type in ['grpc', 'ws']: return True
        
        # Если это Shadowsocks, он должен быть с плагином (но парсить его сложнее, 
        # поэтому для РФ лучше делать упор на VLESS/Reality).
        return False
    except:
        return False

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

    all_keys = list(set(re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', raw_data)))
    random.shuffle(all_keys)
    
    results = []
    cache = {}
    
    print(f"Белый список: Начинаем отбор из {len(all_keys)} ключей...")

    for key in all_keys:
        if len(results) >= 100: break
        if key.startswith("trojan://"): continue
        
        clean = key.split("#")[0]
        
        # 1. СНАЧАЛА проверяем начинку ключа на устойчивость к ТСПУ
        if not is_anti_dpi(clean):
            continue
            
        # 2. ПОТОМ проверяем, жив ли он вообще (пингуем)
        try:
            if "@" in clean:
                addr = clean.split("@")[1].split("?")[0]
                host = addr.split(":")[0]
                port = int(addr.split(":")[1]) if ":" in addr else 443
                
                if get_ping(host, port) < 3500:
                    proto = clean.split("://")[0].upper()
                    results.append({"key": clean, "proto": proto, "host": host})
                    if len(results) % 10 == 0: print(f"Прошли DPI-контроль и пинг: {len(results)}/100")
        except: continue

    final = []
    for i, item in enumerate(results, 1):
        flag = get_country_flag(item["host"], cache)
        emoji = random.choice(EMOJIS)
        name = f"{flag} {item['proto']} {emoji} Семаха [{i}]"
        final.append(f"{item['key']}#{name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(final))
    print(f"Готово! В Белый Семаха добавлено {len(final)} бронебойных ключей.")

if __name__ == "__main__":
    process()
