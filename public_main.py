import requests, re, base64, time, socket, random
from urllib.parse import urlparse

# Спасибо https://t.me/outlineOpenKey за общедоступные ключи <3 
# Канал для парсинга и пара проверенных бэкап-ссылок
TG_CHANNELS = ["outlineOpenKey", "v2rayng_org"] 
BACKUP_SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/E99_Sub_Merge.txt"
]

OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🌐 Публичный Семаха\n"

def get_tg_keys(channel):
    """Парсит ключи прямо из веб-версии телеграм канала"""
    keys = []
    try:
        url = f"https://t.me/s/{channel}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=15)
        # Ищем протоколы в тексте сообщений
        found = re.findall(r'(?:vless|vmess|ss)://[^\s<"\'&]+', r.text)
        keys.extend(found)
        print(f"Из канала @{channel} получено {len(found)} потенциальных ключей.")
    except Exception as e:
        print(f"Ошибка парсинга TG {channel}: {e}")
    return keys

def get_ping(host, port):
    try:
        socket.setdefaulttimeout(4.0)
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return int((time.time() - start) * 1000)
    except: return 9999

def process():
    all_raw_keys = []
    
    # 1. Тянем из ТГ каналов (приоритет)
    for chan in TG_CHANNELS:
        all_raw_keys.extend(get_tg_keys(chan))
    
    # 2. Если из ТГ пришло мало, добираем из бэкапов
    if len(all_raw_keys) < 50:
        for url in BACKUP_SOURCES:
            try:
                r = requests.get(url, timeout=15)
                content = r.text
                if "://" not in content[:50]:
                    content = base64.b64decode(content).decode('utf-8')
                all_raw_keys.extend(re.findall(r'(?:vless|vmess|ss)://[^\s]+', content))
            except: continue

    all_keys = list(set(all_raw_keys))
    random.shuffle(all_keys)
    
    results = []
    print(f"Начинаю проверку {len(all_keys)} уникальных ключей...")

    for key in all_keys:
        if len(results) >= 100: break
        try:
            # Убираем лишнее (иногда в ТГ ссылках остаются HTML-сущности)
            clean_url = key.split('<')[0].split('"')[0].split('#')[0]
            parsed = urlparse(clean_url)
            host = parsed.hostname
            if not host or host.startswith('127.'): continue
            
            port = parsed.port if parsed.port else 443
            if get_ping(host, port) < 4000:
                results.append({"key": clean_url, "proto": parsed.scheme.upper()})
                if len(results) % 10 == 0: print(f"Живых: {len(results)}/100")
        except: continue

    final = []
    for item in results:
        # Для паблика упростим имена, чтобы не тратить время на API флагов (иногда оно тормозит)
        name = f"🌐 {item['proto']}-Public"
        final.append(f"{item['key']}#{name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(final))
    print(f"Успех! Файл обновлен. Найдено живых: {len(final)}")

if __name__ == "__main__":
    process()
