import requests, re, base64, os, socket, time
from urllib.parse import urlparse

SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/E99_Sub_Merge.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
]

OUTPUT_FILE = "scr.txt"
HEADER = "# profile-title: 🛡️ Белый Семаха (Anti-DPI)\n\n"

# Список разрешенных доменных зон и доменов для маскировки (SNI)
ALLOWED_SNI = ['.ru', '.by', '.su', 'vk.com', 'yandex', 'mail.ru', 'gosuslugi', 'ozon', 'avito']

def get_ping(host, port):
    try:
        socket.setdefaulttimeout(3.0)
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        s.close()
        return int((time.time() - start) * 1000)
    except: return None

def is_valid_anti_dpi(key):
    """Проверка: Reality/Vision + фильтр по SNI (RU-зоны)"""
    key_lower = key.lower()
    # 1. Проверка протокола
    if not ("reality" in key_lower or "xtls-rprx-vision" in key_lower):
        return False
    
    # 2. Проверка SNI (маскировки)
    # Ищем параметры sni= или sni: в ссылке
    sni_match = re.search(r'sni=([^&|#\s]+)', key_lower)
    if sni_match:
        sni = sni_match.group(1)
        if any(zone in sni for zone in ALLOWED_SNI):
            return True
    return False

def process():
    existing_keys = []
    # 1. Загружаем старые сервера для перепроверки
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "://" in line:
                    existing_keys.append(line.strip().split('#')[0])

    # 2. Собираем свежие ключи
    raw_data = ""
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15)
            content = r.text
            if "://" not in content[:50]:
                content = base64.b64decode(content).decode('utf-8')
            raw_data += "\n" + content
        except: continue
    
    found_keys = re.findall(r'(?:vless|vmess|ss)://[^\s]+', raw_data)
    
    # Объединяем старые и новые для тотальной проверки
    all_to_check = list(set(existing_keys + found_keys))
    final_list = []
    
    print(f"Всего на проверке: {len(all_to_check)} ключей...")

    for key in all_to_check:
        # Проверяем на ТСПУ-фильтр и SNI
        if is_valid_anti_dpi(key):
            try:
                parsed = urlparse(key.split('#')[0])
                host = parsed.hostname
                port = parsed.port if parsed.port else 443
                
                # Пингуем во второй раз (или первый, если новый)
                if get_ping(host, port):
                    name = "🛡️ RU-AntiDPI | @freedomprotocol_bot"
                    final_list.append(f"{key.split('#')[0]}#{name}")
                    if len(final_list) % 5 == 0:
                        print(f"Рабочих найдено: {len(final_list)}")
            except: continue

    # 3. Полная перезапись файла только РАБОЧИМИ и проверенными ключами
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(final_list))

    print(f"Обновление завершено! Сохранено {len(final_list)} живых серверов с RU-маскировкой.")

if __name__ == "__main__":
    process()
