import requests, re, base64, random, time
from urllib.parse import urlparse

# Основной и единственный источник качества
CHANNEL = "outlineOpenKey"
OUTPUT_FILE = "public_scr.txt"

#output header
HEADER = "# profile-title: 🔮 Публичный Семаха\n\n"
EMOJI_POOL = ["🔮", "🌑", "👾", "🎊", "✨", "🎉", "🎀", "🪄", "🪬", "💣", "🍖", "⚡", "🔥", "🌠"]

def get_country_flag(ip, cache):
    if ip in cache: return cache[ip]
    try:
        # Небольшая задержка для стабильности API
        time.sleep(1.1)
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=status,countryCode", timeout=5).json()
        if resp.get('status') == 'success':
            code = resp.get('countryCode', 'UN')
            flag = "".join(chr(127397 + ord(c)) for c in code)
            cache[ip] = flag
            return flag
    except: pass
    return "🌐"

def process():
    try:
        # Парсим веб-версию канала
        url = f"https://t.me/s/{CHANNEL}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=15)
        
        # Находим все ключи vless, vmess, ss
        found_keys = re.findall(r'(?:vless|vmess|ss)://[^\s<"\'&|]+', r.text)
        
        # Переворачиваем, чтобы последние (самые свежие из ТГ) стали первыми в списке
        found_keys.reverse()
        
        # Убираем дубликаты, сохраняя порядок
        seen = set()
        final_raw_keys = []
        for k in found_keys:
            clean_base = k.split('#')[0]
            if clean_base not in seen:
                final_raw_keys.append(k)
                seen.add(clean_base)
        
        # Берем ровно 10 последних
        top_10 = final_raw_keys[:10]
        
        final_lines = []
        cache = {}
        
        print(f"Обрабатываю {len(top_10)} свежих ключей из @{CHANNEL}...")

        for key in top_10:
            try:
                clean_url = key.split('#')[0]
                parsed = urlparse(clean_url)
                host = parsed.hostname
                proto = parsed.scheme.upper()
                
                if not host: continue
                
                # Получаем флаг и выбираем случайное эмодзи
                flag = get_country_flag(host, cache)
                emoji = random.choice(EMOJI_POOL)
                
                # Формат: [Флаг] [Протокол] | Публичный Семаха [Эмодзи]
                name = f"{flag} {proto} | Публичный Семаха {emoji}"
                final_lines.append(f"{clean_url}#{name}")
            except: continue

        # Запись в файл
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(HEADER + "\n".join(final_lines))
            
        print(f"Готово! В файл записано {len(final_lines)} серверов.")

    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    process()
