import os
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, APIRouter, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app import crud, models, schemas, database, utils
from app.scrapers.factory import ScraperFactory
import logging

models.Base.metadata.create_all(bind=database.engine)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de busca de imóveis",
    description="API para cadastro e busca de imóveis",
    version="1.0.0"
)

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/imoveis/", response_model=schemas.Imovel, include_in_schema=False)
def create_imovel(imovel: schemas.ImovelCreate, db: Session = Depends(get_db)):
    return crud.create_imovel(db=db, imovel=imovel)

@app.get("/imoveis/total", response_model=int)
def total_imoveis(db: Session = Depends(get_db)):
    return crud.get_total_imoveis(db)

@app.get("/imoveis/", response_model=list[schemas.Imovel])
def read_imoveis(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    imoveis = crud.get_imoveis(db=db, skip=skip, limit=limit)
    return imoveis

@app.get("/imoveis/{imovel_id}", response_model=schemas.Imovel)
def read_imovel(imovel_id: int, db: Session = Depends(get_db)):
    imovel = crud.get_imovel_by_id(db, imovel_id)
    if imovel is None:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    return imovel

@app.put("/imoveis/{imovel_id}", response_model=schemas.Imovel,include_in_schema=False)
def update_imovel(imovel_id: int, imovel: schemas.ImovelUpdate, db: Session = Depends(get_db)):
    db_imovel = crud.update_imovel(db, imovel_id, imovel)
    if db_imovel is None:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    return db_imovel

@app.delete("/imoveis/{imovel_id}", include_in_schema=False)
def delete_imovel(imovel_id: int, db: Session = Depends(get_db)):
    success = crud.delete_imovel(db, imovel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    return {"message": "Imóvel deletado com sucesso"}

@app.delete("/imoveis/", include_in_schema=False)
def delete_all_imoveis(db: Session = Depends(get_db)):
    success = crud.delete_all_imoveis(db)
    if not success:
        raise HTTPException(status_code=404, detail="Nenhum imóvel encontrado")
    return {"message": "Todos os imóveis foram deletados"}

@app.post("/scrape/{source}", response_model=dict, include_in_schema=False)
async def scrape_and_save(
    source: str,
    tipo: str,
    estado: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    start_page: int = 1,
    max_pages: int = 10
):
    """
    Endpoint para iniciar o scraping e salvar os resultados no banco de dados.

    - **source**: Fonte do scraping (ex: 'olx')
    - **tipo**: Tipo de imóvel (ex: 'venda', 'aluguel')
    - **estado**: Estado do imóvel (ex: 'sp')
    - **start_page**: Página inicial para iniciar o scraping
    - **max_pages**: Número máximo de páginas para scraping
    """
    def process_scraping():
        try:
            scraper = ScraperFactory.get_scraper(source)
            imoveis = scraper.scrape_imoveis(tipo=tipo, estado=estado, start_page=start_page, max_pages=max_pages)
            for imovel in imoveis:
                try:
                    crud.create_or_update_imovel(db=db, imovel=schemas.ImovelCreate(**imovel))
                except Exception as e:
                    logger.exception(f"Erro ao salvar imóvel: {e}")
        except Exception as e:
            logger.exception(f"Erro ao processar scraping: {e}")

    background_tasks.add_task(process_scraping)
    return {"message": "Scraping iniciado em background"}

@app.post("/export/excel", response_model=dict)
def export_imoveis_to_excel(
    cidade: Optional[str] = Query(None, description="Cidade dos imóveis."),
    bairro: Optional[str] = Query(None, description="Bairro dos imóveis."),
    tipo: Optional[str] = Query(None, description="Tipo de imóvel (ex: 'venda', 'aluguel')."),
    db: Session = Depends(database.get_db)
):
    """
    Endpoint para exportar dados de imóveis para um arquivo Excel com base em filtros.

    - **cidade**: (Opcional) Cidade dos imóveis.
    - **bairro**: (Opcional) Bairro dos imóveis.
    - **tipo**: (Opcional) Tipo de imóvel (ex: 'venda', 'aluguel').
    """
    # Definir os parâmetros de filtro
    filter_params = {}
    if cidade:
        filter_params['cidade'] = utils.normalize_string(cidade)
    if bairro:
        filter_params['bairro'] = utils.normalize_string(bairro)
    if tipo:
        filter_params['tipo'] = utils.normalize_string(tipo)

    # Obter os imóveis filtrados do banco de dados
    imoveis = crud.get_filtered_imoveis(db, filter_params)

    if not imoveis:
        raise HTTPException(status_code=404, detail="Nenhum imóvel encontrado com os filtros fornecidos.")

    # Exportar para Excel
    try:
        resultado = utils.export_to_excel(
            data=[{k: v for k, v in imovel.__dict__.items() if not k.startswith('_')} 
                for imovel in imoveis],
            filter_params=filter_params
        )
        return FileResponse(
            path=resultado,
            filename=os.path.basename(resultado),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
