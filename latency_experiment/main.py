from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import time
import logging
from datetime import datetime

from database import connect_db, disconnect_db, create_tables, init_sample_data
from cache_service import cache_service
from query_services import inventory_query_service, order_query_service
from command_services import inventory_command_service, order_command_service
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Critical Query Latency Experiment",
    description="CQRS implementation with cache optimization for latency testing",
    version="1.0.0"
)

# Pydantic models
class InventoryUpdateRequest(BaseModel):
    warehouse_code: str
    quantity_delta: int

class OrderStatusUpdateRequest(BaseModel):
    status: str

class OrderItemRequest(BaseModel):
    sku: str
    quantity: int
    unit_price: float

class CreateOrderRequest(BaseModel):
    client_id: str
    items: List[OrderItemRequest]

class PerformanceMetrics(BaseModel):
    endpoint: str
    response_time: float
    cache_hit: bool
    timestamp: str

# Middleware for response time measurement
@app.middleware("http")
async def add_performance_headers(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Timestamp"] = datetime.utcnow().isoformat()
    
    # Log slow queries
    if process_time > 1.0:
        logger.warning(f"Slow query detected: {request.url.path} took {process_time:.3f}s")
    
    return response

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    await connect_db()
    await cache_service.connect()
    create_tables()
    await init_sample_data()
    logger.info("Latency Experiment API started")

@app.on_event("shutdown")
async def shutdown():
    await cache_service.disconnect()
    await disconnect_db()
    logger.info("Latency Experiment API stopped")

# Query endpoints (Read operations)
@app.get("/api/inventory/{sku}")
async def get_inventory(
    sku: str,
    warehouse_code: Optional[str] = Query(None, description="Specific warehouse code")
):
    """Get inventory information for a SKU - SLA: ≤2 seconds"""
    start_time = time.time()
    
    try:
        inventory_data = await inventory_query_service.get_inventory_by_sku(sku, warehouse_code)
        response_time = time.time() - start_time
        
        if not inventory_data:
            raise HTTPException(status_code=404, detail=f"Inventory not found for SKU: {sku}")
        
        # Check SLA compliance
        if response_time > settings.INVENTORY_QUERY_SLA:
            logger.warning(f"SLA violation: Inventory query took {response_time:.3f}s (SLA: {settings.INVENTORY_QUERY_SLA}s)")
        
        return {
            "data": inventory_data,
            "metadata": {
                "response_time": response_time,
                "sla_compliant": response_time <= settings.INVENTORY_QUERY_SLA,
                "cached": response_time < 0.1  # Assume cache if very fast
            }
        }
        
    except Exception as e:
        logger.error(f"Inventory query failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/inventory/{sku}/locations")
async def get_product_locations(sku: str):
    """Get all warehouse locations for a product - SLA: ≤1 second"""
    start_time = time.time()
    
    try:
        locations = await inventory_query_service.get_product_locations(sku)
        response_time = time.time() - start_time
        
        # Check SLA compliance
        if response_time > settings.PRODUCT_LOCATION_SLA:
            logger.warning(f"SLA violation: Product location query took {response_time:.3f}s (SLA: {settings.PRODUCT_LOCATION_SLA}s)")
        
        return {
            "data": locations,
            "metadata": {
                "response_time": response_time,
                "sla_compliant": response_time <= settings.PRODUCT_LOCATION_SLA,
                "locations_count": len(locations)
            }
        }
        
    except Exception as e:
        logger.error(f"Product location query failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/orders/{order_number}/status")
async def get_order_status(order_number: str):
    """Get order status - SLA: ≤1 second"""
    start_time = time.time()
    
    try:
        order_data = await order_query_service.get_order_status(order_number)
        response_time = time.time() - start_time
        
        if not order_data:
            raise HTTPException(status_code=404, detail=f"Order not found: {order_number}")
        
        # Check SLA compliance
        if response_time > settings.ORDER_STATUS_SLA:
            logger.warning(f"SLA violation: Order status query took {response_time:.3f}s (SLA: {settings.ORDER_STATUS_SLA}s)")
        
        return {
            "data": order_data,
            "metadata": {
                "response_time": response_time,
                "sla_compliant": response_time <= settings.ORDER_STATUS_SLA
            }
        }
        
    except Exception as e:
        logger.error(f"Order status query failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Command endpoints (Write operations)
@app.put("/api/inventory/{sku}")
async def update_inventory(sku: str, update_request: InventoryUpdateRequest):
    """Update inventory quantity - Write operation"""
    try:
        result = await inventory_command_service.update_inventory(
            sku, update_request.warehouse_code, update_request.quantity_delta
        )
        return {"message": "Inventory updated successfully", "data": result}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Inventory update failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/api/orders/{order_number}/status")
async def update_order_status(order_number: str, update_request: OrderStatusUpdateRequest):
    """Update order status - Write operation"""
    try:
        result = await order_command_service.update_order_status(
            order_number, update_request.status
        )
        return {"message": "Order status updated successfully", "data": result}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Order status update failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/orders")
async def create_order(order_request: CreateOrderRequest):
    """Create new order - Write operation"""
    try:
        items = [item.dict() for item in order_request.items]
        result = await order_command_service.create_order(order_request.client_id, items)
        return {"message": "Order created successfully", "data": result}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Order creation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Metrics and monitoring endpoints
@app.get("/api/metrics/performance")
async def get_performance_metrics():
    """Get performance metrics from database"""
    try:
        query = """
        SELECT 
            query_type,
            endpoint,
            AVG(response_time) as avg_response_time,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) as p95_response_time,
            PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time) as p99_response_time,
            COUNT(*) as total_queries,
            SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits,
            SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as cache_hit_rate
        FROM query_metrics 
        WHERE timestamp > NOW() - INTERVAL '1 hour'
        GROUP BY query_type, endpoint
        ORDER BY avg_response_time DESC
        """
        
        results = await database.fetch_all(query)
        return [dict(row) for row in results]
        
    except Exception as e:
        logger.error(f"Metrics query failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/metrics/sla-compliance")
async def get_sla_compliance():
    """Get SLA compliance metrics"""
    try:
        inventory_query = """
        SELECT 
            COUNT(*) as total_queries,
            SUM(CASE WHEN response_time <= :sla THEN 1 ELSE 0 END) as compliant_queries,
            SUM(CASE WHEN response_time <= :sla THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as compliance_rate
        FROM query_metrics 
        WHERE query_type = 'inventory_query' AND timestamp > NOW() - INTERVAL '1 hour'
        """
        
        order_query = """
        SELECT 
            COUNT(*) as total_queries,
            SUM(CASE WHEN response_time <= :sla THEN 1 ELSE 0 END) as compliant_queries,
            SUM(CASE WHEN response_time <= :sla THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as compliance_rate
        FROM query_metrics 
        WHERE query_type = 'order_status_query' AND timestamp > NOW() - INTERVAL '1 hour'
        """
        
        from database import database
        inventory_compliance = await database.fetch_one(inventory_query, {"sla": settings.INVENTORY_QUERY_SLA})
        order_compliance = await database.fetch_one(order_query, {"sla": settings.ORDER_STATUS_SLA})
        
        return {
            "inventory_queries": dict(inventory_compliance) if inventory_compliance else {},
            "order_status_queries": dict(order_compliance) if order_compliance else {},
            "cache_stats": await cache_service.get_cache_stats()
        }
        
    except Exception as e:
        logger.error(f"SLA compliance query failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database
        from database import database
        db_result = await database.fetch_val("SELECT 1")
        
        # Test cache
        await cache_service.redis.ping()
        
        return {
            "status": "healthy",
            "database": "connected" if db_result else "error",
            "cache": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
