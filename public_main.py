import requests, re, base64, time, socket, random
from urllib.parse import urlparse

SOURCES = [
    "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/E99_Sub_Merge.txt",
    "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/share/all",
    "https://raw.githubusercontent.com/cjosephl/v2ray-config/main/config.txt",
    "https://raw.githubusercontent.com/Epodonios/vless-subscription/main/vless_sub.txt",
    "https://raw.githubusercontent.com/PaimonS/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Aisuko/V2ray-Config/main/sub",
    "https://raw.githubusercontent.com/shifureader/v2ray-config/main/all.txt"
]

OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🌐 Public VPN | @freedomprotocol_bot\n"

def get_ping(host, port):
    try:
        socket.setdefaulttimeout(4.0) # Повысили до 4 секунд
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except: return 9999

def get_country_flag(ip, cache):
    if ip in cache: return cache[ip]
    try:
        time.sleep(1.2) # Чтобы API не отрубило
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

    # Собираем всё и перемешиваем, чтобы не тыкаться в одни и те же мертвые сервера
    all_keys = list(set(re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', raw_data)))
    random.shuffle(all_keys)
    
    results = []
    cache = {}

    print(f"Публичные: Начинаю перебор {len(all_keys)} ключей...")

    for key in all_keys:
        if len(results) >= 100: break # Как только нашли 100 — выходим
        if key.startswith("trojan://"): continue # Убираем Trojan для ТСПУ
        
        try:
            base_part = key.split("#")[0]
            parsed = urlparse(base_part)
            host = parsed.hostname
            if not host: continue
            
            port = parsed.port if parsed.port else 443
            ping = get_ping(host, port)
            
            if ping < 4000: # Берем все, что хоть как-то дышит
                results.append({"key": base_part, "proto": parsed.scheme.upper(), "host": host})
                if len(results) % 10 == 0: print(f"Найдено: {len(results)}/100")
        except: continue

    final = []
    for item in results:
        flag = get_country_flag(item["host"], cache)
        name = f"{flag} {item['proto']} | Public | @freedomprotocol_bot"
        final.append(f"{item['key']}#{name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(final))
    print(f"Готово! Сохранено {len(final)} ключей.")

if __name__ == "__main__":
    process()
