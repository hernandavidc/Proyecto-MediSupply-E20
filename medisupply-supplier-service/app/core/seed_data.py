from datetime import date
from app.models.catalogs import Pais, Certificacion, CategoriaSuministro
from app.models.vendedor import Vendedor
from app.models.proveedor import Proveedor
from app.models.product import Producto
from app.models.client import Cliente
from app.models.pedido import Pedido
from app.core.database import SessionLocal
from app.models.plan_venta import PlanVenta
from app.models.visita import Visita



def seed_data():
    db = SessionLocal()
    try:
        print("🚀 Iniciando carga de datos dummy...")

        # === PAISES ===
        if db.query(Pais).count() == 0:
            print("🌎 Insertando países...")
            paises = [
                Pais(nombre="Colombia"),
                Pais(nombre="México"),
                Pais(nombre="Perú"),
                Pais(nombre="Ecuador"),
            ]
            db.add_all(paises)
            db.commit()
            print("✅ Países creados.")

        # === CERTIFICACIONES ===
        if db.query(Certificacion).count() == 0:
            print("📜 Insertando certificaciones sanitarias...")
            db.add_all([
                Certificacion(codigo="INVIMA", nombre="Certificación INVIMA"),
                Certificacion(codigo="COFEPRIS", nombre="Certificación COFEPRIS"),
                Certificacion(codigo="FDA", nombre="Certificación FDA"),
                Certificacion(codigo="ISO13485", nombre="Certificación ISO 13485"),
            ])
            db.commit()
            print("✅ Certificaciones creadas.")

        # === CATEGORÍAS DE SUMINISTROS ===
        if db.query(CategoriaSuministro).count() == 0:
            print("📦 Insertando categorías de suministros...")
            db.add_all([
                CategoriaSuministro(nombre="Medicamentos"),
                CategoriaSuministro(nombre="Equipos Médicos"),
                CategoriaSuministro(nombre="Insumos Hospitalarios"),
                CategoriaSuministro(nombre="Reactivos y Pruebas"),
                CategoriaSuministro(nombre="Protección Personal"),
            ])
            db.commit()
            print("✅ Categorías creadas.")

        # === VENDEDORES ===
        if db.query(Vendedor).count() == 0:
            print("🧑‍💼 Insertando vendedores...")
            db.add_all([
                Vendedor(nombre="Juan Pérez", email="jp@example.com", pais_id=1),
                Vendedor(nombre="María Gómez", email="mg@example.com", pais_id=2),
                Vendedor(nombre="Carlos López", email="cl@example.com", pais_id=3),
                Vendedor(nombre="Ana Ramírez", email="ar@example.com", pais_id=4),
            ])
            db.commit()
            print("✅ Vendedores creados.")

        # === PROVEEDORES ===
        if db.query(Proveedor).count() == 0:
            print("🏢 Insertando proveedores...")
            db.add_all([
                Proveedor(
                    razon_social="Distribuidora Andina S.A.",
                    paises_operacion=[1, 3],
                    certificaciones_sanitarias=[1],
                    categorias_suministradas=[1, 3],
                    capacidad_cadena_frio=["2–8°C", "-20°C"],
                    estado="ACTIVO",
                    contacto_principal="Juan Pérez",
                    email_contacto="contacto@andina.com",
                    telefono_contacto="+57 301 123 4567",
                    tiene_productos_activos=True,
                    notas="Proveedor nacional especializado en medicamentos con cadena de frío.",
                    created_by=1
                ),
                Proveedor(
                    razon_social="Logística Azteca S.A. de C.V.",
                    paises_operacion=[2],
                    certificaciones_sanitarias=[2],
                    categorias_suministradas=[2, 5],
                    capacidad_cadena_frio=["Ambiente"],
                    estado="ACTIVO",
                    contacto_principal="María López",
                    email_contacto="ventas@logisticaazteca.mx",
                    telefono_contacto="+52 55 9876 5432",
                    tiene_productos_activos=False,
                    notas="Distribuidor regional de dispositivos médicos.",
                    created_by=1
                ),
            ])
            db.commit()
            print("✅ Proveedores creados.")

        # === PRODUCTOS ===
        if db.query(Producto).count() == 0:
            print("🧫 Insertando productos...")

            db.add_all([
                Producto(
                    sku="JER-ML-AAA",  # sin '0'
                    nombre_producto="Jeringas 10ml",
                    proveedor_id=1,
                    ficha_tecnica_url="https://example.com/jeringas10ml",
                    condiciones={
                        "temperatura": "15-25°C",
                        "humedad": "60%",
                        "luz": "baja",
                        "ventilacion": "moderada",
                        "seguridad": "normal",
                        "envase": "plástico sellado"
                    },
                    organizacion={
                        "tipo_medicamento": "Otros",
                        "fecha_vencimiento": "2026-12-31"  # ISO string OK para JSON
                    },
                    valor_unitario_usd=10.50,
                    certificaciones=[1],   # IDs válidos
                    tiempo_entrega_dias=5,
                    origen="MANUAL",
                ),
                Producto(
                    sku="GUA-QUIR-BBB",  # sin '0'
                    nombre_producto="Guantes quirúrgicos estériles",
                    proveedor_id=1,
                    ficha_tecnica_url="https://example.com/guantes",
                    condiciones={
                        "temperatura": "10-30°C",
                        "humedad": "70%",
                        "luz": "difusa",
                        "ventilacion": "moderada",
                        "seguridad": "alta",
                        "envase": "caja individual"
                    },
                    organizacion={
                        "tipo_medicamento": "Otros",
                        "fecha_vencimiento": "2026-08-15"
                    },
                    valor_unitario_usd=25.00,
                    certificaciones=[4],
                    tiempo_entrega_dias=7,
                    origen="MANUAL",
                ),
                Producto(
                    sku="MAS-NOV-CCC",  # sin '0'
                    nombre_producto="Mascarillas N95",
                    proveedor_id=2,
                    ficha_tecnica_url="https://example.com/mascarillas",
                    condiciones={
                        "temperatura": "Ambiente",
                        "humedad": "70%",
                        "luz": "normal",
                        "ventilacion": "buena",
                        "seguridad": "alta",
                        "envase": "bolsa sellada"
                    },
                    organizacion={
                        "tipo_medicamento": "Otros",
                        "fecha_vencimiento": "2027-01-01"
                    },
                    valor_unitario_usd=15.75,
                    certificaciones=[3],
                    tiempo_entrega_dias=10,
                    origen="MANUAL",
                ),
            ])
            db.commit()
            print("✅ Productos creados.")


        # === CLIENTES ===
        if db.query(Cliente).count() == 0:
            print("👥 Insertando clientes...")
            db.add_all([
                Cliente(
                    vendedor_id=1,
                    institucion_nombre="Hospital Central",
                    direccion="Cra 10 # 20-30",
                    contacto_principal="Dra. Pérez"
                ),
                Cliente(
                    vendedor_id=2,
                    institucion_nombre="Clínica Norte",
                    direccion="Av. Reforma 123",
                    contacto_principal="Dr. Gómez"
                ),
            ])
            db.commit()
            print("✅ Clientes creados.")

        # === PEDIDOS ===
        if db.query(Pedido).count() == 0:
            print("🧾 Insertando pedidos...")
            db.add_all([
                Pedido(
                    vendedor_id=1,
                    cliente_id=1,
                    producto_id=1,
                    fecha=date.today(),
                    cantidad=5,
                    valor_total_usd=52.5,
                    estado="ENTREGADO"
                ),
                Pedido(
                    vendedor_id=2,
                    cliente_id=2,
                    producto_id=3,
                    fecha=date.today(),
                    cantidad=10,
                    valor_total_usd=157.5,
                    estado="ENTREGADO"
                ),
            ])
            db.commit()
            print("✅ Pedidos creados.")

        # === PLANES DE VENTA ===
        if db.query(PlanVenta).count() == 0:
            print("🎯 Insertando planes de venta...")
            db.add_all([
                PlanVenta(
                    vendedor_id=1,
                    periodo="Q4",
                    anio=2025,
                    pais=1,
                    productos_objetivo=[1, 2],
                    meta_monetaria_usd=1000.00,
                    estado="CREADO",
                    created_by=1
                ),
                PlanVenta(
                    vendedor_id=2,
                    periodo="Q4",
                    anio=2025,
                    pais=2,
                    productos_objetivo=[3],
                    meta_monetaria_usd=1500.00,
                    estado="CREADO",
                    created_by=1
                ),
            ])
            db.commit()
            print("✅ Planes de venta creados.")

        print("🎯 Datos dummy cargados correctamente.")

        # === VISITAS (ejemplo) ===
        if db.query(Visita).count() == 0:
            print("📍 Insertando visitas de ejemplo...")
            from datetime import datetime, timedelta
            today = datetime.now()
            db.add_all([
                Visita(vendedor_id=1, cliente_id=1, direccion="Hospital Central", lat=4.710989, lon=-74.072090, scheduled_at=today.replace(hour=9, minute=0), duration_minutes=30),
                Visita(vendedor_id=1, cliente_id=1, direccion="Clínica Centro", lat=4.714, lon=-74.065, scheduled_at=today.replace(hour=10, minute=0), duration_minutes=20),
                Visita(vendedor_id=1, cliente_id=1, direccion="Centro Médico", lat=4.720, lon=-74.080, scheduled_at=today.replace(hour=11, minute=0), duration_minutes=25),
            ])
            db.commit()
            print("✅ Visitas de ejemplo creadas.")

    except Exception as e:
        import traceback
        print("❌ Error al cargar datos dummy:", e)
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
