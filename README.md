# API de Busca de Imóveis

API para scraping e busca de imóveis da OLX, com exportação para Excel.

## Funcionalidades

- Scraping de imóveis da OLX
- Filtros por cidade, bairro e tipo
- Exportação para Excel
- API RESTful com documentação Swagger

## Requisitos

- Python 3.13+
- Chrome/Chromium
- ChromeDriver

## Instalação

```bash
# Criar ambiente virtual
python -m venv env

# Ativar ambiente
source env/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
uvicorn app.main:app --reload

# Automação mineradora de dados
python app/minerador.py
```