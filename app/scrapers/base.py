from abc import ABC, abstractmethod
from typing import List, Dict
import re
from unidecode import unidecode

class BaseImovelScraper(ABC):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def clean_price(self, price: str) -> float:
        return float(re.sub(r'[^\d,]', '', price).replace(',', '.'))

    def extract_number(self, text: str) -> int:
        number = re.search(r'\d+', text or "0")
        return int(number.group()) if number else 0
    
    def clean_text(self, text: str) -> str:
        """Limpa e decodifica texto"""
        if not text:
            return ""
        text = unidecode(text)
        text = " ".join(text.split())
        return text

    @abstractmethod
    def scrape_imoveis(self, **kwargs) -> List[Dict]:
        pass