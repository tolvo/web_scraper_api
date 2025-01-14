from pydantic import BaseModel, Field

class ImovelBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    tipo: str = Field(..., min_length=3, max_length=10)
    preco: float = Field(..., gt=0)
    cidade: str = Field(..., max_length=50)
    bairro: str = Field(..., max_length=50)
    num_quartos: int = Field(..., ge=0)
    num_vagas: int = Field(..., ge=0)
    num_banheiros: int = Field(..., ge=0)
    link: str = Field(..., max_length=500)

class ImovelCreate(ImovelBase):
    pass

class ImovelUpdate(BaseModel):
    titulo: str | None = None
    tipo: str | None = None
    preco: float | None = None
    cidade: str | None = None
    bairro: str | None = None
    rua: str | None = None
    numero: str | None = None
    cep: str | None = None
    num_quartos: int | None = None
    num_vagas: int | None = None
    link: str | None = None

class Imovel(ImovelBase):
    id: int

    class Config:
        from_attributes = True  # novo nome para orm_mode no Pydantic v2