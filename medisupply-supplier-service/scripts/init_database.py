#!/usr/bin/env python3
"""
Script de inicialización de datos base para MediSupply Supplier Service
Se ejecuta automáticamente en cada deploy para poblar la base de datos con datos necesarios.
"""

import sys
import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, create_tables
from app.models.catalogs import Pais, Certificacion, CategoriaSuministro
from app.models.proveedor import Proveedor
from app.models.vendedor import Vendedor
from app.models.product import Producto
from app.models.plan_venta import PlanVenta

def init_database():
    """Inicializa la base de datos con datos base necesarios"""
    print("🚀 Iniciando inicialización de base de datos...")
    
    # Crear tablas
    create_tables()
    print("✅ Tablas creadas/verificadas")
    
    db = SessionLocal()
    try:
        # 1. Inicializar catálogos base
        init_catalogs(db)
        
        # 2. Crear proveedores de ejemplo
        init_proveedores(db)
        
        # 3. Crear vendedores de ejemplo
        init_vendedores(db)
        
        # 4. Crear productos de ejemplo
        init_productos_ejemplo(db)
        
        db.commit()
        print("✅ Inicialización completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_catalogs(db: Session):
    """Inicializa los catálogos base"""
    print("📋 Inicializando catálogos...")
    
    # Países
    if db.query(Pais).count() == 0:
        paises = [
            Pais(id=1, nombre='Colombia'),
            Pais(id=2, nombre='Perú'),
            Pais(id=3, nombre='Ecuador'),
            Pais(id=4, nombre='México'),
            Pais(id=5, nombre='Chile'),
            Pais(id=6, nombre='Argentina'),
            Pais(id=7, nombre='Brasil'),
        ]
        db.add_all(paises)
        print("✅ Países creados")
    else:
        print("ℹ️ Países ya existen")
    
    # Certificaciones sanitarias
    if db.query(Certificacion).count() == 0:
        certificaciones = [
            Certificacion(id=1, codigo='FDA', nombre='FDA (Food and Drug Administration)'),
            Certificacion(id=2, codigo='EMA', nombre='EMA (European Medicines Agency)'),
            Certificacion(id=3, codigo='INVIMA', nombre='INVIMA (Instituto Nacional de Vigilancia de Medicamentos y Alimentos)'),
            Certificacion(id=4, codigo='DIGEMID', nombre='DIGEMID (Dirección General de Medicamentos, Insumos y Drogas)'),
            Certificacion(id=5, codigo='COFEPRIS', nombre='COFEPRIS (Comisión Federal para la Protección contra Riesgos Sanitarios)'),
            Certificacion(id=6, codigo='ANVISA', nombre='ANVISA (Agência Nacional de Vigilância Sanitária)'),
            Certificacion(id=7, codigo='ISP', nombre='ISP (Instituto de Salud Pública de Chile)'),
        ]
        db.add_all(certificaciones)
        print("✅ Certificaciones creadas")
    else:
        print("ℹ️ Certificaciones ya existen")
    
    # Categorías de suministro
    if db.query(CategoriaSuministro).count() == 0:
        categorias = [
            CategoriaSuministro(id=1, nombre='Medicamentos especiales'),
            CategoriaSuministro(id=2, nombre='Medicamentos controlados'),
            CategoriaSuministro(id=3, nombre='Insumos quirúrgicos y hospitalarios'),
            CategoriaSuministro(id=4, nombre='Insumos reactivos'),
            CategoriaSuministro(id=5, nombre='Pruebas diagnósticas'),
            CategoriaSuministro(id=6, nombre='Equipos y dispositivos biomédicos'),
            CategoriaSuministro(id=7, nombre='Otros (PPE, Materiales varios)'),
        ]
        db.add_all(categorias)
        print("✅ Categorías de suministro creadas")
    else:
        print("ℹ️ Categorías de suministro ya existen")

def init_proveedores(db: Session):
    """Crea proveedores de ejemplo"""
    print("🏥 Inicializando proveedores...")
    
    if db.query(Proveedor).count() == 0:
        proveedores = [
            Proveedor(
                razon_social="Farmacéutica Internacional S.A.S",
                paises_operacion=[1, 2, 3],  # Colombia, Perú, Ecuador
                certificaciones_sanitarias=[1, 2, 3],  # FDA, EMA, INVIMA
                categorias_suministradas=[1, 2],  # Medicamentos especiales y controlados
                capacidad_cadena_frio=True,
                estado="APROBADO"
            ),
            Proveedor(
                razon_social="MedSupply Global Ltda",
                paises_operacion=[1, 4, 5],  # Colombia, México, Chile
                certificaciones_sanitarias=[2, 4, 5],  # EMA, DIGEMID, COFEPRIS
                categorias_suministradas=[3, 4],  # Insumos quirúrgicos y reactivos
                capacidad_cadena_frio=False,
                estado="APROBADO"
            ),
            Proveedor(
                razon_social="BioMedical Solutions Inc",
                paises_operacion=[1, 6, 7],  # Colombia, Argentina, Brasil
                certificaciones_sanitarias=[1, 6, 7],  # FDA, ANVISA, ISP
                categorias_suministradas=[5, 6],  # Pruebas diagnósticas y equipos
                capacidad_cadena_frio=True,
                estado="APROBADO"
            ),
            Proveedor(
                razon_social="PharmaTech Colombia",
                paises_operacion=[1],  # Solo Colombia
                certificaciones_sanitarias=[3],  # Solo INVIMA
                categorias_suministradas=[1, 7],  # Medicamentos especiales y otros
                capacidad_cadena_frio=False,
                estado="PENDIENTE"
            ),
            Proveedor(
                razon_social="Global Health Supplies",
                paises_operacion=[1, 2, 3, 4, 5],  # Múltiples países
                certificaciones_sanitarias=[1, 2, 3, 4, 5],  # Múltiples certificaciones
                categorias_suministradas=[1, 2, 3, 4, 5, 6, 7],  # Todas las categorías
                capacidad_cadena_frio=True,
                estado="APROBADO"
            )
        ]
        db.add_all(proveedores)
        print("✅ Proveedores creados")
    else:
        print("ℹ️ Proveedores ya existen")

def init_vendedores(db: Session):
    """Crea vendedores de ejemplo"""
    print("👥 Inicializando vendedores...")
    
    if db.query(Vendedor).count() == 0:
        vendedores = [
            Vendedor(
                nombre="María González",
                email="maria.gonzalez@medisupply.com",
                pais=1,  # Colombia
                estado="ACTIVO"
            ),
            Vendedor(
                nombre="Carlos Rodríguez",
                email="carlos.rodriguez@medisupply.com",
                pais=1,  # Colombia
                estado="ACTIVO"
            ),
            Vendedor(
                nombre="Ana Martínez",
                email="ana.martinez@medisupply.com",
                pais=2,  # Perú
                estado="ACTIVO"
            ),
            Vendedor(
                nombre="Luis Fernández",
                email="luis.fernandez@medisupply.com",
                pais=3,  # Ecuador
                estado="ACTIVO"
            ),
            Vendedor(
                nombre="Sofia Herrera",
                email="sofia.herrera@medisupply.com",
                pais=4,  # México
                estado="ACTIVO"
            )
        ]
        db.add_all(vendedores)
        print("✅ Vendedores creados")
    else:
        print("ℹ️ Vendedores ya existen")

def init_productos_ejemplo(db: Session):
    """Crea algunos productos de ejemplo"""
    print("💊 Inicializando productos de ejemplo...")
    
    if db.query(Producto).count() == 0:
        # Obtener el primer proveedor aprobado
        proveedor = db.query(Proveedor).filter(Proveedor.estado == "APROBADO").first()
        
        if proveedor:
            productos = [
                Producto(
                    sku="MED001",
                    nombre_producto="Paracetamol 500mg",
                    proveedor_id=proveedor.id,
                    ficha_tecnica_url="https://ejemplo.com/ficha-paracetamol.pdf",
                    condiciones={
                        "temperatura": "15-25°C",
                        "humedad": "40-60%",
                        "luz": "Ambiente normal",
                        "ventilacion": "Ventilación normal",
                        "seguridad": "Estándar",
                        "envase": "Envase original"
                    },
                    organizacion={
                        "tipo_medicamento": "Analgésicos",
                        "fecha_vencimiento": "2025-12-31"
                    },
                    tipo_medicamento="Analgésicos",
                    fecha_vencimiento="2025-12-31",
                    valor_unitario_usd=15.50,
                    certificaciones=[1, 2],
                    tiempo_entrega_dias=7,
                    origen="INIT_SCRIPT"
                ),
                Producto(
                    sku="MED002",
                    nombre_producto="Ibuprofeno 400mg",
                    proveedor_id=proveedor.id,
                    ficha_tecnica_url="https://ejemplo.com/ficha-ibuprofeno.pdf",
                    condiciones={
                        "temperatura": "15-25°C",
                        "humedad": "40-60%",
                        "luz": "Ambiente normal",
                        "ventilacion": "Ventilación normal",
                        "seguridad": "Estándar",
                        "envase": "Envase original"
                    },
                    organizacion={
                        "tipo_medicamento": "Antiinflamatorios",
                        "fecha_vencimiento": "2025-10-15"
                    },
                    tipo_medicamento="Antiinflamatorios",
                    fecha_vencimiento="2025-10-15",
                    valor_unitario_usd=18.75,
                    certificaciones=[1, 3],
                    tiempo_entrega_dias=5,
                    origen="INIT_SCRIPT"
                )
            ]
            db.add_all(productos)
            print("✅ Productos de ejemplo creados")
        else:
            print("⚠️ No se encontraron proveedores aprobados para crear productos")
    else:
        print("ℹ️ Productos ya existen")

def main():
    """Función principal"""
    try:
        init_database()
        print("\n🎉 ¡Inicialización de base de datos completada exitosamente!")
        print("📊 Datos creados:")
        print("   - Catálogos base (países, certificaciones, categorías)")
        print("   - Proveedores de ejemplo")
        print("   - Vendedores de ejemplo")
        print("   - Productos de ejemplo")
        print("\n🚀 El servicio está listo para usar")
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
