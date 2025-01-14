from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Imovel(Base):
    __tablename__ = "imoveis"

    id = Column(Integer, primary_key=True)
    titulo = Column(String)
    tipo = Column(String, index=True)
    preco = Column(Float)
    cidade = Column(String, index=True)
    bairro = Column(String, index=True)
    num_quartos = Column(Integer)
    num_vagas = Column(Integer)
    num_banheiros = Column(Integer)
    link = Column(String)

    def __repr__(self):
        return f"<Imovel(cidade={self.cidade}, bairro={self.bairro}, preco={self.preco}, link={self.link})>"
    