import requests, re, random, time, os
from urllib.parse import urlparse

CHANNEL = "outlineOpenKey"
ID_FILE = "last_id.txt"
OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🔮 Публичный Семаха\n\n"
EMOJI_POOL = ["🔮", "🌑", "👾", "🎊", "✨", "🎉", "🎀", "🪄", "🪬", "💣", "🍖", "⚡", "🔥", "🌠"]

def get_country_flag(ip):
    try:
        # Ускоренный запрос флага
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=countryCode", timeout=5).json()
        code = resp.get('countryCode', 'UN')
        return "".join(chr(127397 + ord(c)) for c in code)
    except: return "🌐"

def parse_post(post_id):
    try:
        url = f"https://t.me/{CHANNEL}/{post_id}?embed=1"
        r = requests.get(url, timeout=10)
        if r.status_code != 200: return None
        found = re.findall(r'(?:vless|vmess|ss)://[^\s<"\'&|]+', r.text)
        return found[0] if found else None
    except: return None

def process():
    # 1. Читаем последний ID
    if os.path.exists(ID_FILE):
        with open(ID_FILE, "r") as f:
            last_id = int(f.read().strip())
    else:
        last_id = 7689

    # 2. Читаем текущий список, чтобы не дублировать
    current_content = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            current_content = [l.strip() for l in f.readlines() if "://" in l]

    new_keys_found = 0
    current_id = last_id + 1
    
    # За один запуск проверяем до 50 новых постов (чтобы не пропустить за сутки)
    print(f"Начинаю поиск новых ключей начиная с ID {current_id}...")
    
    while True:
        new_key = parse_post(current_id)
        if not new_key:
            # Если поста нет или в нем нет ключа, проверяем еще 2 вперед (на случай пустых постов)
            gap_check = False
            for i in range(1, 3):
                if parse_post(current_id + i):
                    gap_check = True
                    break
            if not gap_check:
                break # Реально дошли до конца ленты
        
        if new_key:
            clean_url = new_key.split('#')[0]
            # Проверяем, нет ли такого ключа уже в файле
            if not any(clean_url in s for s in current_content):
                host = urlparse(clean_url).hostname
                proto = urlparse(clean_url).scheme.upper()
                flag = get_country_flag(host)
                emoji = random.choice(EMOJI_POOL)
                
                formatted_entry = f"{clean_url}#{flag} {proto} | Публичный Семаха {emoji}"
                current_content.append(formatted_entry)
                new_keys_found += 1
                print(f"Добавлен ключ из поста {current_id}")
        
        last_id = current_id
        current_id += 1
        if new_keys_found > 30: break # Ограничение за один проход, чтобы не вешать Action

    # 3. Сохраняем (БЕЗ удаления старых)
    if new_keys_found > 0:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HEADER + "\n".join(current_content))
            
        with open(ID_FILE, "w") as f:
            f.write(str(last_id))
        print(f"Обновление завершено. Добавлено {new_keys_found} новых серверов.")
    else:
        print("Новых ключей не обнаружено.")

if __name__ == "__main__":
    process()
