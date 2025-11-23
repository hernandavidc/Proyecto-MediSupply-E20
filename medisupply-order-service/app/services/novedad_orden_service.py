from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.novedad_orden import NovedadOrden
from app.schemas.novedad_orden_schema import NovedadOrdenCreate, NovedadOrdenUpdate
import json
import os
import shutil
from pathlib import Path
from fastapi import UploadFile
import uuid


class NovedadOrdenService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path("uploads/novedades")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def crear_novedad(self, data: NovedadOrdenCreate, fotos: Optional[List[UploadFile]] = None) -> NovedadOrden:
        novedad = NovedadOrden(**data.model_dump())
        
        # Guardar fotos si existen
        if fotos:
            foto_urls = self._guardar_fotos(fotos)
            novedad.fotos = json.dumps(foto_urls)
        
        self.db.add(novedad)
        self.db.commit()
        self.db.refresh(novedad)
        return novedad
    
    def _guardar_fotos(self, fotos: List[UploadFile]) -> List[str]:
        """Guarda las fotos en el sistema de archivos y retorna las URLs"""
        foto_urls = []
        
        for foto in fotos:
            # Validar que sea una imagen
            if not foto.content_type or not foto.content_type.startswith('image/'):
                continue
            
            # Generar nombre único para el archivo
            file_extension = os.path.splitext(foto.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = self.upload_dir / unique_filename
            
            # Guardar el archivo
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(foto.file, buffer)
            
            # Agregar la URL relativa
            foto_urls.append(f"/uploads/novedades/{unique_filename}")
        
        return foto_urls

    def listar_novedades(self, skip: int = 0, limit: int = 100) -> List[NovedadOrden]:
        return self.db.query(NovedadOrden).offset(skip).limit(limit).all()

    def listar_por_orden(self, orden_id: int) -> List[NovedadOrden]:
        return self.db.query(NovedadOrden).filter(NovedadOrden.id_pedido == orden_id).all()

    def obtener_novedad(self, novedad_id: int) -> Optional[NovedadOrden]:
        return self.db.query(NovedadOrden).filter(NovedadOrden.id == novedad_id).first()

    def actualizar_novedad(self, novedad_id: int, data: NovedadOrdenUpdate) -> Optional[NovedadOrden]:
        novedad = self.obtener_novedad(novedad_id)
        if not novedad:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(novedad, key, value)
        
        self.db.commit()
        self.db.refresh(novedad)
        return novedad

    def eliminar_novedad(self, novedad_id: int) -> bool:
        novedad = self.obtener_novedad(novedad_id)
        if not novedad:
            return False
        
        self.db.delete(novedad)
        self.db.commit()
        return True
