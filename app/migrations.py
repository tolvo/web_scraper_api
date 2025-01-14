from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
#from app.database import SQLALCHEMY_DATABASE_URL

engine = create_engine("sqlite:///./imoveis.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_tipo_column():
    with engine.connect() as connection:
        connection.execute(text("ALTER TABLE imoveis ADD COLUMN tipo STRING"))

if __name__ == "__main__":
    add_tipo_column()