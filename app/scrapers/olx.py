from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent
import re
import time
import json
from app.scrapers.base import BaseImovelScraper



class OLXScraper(BaseImovelScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.olx.com.br/imoveis"
        self.delay = random.uniform(5, 15)
        self.user_agent = UserAgent()
        #self.options = '--headless'

    def _get_chrome_options(self) -> Options:
        options = Options()
        options.add_argument(f'user-agent={self.user_agent.random}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return options

    def get_location_info(self, location_text: str) -> tuple:
        parts = location_text.split(',')
        if len(parts) >= 2:
            cidade = parts[0].strip()
            bairro = parts[1].strip().split('|')[0].strip()
            return bairro, cidade
        return "N/A", "N/A"

    def extract_details(self, card, tipo) -> Dict:
        try:
            details = card.select_one('.olx-ad-card__labels-items')
            if details:
                for item in details.find_all('li'):
                    span = item.find('span')
                    label = span['aria-label']
                    num = self.extract_number(label)
                    if 'quartos' in label:
                        num_quartos = num
                    elif 'metros quadrados' in label:
                        area = num
                    elif ('vaga' in label) or ('vagas' in label):
                        num_vagas = num
                    elif ('banheiro' in label) or ('banheiros' in label):
                        num_banheiros = num
            else:
                num_quartos = 0
                area = 0
                num_vagas = 0
                num_banheiros = 0

            price_element = card.select_one('.olx-ad-card__price')
            location_element = card.select_one('.olx-ad-card__location')

            price_text = price_element.get_text(strip=True) if price_element else "0"
            location_text = location_element.get_text(strip=True) if location_element else "N/A"

            bairro, cidade = self.get_location_info(location_text)
            bairro = self.clean_text(bairro)
            cidade = self.clean_text(cidade)
            titulo = self.clean_text(card.select_one('h2').text.strip())
            
            return {
                'titulo': titulo,
                'tipo': tipo,
                'preco': self.clean_price(price_text),
                'cidade': cidade,
                'bairro': bairro,
                'link': card.select_one('a')['href'],
                'num_quartos': num_quartos,
                'num_vagas': num_vagas,
                'num_banheiros': num_banheiros,
                'area': area
            }
        except Exception as e:
            print(f"Erro ao extrair detalhes do card: {e}")

    
    def scrape_imoveis(self, **kwargs) -> List[Dict]:
        tipo = kwargs.get('tipo')
        estado = kwargs.get('estado')
        start_page = kwargs.get('start_page', 1)
        max_pages = start_page + kwargs.get('max_pages', 3)

        #time.sleep(self.delay)

        results = []
        #for page in max_pages:
        def process_page(page_number: int) -> List[Dict]:
            url = f"{self.base_url}/{tipo}/estado-{estado}?lis=home_body_search_bar_1001&o={page_number}"
            
            print(f"[INFO] Starting scraping for {url}")
            options = self._get_chrome_options()
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            driver.execute_script("window.stop();")
            
            #driver.save_screenshot(f"page_{page_number}.png")
            print("[INFO] Get page source")
            page = driver.page_source
            driver.quit()

            if not page:
                print("[ERROR] Could not get page source")
                return []
            
            print("[INFO] Extracting data from page")
            soup = BeautifulSoup(page, 'html.parser')
            cards = soup.find_all('section', attrs={'data-ds-component': 'DS-AdCard'})
            print(f"[INFO] Found {len(cards)} cards")

            print("[INFO] Extracting data from cards")
            imoveis = []
            for card in cards:
                details = self.extract_details(card, tipo)
                if details:
                    #print(json.dumps(details, indent=2))
                    imoveis.append(details)
            print(f"[INFO] Finished scraping page {page_number}")
            return imoveis
        
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_page, page) for page in range(start_page, max_pages)]
            for future in futures:
                results.extend(future.result())
        print(results)
        return results

  
if __name__ == "__main__":
    scraper = OLXScraper()
    r = scraper.scrape_imoveis(tipo='venda', estado='sp', start_page=1, max_pages=10)
    print(r)
