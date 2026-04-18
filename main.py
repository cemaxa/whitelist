import requests, re, base64, os

# Твои источники для "Белого Семахи"
SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/E99_Sub_Merge.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
]

OUTPUT_FILE = "scr.txt"
HEADER = "# profile-title: 🛡️ Белый Семаха (Anti-DPI)\n\n"

def is_anti_dpi(key):
    """Проверка на наличие защиты от ТСПУ (Reality или Vision)"""
    return "reality" in key.lower() or "xtls-rprx-vision" in key.lower()

def process():
    # 1. Загружаем то, что уже есть в файле, чтобы не удалить рабочее
    existing_keys = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            # Собираем только сами ссылки, очищая от названий после #
            for line in f:
                if "://" in line:
                    existing_keys.append(line.strip().split('#')[0])

    # 2. Собираем новые ключи из интернета
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
    
    new_added = 0
    # 3. Фильтруем и добавляем только уникальные Anti-DPI ключи
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        # Если файл был пустой, пишем заголовок (проверка на размер)
        if os.path.getsize(OUTPUT_FILE) < 10:
            f.write(HEADER)

        for key in found_keys:
            clean_key = key.split('#')[0]
            # Если ключа нет в базе И он проходит фильтр ТСПУ
            if clean_key not in existing_keys and is_anti_dpi(clean_key):
                # Формируем название с пометкой защиты
                name = "🛡️ Anti-DPI | @freedomprotocol_bot"
                f.write(f"{clean_key}#{name}\n")
                existing_keys.append(clean_key) # Чтобы не дублировать в одном цикле
                new_added += 1

    print(f"Готово! В Белый Семаха добавлено {new_added} новых Anti-DPI серверов. Старые сохранены.")

if __name__ == "__main__":
    process()
