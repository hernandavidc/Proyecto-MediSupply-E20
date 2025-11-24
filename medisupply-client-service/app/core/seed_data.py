import uuid
from app.models.client import Client
from app.core.database import SessionLocal


def seed_data():
    """
    Seed de datos para el servicio de clientes.
    Crea clientes de ejemplo para validación y registro inicial.
    """
    db = SessionLocal()
    try:
        print("🚀 Iniciando carga de datos de clientes...")

        # === CLIENTES ===
        if db.query(Client).count() == 0:
            print("🏥 Insertando clientes...")
            
            clientes = [
                # Cliente 1 - Hospital validado
                Client(
                    id=str(uuid.uuid4()),
                    nombre="Hospital Central de Bogotá",
                    nit="900123456-7",
                    direccion="Cra 10 # 20-30, Bogotá, Colombia",
                    nombre_contacto="Dra. Patricia Pérez",
                    telefono_contacto="+57 1 234 5678",
                    email_contacto="compras@hospitalcentral.com.co",
                    is_validated=True
                ),
                
                # Cliente 2 - Clínica validada
                Client(
                    id=str(uuid.uuid4()),
                    nombre="Clínica Norte S.A.S",
                    nit="900234567-8",
                    direccion="Av. Reforma 123, Ciudad de México, México",
                    nombre_contacto="Dr. Roberto Gómez",
                    telefono_contacto="+52 55 9876 5432",
                    email_contacto="adquisiciones@clinicanorte.mx",
                    is_validated=True
                ),
                
                # Cliente 3 - Hospital pendiente validación
                Client(
                    id=str(uuid.uuid4()),
                    nombre="Hospital San Rafael",
                    nit="900345678-9",
                    direccion="Av. Javier Prado 456, Lima, Perú",
                    nombre_contacto="Lic. Carmen López",
                    telefono_contacto="+51 1 456 7890",
                    email_contacto="logistica@sanrafael.pe",
                    is_validated=False
                ),
                
                # Cliente 4 - Clínica validada
                Client(
                    id=str(uuid.uuid4()),
                    nombre="Clínica El Bosque",
                    nit="900456789-0",
                    direccion="Calle 134 # 7-83, Bogotá, Colombia",
                    nombre_contacto="Dr. Fernando Díaz",
                    telefono_contacto="+57 1 987 6543",
                    email_contacto="compras@elbosque.com.co",
                    is_validated=True
                ),
                
                # Cliente 5 - Centro médico pendiente
                Client(
                    id=str(uuid.uuid4()),
                    nombre="Centro Médico Andino",
                    nit="900567890-1",
                    direccion="Av. Mariscal Sucre 789, Quito, Ecuador",
                    nombre_contacto="Dra. Sofía Ramírez",
                    telefono_contacto="+593 2 345 6789",
                    email_contacto="admin@medicoandino.ec",
                    is_validated=False
                ),
                
                # Cliente 6 - Hospital validado
                Client(
                    id=str(uuid.uuid4()),
                    nombre="Hospital Universitario del Valle",
                    nit="900678901-2",
                    direccion="Calle 5 # 36-08, Cali, Colombia",
                    nombre_contacto="Dr. Miguel Ángel Torres",
                    telefono_contacto="+57 2 556 7890",
                    email_contacto="suministros@huv.gov.co",
                    is_validated=True
                ),
                
                # Cliente 7 - Clínica privada validada
                Client(
                    id=str(uuid.uuid4()),
                    nombre="Clínica Internacional",
                    nit="900789012-3",
                    direccion="Av. Grau 800, Lima, Perú",
                    nombre_contacto="Lic. Ana María Flores",
                    telefono_contacto="+51 1 567 8901",
                    email_contacto="compras@clinicainternacional.pe",
                    is_validated=True
                ),
                
                # Cliente 8 - Centro de salud pendiente
                Client(
                    id=str(uuid.uuid4()),
                    nombre="Centro de Salud Guadalajara",
                    nit="900890123-4",
                    direccion="Av. Chapultepec 234, Guadalajara, México",
                    nombre_contacto="Dr. Luis Hernández",
                    telefono_contacto="+52 33 2345 6789",
                    email_contacto="administracion@csgdl.mx",
                    is_validated=False
                ),
                
                # Cliente 9 - IPS validada
                Client(
                    id=str(uuid.uuid4()),
                    nombre="IPS Salud Total",
                    nit="900901234-5",
                    direccion="Cra 15 # 93-30, Bogotá, Colombia",
                    nombre_contacto="Dr. Andrés Castro",
                    telefono_contacto="+57 1 432 1098",
                    email_contacto="logistica@saludtotal.com.co",
                    is_validated=True
                ),
                
                # Cliente 10 - Clínica especializada validada
                Client(
                    id=str(uuid.uuid4()),
                    nombre="Clínica Cardiovascular",
                    nit="901012345-6",
                    direccion="Av. El Sol 567, Medellín, Colombia",
                    nombre_contacto="Dra. Beatriz Moreno",
                    telefono_contacto="+57 4 321 0987",
                    email_contacto="compras@cardiovascular.com.co",
                    is_validated=True
                ),
            ]
            
            db.add_all(clientes)
            db.commit()
            print(f"✅ {len(clientes)} clientes creados.")

        print("\n🎉 ¡Datos de clientes cargados correctamente!")
        print("\n📊 Resumen de datos creados:")
        print(f"   🏥 Total clientes: {db.query(Client).count()}")
        
        # Conteo por estado de validación
        validados = db.query(Client).filter(Client.is_validated == True).count()
        pendientes = db.query(Client).filter(Client.is_validated == False).count()
        
        print("\n📈 Clientes por estado:")
        print(f"   ✅ Validados: {validados}")
        print(f"   ⏳ Pendientes de validación: {pendientes}")
        
        print("\n💡 Información adicional:")
        print("   - Todos los clientes tienen NIT único")
        print("   - Incluye clientes de Colombia, México, Perú y Ecuador")
        print("   - Mezcla de hospitales, clínicas, IPS y centros médicos")

    except Exception as e:
        import traceback
        print(f"\n❌ Error al cargar datos de clientes: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()

