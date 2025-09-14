#!/usr/bin/env python3
"""
Database setup script for the latency experiment
"""
import asyncio
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to postgres database to create our experiment database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='latency_experiment'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute('CREATE DATABASE latency_experiment')
            logger.info("Database 'latency_experiment' created successfully")
        else:
            logger.info("Database 'latency_experiment' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return False

async def test_connections():
    """Test database and cache connections"""
    logger.info("Testing connections...")
    
    # Test database
    try:
        from database import connect_db, disconnect_db, create_tables, init_sample_data
        await connect_db()
        logger.info("✅ Database connection successful")
        
        # Create tables
        create_tables()
        logger.info("✅ Database tables created")
        
        # Initialize sample data
        await init_sample_data()
        logger.info("✅ Sample data initialized")
        
        await disconnect_db()
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
    
    # Test Redis
    try:
        from cache_service import cache_service
        await cache_service.connect()
        logger.info("✅ Redis connection successful")
        await cache_service.disconnect()
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return False
    
    logger.info("🎉 All connections successful!")
    return True

async def main():
    logger.info("Setting up Critical Query Latency Experiment")
    logger.info("=" * 50)
    
    # Create database
    if not create_database():
        logger.error("Failed to create database. Exiting.")
        sys.exit(1)
    
    # Test connections
    if await test_connections():
        logger.info("✅ Setup completed successfully!")
        logger.info("You can now run: python main.py")
    else:
        logger.error("❌ Setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
