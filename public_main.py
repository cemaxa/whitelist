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
        code = resp.get('countryCode', 'UN')
        return "".join(chr(127397 + ord(c)) for c in code)
    except: return "🌐"

def parse_post(post_id):
    """Проверяет пост по ID и ищет в нем ключ"""
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
        last_id = 7689 # here we started

    # 2. Проверяем следующий пост
    next_id = last_id + 1
    new_key = parse_post(next_id)

    if not new_key:
        print(f"Нового ключа в посте {next_id} пока нет. Ждем.")
        return

    print(f"Нашел новый ключ в посте {next_id}!")

    # 3. Читаем текущий список серверов
    current_servers = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Пропускаем заголовок и берем только строки с ключами
            current_servers = [l.strip() for l in lines if "://" in l]

    # 4. Формируем новый сервер
    try:
        clean_url = new_key.split('#')[0]
        host = urlparse(clean_url).hostname
        proto = urlparse(clean_url).scheme.upper()
        flag = get_country_flag(host)
        emoji = random.choice(EMOJI_POOL)
        formatted_entry = f"{clean_url}#{flag} {proto} | Публичный Семаха {emoji}"
        
        # Добавляем новый, удаляем самый старый (первый), если их уже 10
        current_servers.append(formatted_entry)
        if len(current_servers) > 10:
            current_servers.pop(0)
            
        # 5. Сохраняем результаты
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HEADER + "\n".join(current_servers))
            
        with open(ID_FILE, "w") as f:
            f.write(str(next_id))
            
        print(f"Список обновлен. Теперь последний ID: {next_id}")
    except Exception as e:
        print(f"Ошибка при обработке: {e}")

if __name__ == "__main__":
    process()
