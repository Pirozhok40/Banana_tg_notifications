import requests


def fetch_price(item_name: str) -> float | None:
    """Получает текущую цену предмета с рынка Steam"""
    url = f"https://steamcommunity.com/market/priceoverview/"
    params = {
        "country": "RU",
        "currency": 5,
        "appid": 2923300,  # Замените на ID вашей игры
        "market_hash_name": item_name
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"[DEBUG] Ответ Steam API для '{item_name}': {data}")
        return float(data["lowest_price"].replace(",", ".").replace(" руб.", ""))
    except (requests.RequestException, KeyError, ValueError):
        print(f"[DEBUG] Ошибка при получении цены для '{item_name}'.")
        return None