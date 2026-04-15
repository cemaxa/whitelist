import requests
import re
import base64
from urllib.parse import urlparse, quote, unquote

# Расширенный список источников
SOURCES = [
    "https://raw.githubusercontent.com/Temnuk/naabuzil/main/whitelist_full",
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt",
    "https://raw.githubusercontent.com/Epodonios/vless-subscription/main/vless_sub.txt",
    "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
]
OUTPUT_FILE = "scr.txt"

def get_country_flag(ip):
    try:
        # Быстрая проверка страны без лишних задержек
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=2).json()
        code = resp.get("countryCode", "UN")
        return "".join(chr(127397 + ord(c)) for c in code)
    except:
        return "🌐"

def safe_decode(data):
    """Декодирует base64, если данные в нем, иначе возвращает текст"""
    try:
        return base64.b64decode(data).decode('utf-8')
    except:
        return data

def process():
    all_raw_text = ""
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10)
            all_raw_text += "\n" + safe_decode(r.text)
        except:
            continue

    # Ищем все возможные протоколы
    found_keys = re.findall(r'(vless|vmess|ss|trojan)://[^\s]+', all_raw_text)
    unique_keys = list(set(found_keys))
    
    print(f"Найдено ключей: {len(unique_keys)}")
    
    processed_list = []
    for key in unique_keys:
        try:
            # Разделяем основную часть и старое название
            if "#" in key:
                base_part = key.split("#")[0]
            else:
                base_part = key
            
            # Извлекаем IP для флага
            parsed = urlparse(base_part)
            host = parsed.hostname
            
            # Если это vmess, там внутри json, пропустим сложную логику флага для них пока
            flag = get_country_flag(host) if host and not host.isdigit() else "📍"
            proto = parsed.scheme.upper()
            
            # Формируем новое название
            new_name = f"{flag} {proto} | Белый Семаха"
            processed_list.append(f"{base_part}#{quote(new_name)}")
        except:
            continue

    # Сохраняем результат (даже если пинг не проверяли, чтобы файл не был пустым)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(processed_list))
    
    print(f"Сохранено в {OUTPUT_FILE}: {len(processed_list)} шт.")

if __name__ == "__main__":
    process()
