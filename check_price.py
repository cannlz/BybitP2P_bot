import requests

def get_bybit_price():
    url = f"https://api.bybit.com/v2/public/tickers?symbol=BTCUSDT"
    response = requests.get(url)
    data = response.json()
    if data["ret_code"] == 0:
        return data["result"][0]["last_price"]
    else:
        return None

def get_price(user_rub_course):
    price = get_bybit_price()
    if price is not None:
        answer = float(user_rub_course) * float(price)
        print
        return (f'{answer:,.2f} Руб.'.replace(',', ' '))
    else:
        return (f"Не удалось получить курс")