import requests, re, base64, time, socket
from urllib.parse import urlparse

SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/BardiaFA/Proxy-Collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/sub",
    "https://raw.githubusercontent.com/sarinaesmailzadeh/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
]

OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🌐 Public VPN | @freedomprotocol_bot\n"

def get_ping(host, port):
    try:
        socket.setdefaulttimeout(2.5)
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except: return 9999

def get_country_flag(ip, cache):
    if ip in cache: return cache[ip]
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        code = resp.get("countryCode", "UN")
        flag = "".join(chr(127397 + ord(c)) for c in code) if code != "UN" else "🌐"
        cache[ip] = flag
        time.sleep(1.2)
        return flag
    except: return "🌐"

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

    all_keys = list(set(re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', all_raw_text)))
    results = []
    country_cache = {}

    for key in all_keys:
        if len(results) >= 150: break
        try:
            base_part = key.split("#")[0]
            parsed = urlparse(base_part)
            if parsed.scheme.lower() == "trojan": continue # Trojan не берем
            if not parsed.hostname: continue
            
            port = parsed.port if parsed.port else 443
            ping = get_ping(parsed.hostname, port)
            if ping < 4500:
                results.append({"key": base_part, "ping": ping, "proto": parsed.scheme.upper(), "host": parsed.hostname})
        except: continue

    results.sort(key=lambda x: x["ping"])
    processed_list = []
    for item in results[:100]:
        flag = get_country_flag(item["host"], country_cache)
        # Формат: [Флаг] [Протокол] | Public | @freedomprotocol_bot
        new_name = f"{flag} {item['proto']} | Public | @freedomprotocol_bot"
        processed_list.append(f"{item['key']}#{new_name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(processed_list))

if __name__ == "__main__":
    process()
