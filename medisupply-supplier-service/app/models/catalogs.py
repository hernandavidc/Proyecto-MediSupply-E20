from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Pais(Base):
    __tablename__ = "paises"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)


class Certificacion(Base):
    __tablename__ = "certificaciones"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, nullable=False)
    nombre = Column(String, nullable=False)


class CategoriaSuministro(Base):
    __tablename__ = "categorias_suministros"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
