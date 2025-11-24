from app.models.role import Role
from app.models.user import User
from app.core.database import SessionLocal
from app.core.auth import get_password_hash


def seed_data():
    """
    Seed de datos para el servicio de usuarios.
    Crea roles y usuarios de ejemplo para todos los tipos de usuario del sistema.
    """
    db = SessionLocal()
    try:
        print("🚀 Iniciando carga de datos de usuarios...")

        # === ROLES ===
        if db.query(Role).count() == 0:
            print("👔 Insertando roles...")
            roles = [
                Role(name="Admin"),
                Role(name="Cliente"),
                Role(name="Vendedor"),
                Role(name="Conductor"),
            ]
            db.add_all(roles)
            db.commit()
            print(f"✅ {len(roles)} roles creados.")

        # === USUARIOS ===
        if db.query(User).count() == 0:
            print("👥 Insertando usuarios...")
            
            # Contraseña por defecto para todos: "password123"
            default_password = get_password_hash("password123")
            
            usuarios = [
                # Administradores
                User(
                    email="admin@medisupply.com",
                    name="Admin Principal",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=1  # Admin
                ),
                User(
                    email="admin2@medisupply.com",
                    name="Admin Secundario",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=1  # Admin
                ),
                
                # Vendedores (coherentes con supplier-service: IDs 1-4)
                User(
                    email="jp@example.com",
                    name="Juan Pérez",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=3  # Vendedor
                ),
                User(
                    email="mg@example.com",
                    name="María Gómez",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=3  # Vendedor
                ),
                User(
                    email="cl@example.com",
                    name="Carlos López",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=3  # Vendedor
                ),
                User(
                    email="ar@example.com",
                    name="Ana Ramírez",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=3  # Vendedor
                ),
                
                # Conductores (coherentes con order-service: IDs 1-5)
                User(
                    email="conductor1@medisupply.com",
                    name="Pedro Martínez",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=4  # Conductor
                ),
                User(
                    email="conductor2@medisupply.com",
                    name="Laura González",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=4  # Conductor
                ),
                User(
                    email="conductor3@medisupply.com",
                    name="Roberto Díaz",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=4  # Conductor
                ),
                User(
                    email="conductor4@medisupply.com",
                    name="Carmen Ruiz",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=4  # Conductor
                ),
                User(
                    email="conductor5@medisupply.com",
                    name="José Hernández",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=4  # Conductor
                ),
                
                # Clientes
                User(
                    email="cliente1@hospitalcentral.com",
                    name="Hospital Central Admin",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=2  # Cliente
                ),
                User(
                    email="cliente2@clinicanorte.com",
                    name="Clínica Norte Admin",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=2  # Cliente
                ),
                User(
                    email="cliente3@medisupply.com",
                    name="Cliente Demo",
                    hashed_password=default_password,
                    is_active=True,
                    role_id=2  # Cliente
                ),
                
                # Usuario inactivo (para testing)
                User(
                    email="inactive@medisupply.com",
                    name="Usuario Inactivo",
                    hashed_password=default_password,
                    is_active=False,
                    role_id=2  # Cliente
                ),
            ]
            
            db.add_all(usuarios)
            db.commit()
            print(f"✅ {len(usuarios)} usuarios creados.")

        print("\n🎉 ¡Datos de usuarios cargados correctamente!")
        print("\n📊 Resumen de datos creados:")
        print(f"   👔 Roles: {db.query(Role).count()}")
        print(f"   👥 Usuarios: {db.query(User).count()}")
        
        # Conteo por rol
        print("\n📈 Usuarios por rol:")
        for role in db.query(Role).all():
            count = db.query(User).filter(User.role_id == role.id).count()
            print(f"   - {role.name}: {count} usuarios")
        
        print("\n💡 Credenciales por defecto:")
        print("   - Password para todos: password123")
        print("   - Ejemplo Admin: admin@medisupply.com / password123")
        print("   - Ejemplo Vendedor: jp@example.com / password123")
        print("   - Ejemplo Conductor: conductor1@medisupply.com / password123")
        print("   - Ejemplo Cliente: cliente1@hospitalcentral.com / password123")

    except Exception as e:
        import traceback
        print(f"\n❌ Error al cargar datos de usuarios: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()

