import requests
import re
import socket
from urllib.parse import urlparse, quote

#key sources (public)
SOURCES = [
    "https://raw.githubusercontent.com/Temnuk/naabuzil/main/whitelist_full",
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt"
]
OUTPUT_FILE = "scr.txt"

def get_country_flag(ip):
    try:
        #ip data
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        code = response.get("countryCode", "UN")
        #output display
        return "".join(chr(127397 + ord(c)) for c in code)
    except:
        return "🌐"

def check_ping(hostname, port):
    try:
        #does server response?
        socket.setdefaulttimeout(2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, port))
        s.close()
        return True
    except:
        return False

def process_keys():
    unique_keys = set()
    final_list = []

    for url in SOURCES:
        try:
            print(f"Загружаю: {url}")
            raw_data = requests.get(url).text
            #filter
            keys = re.findall(r'(vless|vmess|ss|trojan)://[^\s]+', raw_data)
            unique_keys.update(keys)
        except Exception as e:
            print(f"Ошибка при загрузке {url}: {e}")

    print(f"Найдено всего ключей: {len(unique_keys)}. Начинаю проверку...")

    for key in unique_keys:
        try:
            parsed = urlparse(key)
            host = parsed.hostname
            port = parsed.port or 443
            
            if host and check_ping(host, port):
                flag = get_country_flag(host)
                proto = parsed.scheme
                
                #output display 2
                base_part = key.split('#')[0]
                new_name = f"{flag} {proto.upper()} | Белый Семаха"
                final_list.append(f"{base_part}#{quote(new_name)}")
        except:
            continue

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_list))
    print(f"Готово! Сохранено рабочих ключей: {len(final_list)}")

if __name__ == "__main__":
    process_keys()
