from datetime import datetime, timedelta
from app.models.bodega import Bodega
from app.models.bodega_producto import BodegaProducto
from app.models.vehiculo import Vehiculo, TipoVehiculo
from app.models.orden import Orden, EstadoOrden
from app.models.orden_producto import OrdenProducto
from app.models.novedad_orden import NovedadOrden, TipoNovedad
from app.core.database import SessionLocal


def seed_data():
    """
    Seed de datos para el servicio de órdenes.
    Coherente con los datos del supplier-service:
    - Vendedores: IDs 1-4 (Juan Pérez, María Gómez, Carlos López, Ana Ramírez)
    - Clientes: IDs 1-2 (Hospital Central, Clínica Norte)
    - Productos: IDs 1-3 (Jeringas 10ml, Guantes quirúrgicos, Mascarillas N95)
    - Países: 1=Colombia, 2=México, 3=Perú, 4=Ecuador
    """
    db = SessionLocal()
    try:
        print("🚀 Iniciando carga de datos de órdenes...")

        # === BODEGAS ===
        if db.query(Bodega).count() == 0:
            print("🏭 Insertando bodegas...")
            bodegas = [
                Bodega(
                    nombre="Bodega Central Bogotá",
                    direccion="Cra 50 # 26-20, Zona Industrial",
                    id_pais=1,  # Colombia
                    ciudad="Bogotá",
                    latitud=4.6097,
                    longitud=-74.0817
                ),
                Bodega(
                    nombre="Bodega Norte Medellín",
                    direccion="Calle 80 # 45-12",
                    id_pais=1,  # Colombia
                    ciudad="Medellín",
                    latitud=6.2442,
                    longitud=-75.5812
                ),
                Bodega(
                    nombre="Bodega Ciudad de México",
                    direccion="Av. Insurgentes Sur 1234",
                    id_pais=2,  # México
                    ciudad="Ciudad de México",
                    latitud=19.4326,
                    longitud=-99.1332
                ),
                Bodega(
                    nombre="Bodega Lima Centro",
                    direccion="Av. Javier Prado 456",
                    id_pais=3,  # Perú
                    ciudad="Lima",
                    latitud=-12.0464,
                    longitud=-77.0428
                ),
                Bodega(
                    nombre="Bodega Quito Sur",
                    direccion="Av. Mariscal Sucre y Quitumbe",
                    id_pais=4,  # Ecuador
                    ciudad="Quito",
                    latitud=-0.1807,
                    longitud=-78.4678
                ),
            ]
            db.add_all(bodegas)
            db.commit()
            print(f"✅ {len(bodegas)} bodegas creadas.")

        # === BODEGA PRODUCTOS (Inventario) ===
        if db.query(BodegaProducto).count() == 0:
            print("📦 Insertando inventario de productos en bodegas...")
            inventario = [
                # Bodega 1 - Bogotá
                BodegaProducto(id_bodega=1, id_producto=1, lote="JER-2024-001", cantidad=500, dias_alistamiento=2),
                BodegaProducto(id_bodega=1, id_producto=2, lote="GUA-2024-001", cantidad=1000, dias_alistamiento=1),
                BodegaProducto(id_bodega=1, id_producto=3, lote="MAS-2024-001", cantidad=800, dias_alistamiento=1),
                
                # Bodega 2 - Medellín
                BodegaProducto(id_bodega=2, id_producto=1, lote="JER-2024-002", cantidad=300, dias_alistamiento=3),
                BodegaProducto(id_bodega=2, id_producto=2, lote="GUA-2024-002", cantidad=600, dias_alistamiento=2),
                
                # Bodega 3 - Ciudad de México
                BodegaProducto(id_bodega=3, id_producto=3, lote="MAS-2024-MX1", cantidad=1200, dias_alistamiento=2),
                BodegaProducto(id_bodega=3, id_producto=1, lote="JER-2024-MX1", cantidad=400, dias_alistamiento=3),
                
                # Bodega 4 - Lima
                BodegaProducto(id_bodega=4, id_producto=1, lote="JER-2024-PE1", cantidad=250, dias_alistamiento=4),
                BodegaProducto(id_bodega=4, id_producto=2, lote="GUA-2024-PE1", cantidad=500, dias_alistamiento=3),
                BodegaProducto(id_bodega=4, id_producto=3, lote="MAS-2024-PE1", cantidad=700, dias_alistamiento=2),
                
                # Bodega 5 - Quito
                BodegaProducto(id_bodega=5, id_producto=2, lote="GUA-2024-EC1", cantidad=400, dias_alistamiento=2),
                BodegaProducto(id_bodega=5, id_producto=3, lote="MAS-2024-EC1", cantidad=600, dias_alistamiento=1),
            ]
            db.add_all(inventario)
            db.commit()
            print(f"✅ {len(inventario)} registros de inventario creados.")

        # === VEHÍCULOS ===
        if db.query(Vehiculo).count() == 0:
            print("🚚 Insertando vehículos...")
            vehiculos = [
                Vehiculo(id_conductor=1, placa="ABC-123", tipo=TipoVehiculo.CAMION),
                Vehiculo(id_conductor=2, placa="DEF-456", tipo=TipoVehiculo.VAN),
                Vehiculo(id_conductor=3, placa="GHI-789", tipo=TipoVehiculo.CAMION),
                Vehiculo(id_conductor=4, placa="JKL-012", tipo=TipoVehiculo.TRACTOMULA),
                Vehiculo(id_conductor=5, placa="MNO-345", tipo=TipoVehiculo.VAN),
            ]
            db.add_all(vehiculos)
            db.commit()
            print(f"✅ {len(vehiculos)} vehículos creados.")

        # === ÓRDENES ===
        if db.query(Orden).count() == 0:
            print("📋 Insertando órdenes...")
            
            # Fechas de referencia
            hoy = datetime.now()
            hace_20_dias = hoy - timedelta(days=20)
            hace_15_dias = hoy - timedelta(days=15)
            hace_10_dias = hoy - timedelta(days=10)
            hace_7_dias = hoy - timedelta(days=7)
            hace_2_dias = hoy - timedelta(days=2)
            manana = hoy + timedelta(days=1)
            en_5_dias = hoy + timedelta(days=5)
            en_10_dias = hoy + timedelta(days=10)
            
            ordenes = [
                # Orden 1: Entregada hace 20 días - Vendedor Juan Pérez (1) - Cliente Hospital Central (1)
                Orden(
                    fecha_entrega_estimada=hace_20_dias,
                    id_vehiculo=1,
                    id_cliente=1,
                    id_vendedor=1,
                    estado=EstadoOrden.ENTREGADO,
                    fecha_creacion=hace_20_dias - timedelta(days=2)
                ),
                
                # Orden 2: Entregada hace 15 días - Vendedor María Gómez (2) - Cliente Clínica Norte (2)
                Orden(
                    fecha_entrega_estimada=hace_15_dias,
                    id_vehiculo=2,
                    id_cliente=2,
                    id_vendedor=2,
                    estado=EstadoOrden.ENTREGADO,
                    fecha_creacion=hace_15_dias - timedelta(days=3)
                ),
                
                # Orden 3: En reparto - Vendedor Carlos López (3) - Cliente Hospital Central (1)
                Orden(
                    fecha_entrega_estimada=hoy,
                    id_vehiculo=3,
                    id_cliente=1,
                    id_vendedor=3,
                    estado=EstadoOrden.EN_REPARTO,
                    fecha_creacion=hace_2_dias
                ),
                
                # Orden 4: En alistamiento - Vendedor Juan Pérez (1) - Cliente Clínica Norte (2)
                Orden(
                    fecha_entrega_estimada=manana,
                    id_vehiculo=None,
                    id_cliente=2,
                    id_vendedor=1,
                    estado=EstadoOrden.EN_ALISTAMIENTO,
                    fecha_creacion=hace_7_dias
                ),
                
                # Orden 5: Por alistar - Vendedor Ana Ramírez (4) - Cliente Hospital Central (1)
                Orden(
                    fecha_entrega_estimada=en_5_dias,
                    id_vehiculo=None,
                    id_cliente=1,
                    id_vendedor=4,
                    estado=EstadoOrden.POR_ALISTAR,
                    fecha_creacion=hace_2_dias
                ),
                
                # Orden 6: Abierta (editable) - Vendedor María Gómez (2) - Cliente Hospital Central (1)
                Orden(
                    fecha_entrega_estimada=en_10_dias,
                    id_vehiculo=None,
                    id_cliente=1,
                    id_vendedor=2,
                    estado=EstadoOrden.ABIERTO,
                    fecha_creacion=hoy
                ),
                
                # Orden 7: Entregada hace 7 días - Vendedor Carlos López (3) - Cliente Clínica Norte (2)
                Orden(
                    fecha_entrega_estimada=hace_7_dias,
                    id_vehiculo=4,
                    id_cliente=2,
                    id_vendedor=3,
                    estado=EstadoOrden.ENTREGADO,
                    fecha_creacion=hace_7_dias - timedelta(days=4)
                ),
                
                # Orden 8: Abierta - Vendedor Juan Pérez (1) - Cliente Hospital Central (1)
                Orden(
                    fecha_entrega_estimada=en_10_dias,
                    id_vehiculo=None,
                    id_cliente=1,
                    id_vendedor=1,
                    estado=EstadoOrden.ABIERTO,
                    fecha_creacion=hoy - timedelta(hours=3)
                ),
            ]
            
            db.add_all(ordenes)
            db.commit()
            print(f"✅ {len(ordenes)} órdenes creadas.")

        # === ORDEN PRODUCTOS (Detalles de las órdenes) ===
        if db.query(OrdenProducto).count() == 0:
            print("🧾 Insertando productos de órdenes...")
            orden_productos = [
                # Orden 1: 50 Jeringas + 100 Guantes
                OrdenProducto(id_orden=1, id_producto=1, cantidad=50),
                OrdenProducto(id_orden=1, id_producto=2, cantidad=100),
                
                # Orden 2: 200 Mascarillas
                OrdenProducto(id_orden=2, id_producto=3, cantidad=200),
                
                # Orden 3: 30 Jeringas + 50 Guantes + 80 Mascarillas
                OrdenProducto(id_orden=3, id_producto=1, cantidad=30),
                OrdenProducto(id_orden=3, id_producto=2, cantidad=50),
                OrdenProducto(id_orden=3, id_producto=3, cantidad=80),
                
                # Orden 4: 150 Mascarillas
                OrdenProducto(id_orden=4, id_producto=3, cantidad=150),
                
                # Orden 5: 20 Jeringas + 40 Guantes
                OrdenProducto(id_orden=5, id_producto=1, cantidad=20),
                OrdenProducto(id_orden=5, id_producto=2, cantidad=40),
                
                # Orden 6: 10 Jeringas (orden abierta, puede editarse)
                OrdenProducto(id_orden=6, id_producto=1, cantidad=10),
                
                # Orden 7: 100 Guantes + 150 Mascarillas
                OrdenProducto(id_orden=7, id_producto=2, cantidad=100),
                OrdenProducto(id_orden=7, id_producto=3, cantidad=150),
                
                # Orden 8: 5 Jeringas (orden recién creada)
                OrdenProducto(id_orden=8, id_producto=1, cantidad=5),
            ]
            
            db.add_all(orden_productos)
            db.commit()
            print(f"✅ {len(orden_productos)} productos de órdenes creados.")

        # === NOVEDADES ===
        if db.query(NovedadOrden).count() == 0:
            print("⚠️ Insertando novedades de órdenes...")
            novedades = [
                # Novedad en orden 3 (en reparto)
                NovedadOrden(
                    id_pedido=3,
                    tipo=TipoNovedad.CANTIDAD_DIFERENTE,
                    descripcion="Se entregaron 28 jeringas en lugar de 30 solicitadas"
                ),
                
                # Novedad en orden 2 (entregada)
                NovedadOrden(
                    id_pedido=2,
                    tipo=TipoNovedad.MAL_ESTADO,
                    descripcion="5 unidades de mascarillas llegaron con empaque dañado"
                ),
                
                # Novedad en orden 7 (entregada)
                NovedadOrden(
                    id_pedido=7,
                    tipo=TipoNovedad.PRODUCTO_NO_COINCIDE,
                    descripcion="Se enviaron guantes talla M en lugar de talla L"
                ),
            ]
            
            db.add_all(novedades)
            db.commit()
            print(f"✅ {len(novedades)} novedades creadas.")

        print("\n🎉 ¡Datos de órdenes cargados correctamente!")
        print("\n📊 Resumen de datos creados:")
        print(f"   🏭 Bodegas: {db.query(Bodega).count()}")
        print(f"   📦 Inventario (bodega_producto): {db.query(BodegaProducto).count()}")
        print(f"   🚚 Vehículos: {db.query(Vehiculo).count()}")
        print(f"   📋 Órdenes: {db.query(Orden).count()}")
        print(f"   🧾 Productos en órdenes: {db.query(OrdenProducto).count()}")
        print(f"   ⚠️ Novedades: {db.query(NovedadOrden).count()}")
        print("\n💡 Coherencia con supplier-service:")
        print("   - Vendedores: IDs 1-4")
        print("   - Clientes: IDs 1-2")
        print("   - Productos: IDs 1-3")
        print("   - Países: 1=COL, 2=MEX, 3=PER, 4=ECU")

    except Exception as e:
        import traceback
        print(f"\n❌ Error al cargar datos de órdenes: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
