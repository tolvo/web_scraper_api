from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app import models, schemas

def get_imoveis(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Imovel).offset(skip).limit(limit).all()

def create_imovel(db: Session, imovel: schemas.ImovelCreate):
    db_imovel = models.Imovel(**imovel.model_dump())
    db.add(db_imovel)
    db.commit()
    db.refresh(db_imovel)
    return db_imovel

def create_or_update_imovel(db: Session, imovel: schemas.ImovelCreate):
    existing = db.query(models.Imovel).filter(
        models.Imovel.cidade == imovel.cidade,
        models.Imovel.bairro == imovel.bairro,
        models.Imovel.titulo == imovel.titulo,
        models.Imovel.num_quartos == imovel.num_quartos,
        models.Imovel.num_vagas == imovel.num_vagas,
        models.Imovel.num_banheiros == imovel.num_banheiros,
        models.Imovel.tipo == imovel.tipo
    ).first()

    if existing:
        update_data = imovel.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        return create_imovel(db, imovel)

def get_imovel_by_id(db: Session, imovel_id: int):
    return db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()

def get_filtered_imoveis(db: Session, filter_params: Dict) -> List[models.Imovel]:
    query = db.query(models.Imovel)
    for key, value in filter_params.items():
        if hasattr(models.Imovel, key):
            if key in ['cidade', 'bairro', 'tipo']:
                query = query.filter(
                    func.lower(getattr(models.Imovel, key)).like(f'%{value.lower()}%')
                )
            else:
                query = query.filter(getattr(models.Imovel, key) == value)
    return query.all()

def update_imovel(db: Session, imovel_id: int, imovel: schemas.ImovelUpdate):
    db_imovel = get_imovel_by_id(db, imovel_id)
    if db_imovel:
        update_data = imovel.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_imovel, key, value)
        db.commit()
        db.refresh(db_imovel)
    return db_imovel

def delete_all_imoveis(db: Session):
    db.query(models.Imovel).delete()
    db.commit()
    return True

def delete_imovel(db: Session, imovel_id: int):
    db_imovel = get_imovel_by_id(db, imovel_id)
    if db_imovel:
        db.delete(db_imovel)
        db.commit()
        return True
    return False

def search_imoveis(
    db: Session, 
    cidade: str = None, 
    bairro: str = None, 
    preco_min: float = None, 
    preco_max: float = None
):
    query = db.query(models.Imovel)
    if cidade:
        query = query.filter(models.Imovel.cidade == cidade)
    if bairro:
        query = query.filter(models.Imovel.bairro == bairro)
    if preco_min:
        query = query.filter(models.Imovel.preco >= preco_min)
    if preco_max:
        query = query.filter(models.Imovel.preco <= preco_max)
    return query.all()

def get_total_imoveis(db: Session):
    return db.query(models.Imovel).count()
