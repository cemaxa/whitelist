import requests, re, base64, time, socket, random
from urllib.parse import urlparse

#agressive public vpn key sources
SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/E99_Sub_Merge.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
    "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes",
    "https://raw.githubusercontent.com/2dust/v2rayCustomGroup/master/list.txt",
    "https://raw.githubusercontent.com/LonUp/NodeList/main/V2RAY/Latest.txt",
    "https://raw.githubusercontent.com/shifureader/v2ray-config/main/all.txt",
    "https://raw.githubusercontent.com/Serein7/V2Ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Zizifn/free-v2ray-config/main/v2ray.txt"
]

OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🌐 Public VPN | @freedomprotocol_bot\n"

def get_ping(host, port):
    try:
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
        time.sleep(1.3)
        # Ограничиваем поля, чтобы ответ был быстрее
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
    random.shuffle(SOURCES)
    
    for url in SOURCES:
        try:
            # Отключаем проверку SSL, чтобы не падать на кривых доменах источников
            r = requests.get(url, timeout=25, verify=False)
            t = r.text
            # Проверка на Base64
            if "://" not in t[:50]:
                try: t = base64.b64decode(t).decode('utf-8')
                except: pass
            raw_data += "\n" + t
            print(f"Загружено: {url}")
        except: continue

    # Ищем все основные протоколы
    all_keys = list(set(re.findall(r'(?:vless|vmess|ss)://[^\s]+', raw_data)))
    random.shuffle(all_keys)
    
    results = []
    cache = {}
    print(f"Всего найдено ссылок: {len(all_keys)}. Начинаю проверку...")

    for key in all_keys:
        if len(results) >= 100: break
        
        try:
            # Очищаем ключ от старых имен
            base_part = key.split("#")[0]
            parsed = urlparse(base_part)
            host = parsed.hostname
            if not host: continue
            
            port = parsed.port if parsed.port else 443
            
            ping = get_ping(host, port)
            if ping < 5000:
                results.append({"key": base_part, "proto": parsed.scheme.upper(), "host": host})
                if len(results) % 5 == 0:
                    print(f"Живых: {len(results)}/100")
        except: continue

    final = []
    for item in results:
        flag = get_country_flag(item["host"], cache)
        # Чистое имя без лишнего мусора
        name = f"{flag} {item['proto']} | Public | @freedomprotocol_bot"
        final.append(f"{item['key']}#{name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(final))
    
    if len(final) > 0:
        print(f"Успех! Собрано {len(final)} рабочих ключей.")
    else:
        print("Ошибка: Не удалось найти ни одного живого ключа. Проверь интернет или источники.")

if __name__ == "__main__":
    process()
