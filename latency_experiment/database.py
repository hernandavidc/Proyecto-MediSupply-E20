import asyncio
from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from config import settings
from models import Base
import logging

logger = logging.getLogger(__name__)

# Database connection
database = Database(
    settings.DATABASE_URL,
    min_size=settings.MIN_DB_CONNECTIONS,
    max_size=settings.MAX_DB_CONNECTIONS
)

# SQLAlchemy engine for migrations
engine = create_engine(settings.DATABASE_URL)
metadata = MetaData()

async def connect_db():
    """Connect to database"""
    try:
        await database.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

async def disconnect_db():
    """Disconnect from database"""
    await database.disconnect()
    logger.info("Database disconnected")

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

async def init_sample_data():
    """Initialize database with sample data for testing"""
    
    # Check if data already exists
    count_query = "SELECT COUNT(*) FROM products"
    count = await database.fetch_val(count_query)
    
    if count > 0:
        logger.info("Sample data already exists")
        return
    
    logger.info("Initializing sample data...")
    
    # Insert warehouses
    warehouses = [
        {"code": "WH001", "name": "Main Warehouse", "location": "Bogota, Colombia"},
        {"code": "WH002", "name": "Distribution Center", "location": "Medellin, Colombia"},
        {"code": "WH003", "name": "Regional Hub", "location": "Cali, Colombia"}
    ]
    
    for wh in warehouses:
        await database.execute(
            "INSERT INTO warehouses (code, name, location, active) VALUES (:code, :name, :location, :active)",
            {**wh, "active": True}
        )
    
    # Insert products
    products = []
    for i in range(1000):  # 1000 products for realistic testing
        products.append({
            "sku": f"MED{i:06d}",
            "name": f"Medical Product {i}",
            "description": f"Medical product for testing - {i}",
            "category": f"Category {i % 10}",
            "unit_price": 10.0 + (i % 100)
        })
    
    # Batch insert products
    await database.execute_many(
        "INSERT INTO products (sku, name, description, category, unit_price) VALUES (:sku, :name, :description, :category, :unit_price)",
        products
    )
    
    # Insert inventory data
    inventory_data = []
    product_ids = await database.fetch_all("SELECT id FROM products")
    warehouse_ids = await database.fetch_all("SELECT id FROM warehouses")
    
    for product in product_ids:
        for warehouse in warehouse_ids:
            qty = 100 + (product["id"] % 500)  # Varying quantities
            inventory_data.append({
                "product_id": product["id"],
                "warehouse_id": warehouse["id"],
                "quantity": qty,
                "reserved_quantity": qty // 10,
                "available_quantity": qty - (qty // 10),
                "zone": f"Zone-{warehouse['id']}",
                "shelf": f"Shelf-{product['id'] % 20}"
            })
    
    # Batch insert inventory
    await database.execute_many(
        """INSERT INTO inventory (product_id, warehouse_id, quantity, reserved_quantity, 
           available_quantity, zone, shelf) VALUES (:product_id, :warehouse_id, :quantity, 
           :reserved_quantity, :available_quantity, :zone, :shelf)""",
        inventory_data
    )
    
    # Insert sample orders
    orders_data = []
    for i in range(500):  # 500 sample orders
        orders_data.append({
            "order_number": f"ORD{i:06d}",
            "client_id": f"CLIENT{i % 50:03d}",
            "status": ["pending", "processing", "shipped", "delivered"][i % 4],
            "total_amount": 100.0 + (i % 1000)
        })
    
    await database.execute_many(
        "INSERT INTO orders (order_number, client_id, status, total_amount) VALUES (:order_number, :client_id, :status, :total_amount)",
        orders_data
    )
    
    logger.info("Sample data initialization completed")
