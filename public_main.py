import requests, re, random, time, os
from urllib.parse import urlparse

CHANNEL = "outlineOpenKey"
ID_FILE = "last_id.txt"
OUTPUT_FILE = "public_scr.txt"
HEADER = "# profile-title: 🔮 Публичный Семаха\n\n"
EMOJI_POOL = ["🔮", "🌑", "👾", "🎊", "✨", "🎉", "🎀", "🪄", "🪬", "💣", "🍖", "⚡", "🔥", "🌠"]

def get_country_flag(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=countryCode", timeout=5).json()
        if resp.status_code == 200:
            code = resp.json().get('countryCode', 'UN')
            return "".join(chr(127397 + ord(c)) for c in code)
    except: pass
    return "🌐"

def parse_post(post_id):
    """Проверяет пост и вытаскивает ключ"""
    try:
        url = f"https://t.me/{CHANNEL}/{post_id}?embed=1"
        # Добавляем рандомный параметр к URL, чтобы не ловить кэш телеграма
        r = requests.get(f"{url}&nocache={random.randint(1,1000)}", timeout=10)
        if r.status_code != 200: return None
        # Ищем ключи
        found = re.findall(r'(?:vless|vmess|ss)://[^\s<"\'&|]+', r.text)
        return found[0] if found else None
    except: return None

def process():
    # 1. Загружаем ID. Если файла нет - берем твой актуальный
    if os.path.exists(ID_FILE):
        with open(ID_FILE, "r") as f:
            last_id = int(f.read().strip())
    else:
        last_id = 7689 

    # 2. Загружаем текущий список
    current_content = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            current_content = [l.strip() for l in f.readlines() if "://" in l]

    new_keys_found = 0
    current_id = last_id + 1
    empty_streak = 0 # Счетчик пустых постов подряд
    
    print(f"Старт проверки. Последний успешный ID: {last_id}")

    # Идем по ленте, пока не встретим 10 пустых постов подряд (конец ленты)
    while empty_streak < 10:
        new_key = parse_post(current_id)
        
        if new_key:
            clean_url = new_key.split('#')[0]
            # Проверяем на дубликаты
            if not any(clean_url in s for s in current_content):
                host = urlparse(clean_url).hostname
                proto = urlparse(clean_url).scheme.upper()
                flag = get_country_flag(host)
                emoji = random.choice(EMOJI_POOL)
                
                formatted_entry = f"{clean_url}#{flag} {proto} | Публичный Семаха {emoji}"
                current_content.append(formatted_entry)
                new_keys_found += 1
                print(f"[+] НАЙДЕН КЛЮЧ в посте {current_id}")
            
            last_id = current_id # Запоминаем ID только если нашли ключ или пост существует
            empty_streak = 0 
        else:
            # Если ключа нет, проверяем просто наличие поста (вдруг там текст)
            # Если пост совсем не отдается 404 - это точно конец
            empty_streak += 1
            if empty_streak % 5 == 0:
                print(f"Проверено {current_id}, ключей пока нет...")

        current_id += 1
        if new_keys_found >= 10: break # Не берем слишком много за раз

    # 3. Финальный срез (строго 10 последних)
    if len(current_content) > 10:
        current_content = current_content[-10:]

    # 4. Сохранение
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(current_content))
            
    with open(ID_FILE, "w") as f:
        f.write(str(last_id))
        
    print(f"Итог: добавлено {new_keys_found}. Файл обновлен до поста {last_id}.")

if __name__ == "__main__":
    process()
