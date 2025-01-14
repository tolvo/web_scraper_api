import requests
import time

tipo = input("tipo: ") or "venda"
pages = input("pages: ") or 1000
state = input("state: ") or "sp"

print(f"Scraping {pages} pages of {tipo} in {state}")

for i in range(1, int(pages)):
    url = f"http://127.0.0.1:8000/scrape/olx?tipo={tipo}&estado={state}&start_page={i}&max_pages=1"
    response = requests.post(url)
    print(response.status_code)
    time.sleep(30)