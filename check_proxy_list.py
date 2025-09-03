import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os

# Файл для хранения актуальных прокси
DEFAULT_DIR_PROXY = os.getenv("DIR_PROXIES", "/data")
WORKING_PROXIES_FILE = os.path.join(DEFAULT_DIR_PROXY, "working_proxies.json")


def get_proxies_from_free_proxy_list():
    """Получает список прокси с сайта free-proxy-list.net."""
    url = "https://free-proxy-list.net/"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "table-striped"})
        proxies = []
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) > 6:
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                https = cols[6].text.strip().lower() == "yes"
                if not https:
                    continue
                proxy = {
                    "http": f"http://{ip}:{port}",
                    "https": f"http://{ip}:{port}" if https else None,
                }
                proxies.append(proxy)
        return proxies
    except Exception as e:
        print(f"Failed to fetch proxies from free-proxy-list.net: {e}")
        return []


def load_known_proxies():
    """Загружает список известных прокси из файла."""
    if not os.path.exists(WORKING_PROXIES_FILE):
        return []
    with open(WORKING_PROXIES_FILE, "r") as f:
        return json.load(f)


def save_working_proxies(proxies):
    """Сохраняет список рабочих прокси в файл."""
    with open(WORKING_PROXIES_FILE, "w") as f:
        json.dump(proxies, f, indent=4)


def get_real_ip() -> str | None:
    url = "http://httpbin.org/ip"

    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        proxy_ip = response.json().get("origin", "")
        return proxy_ip
    return None


def test_proxy(proxy, real_ip):
    """Проверяет работоспособность прокси и скрытие IP."""
    test_urls = {
        "http": "http://httpbin.org/ip",
        "https": "https://httpbin.org/ip",
    }
    results = {}

    for protocol, url in test_urls.items():
        if proxy.get(protocol):
            try:
                response = requests.get(url, proxies={protocol: proxy[protocol]}, timeout=10)
                if response.status_code == 200:
                    proxy_ip = response.json().get("origin", "")
                    print('proxy ip:', proxy_ip, ' === ', proxy)
                    hides_ip = proxy_ip != real_ip
                    results[protocol] = {
                        "status": "success",
                        "ip": proxy_ip,
                        "proxy_ip": proxy_ip,
                        "hides_ip": hides_ip,
                    }
                else:
                    results[protocol] = {"status": "failure", "reason": "non-200 status code"}
            except Exception as e:
                results[protocol] = {"status": "failure", "reason": str(e)}

            time.sleep(random.uniform(1, 3))
        else:
            results[protocol] = {"status": "skipped", "reason": "protocol not supported"}

    # Прокси считается рабочим, если оба протокола работают
    is_working = all(
        result["status"] == "success" and result["hides_ip"]
        for result in results.values()
        if result["status"] != "skipped"
    )
    return is_working, results


def main():
    # Шаг 1: Получить список прокси с общедоступных сайтов
    print("Fetching proxies from free-proxy-list.net...")
    proxies = get_proxies_from_free_proxy_list()
    #proxies = []

    # Шаг 2: Добавить известные прокси из файла
    print("Loading known proxies...")
    known_proxies = load_known_proxies()
    proxies.extend(known_proxies)

    # Уникализация прокси
    unique_proxies = []
    seen = set()
    for proxy in proxies:
        key = (proxy.get("http"), proxy.get("https"))
        if key not in seen:
            seen.add(key)
            unique_proxies.append(proxy)

    real_ip = get_real_ip()
    if not real_ip is None:

        # Шаг 3: Проверить каждый прокси
        print(f"Testing {len(unique_proxies)} proxies...")
        working_proxies = []
        for proxy in unique_proxies:
            print(f"Testing proxy: {proxy}")
            is_working, results = test_proxy(proxy, real_ip)
            if is_working:
                print(f"Proxy works and hides IP: {proxy}")
                working_proxies.append(proxy)
                save_working_proxies(working_proxies)
            else:
                print(f"Proxy failed: {results}")

        # Шаг 4: Сохранить рабочие прокси в файл
        print(f"Saving {len(working_proxies)} working proxies to file...")
        save_working_proxies(working_proxies)

        print("Done!")


if __name__ == "__main__":
    main()
