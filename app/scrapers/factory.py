from typing import Dict, Type
from app.scrapers.base import BaseImovelScraper
from app.scrapers.olx import OLXScraper

class ScraperFactory:
    _scrapers: Dict[str, Type[BaseImovelScraper]] = {
        'olx': OLXScraper,
    }

    @classmethod
    def get_scraper(cls, source: str) -> BaseImovelScraper:
        scraper_class = cls._scrapers.get(source.lower())
        if not scraper_class:
            raise ValueError(f"Scraper não encontrado para: {source}")
        return scraper_class()