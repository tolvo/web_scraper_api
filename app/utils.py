import os
import unicodedata
import re
import pandas as pd
from typing import List, Dict, Optional

def normalize_string(text: str) -> str:
    if not isinstance(text, str):
        return str(text).lower()
    
    # Normalizar texto
    normalized = unicodedata.normalize('NFKD', text)
    normalized = normalized.encode('ASCII', 'ignore').decode('ASCII')
    normalized = re.sub(r'[^a-zA-Z0-9\s]', '', normalized)
    normalized = ' '.join(normalized.split())
    return normalized.lower().strip()

def strings_match(str1: str, str2: str) -> bool:
    if not str1 or not str2:
        return False
    norm1 = normalize_string(str1)
    norm2 = normalize_string(str2)
    print(f"Comparing: {norm1} with {norm2}")
    return norm1 in norm2 or norm2 in norm1

def export_to_excel(data: List[Dict], filter_params: Optional[Dict] = None, output_dir: str = "exports/excel") -> str:
    if not data:
        raise ValueError("No data to export")
        
    if filter_params is None:
        filter_params = {}

    filtered_data = []
    for imovel in data:
        match = True
        for key, value in filter_params.items():
            imovel_value = imovel.get(key, '')
            if not strings_match(str(imovel_value), str(value)):
                match = False
                break
        if match:
            filtered_data.append(imovel)
    
    if not filtered_data:
        raise ValueError(f"No matches found for filters: {filter_params}")

    df = pd.DataFrame(filtered_data)
    
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)

    # Definir nome do arquivo
    nome_arquivo = "imoveis"
    if filter_params:
        partes = [f"{key}_{value.replace(' ', '_')}" for key, value in filter_params.items()]
        nome_arquivo += "_" + "_".join(partes)
    nome_arquivo += ".xlsx"

    # Caminho completo do arquivo
    caminho_arquivo = os.path.join(output_dir, nome_arquivo)

    # Exportar para Excel
    df.to_excel(caminho_arquivo, index=False, engine='openpyxl')

    # Retornar apenas o caminho do arquivo
    return caminho_arquivo