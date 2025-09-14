import time
from typing import List, Dict, Optional
from database import database
from cache_service import cache_service
from config import settings
import logging

logger = logging.getLogger(__name__)

class InventoryQueryService:
    """Read-optimized service for inventory queries"""
    
    async def get_inventory_by_sku(self, sku: str, warehouse_code: str = None) -> Dict:
        """Get inventory information for a specific SKU with cache optimization"""
        start_time = time.time()
        cache_hit = False
        
        # Try cache first
        cached_data = await cache_service.get_inventory_cache(sku, warehouse_code)
        if cached_data:
            cache_hit = True
            query_time = time.time() - start_time
            
            # Log metrics
            await self._log_query_metrics("inventory_query", "GET /api/inventory/{sku}", 
                                         query_time, cache_hit, {"sku": sku})
            
            return cached_data
        
        # Build query based on parameters
        if warehouse_code:
            query = """
            SELECT 
                p.sku, p.name, p.category,
                i.quantity, i.reserved_quantity, i.available_quantity,
                i.zone, i.shelf,
                w.code as warehouse_code, w.name as warehouse_name,
                i.last_updated
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            JOIN warehouses w ON i.warehouse_id = w.id
            WHERE p.sku = :sku AND w.code = :warehouse_code AND w.active = true
            """
            params = {"sku": sku, "warehouse_code": warehouse_code}
        else:
            query = """
            SELECT 
                p.sku, p.name, p.category,
                SUM(i.quantity) as total_quantity,
                SUM(i.reserved_quantity) as total_reserved,
                SUM(i.available_quantity) as total_available,
                COUNT(w.id) as warehouse_count,
                MAX(i.last_updated) as last_updated
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            JOIN warehouses w ON i.warehouse_id = w.id
            WHERE p.sku = :sku AND w.active = true
            GROUP BY p.id, p.sku, p.name, p.category
            """
            params = {"sku": sku}
        
        # Execute query
        result = await database.fetch_one(query, params)
        
        query_time = time.time() - start_time
        
        if result:
            inventory_data = dict(result)
            
            # Cache the result
            await cache_service.set_inventory_cache(sku, inventory_data, warehouse_code)
            
            # Log metrics
            await self._log_query_metrics("inventory_query", "GET /api/inventory/{sku}", 
                                         query_time, cache_hit, {"sku": sku})
            
            return inventory_data
        else:
            # Log metrics even for not found
            await self._log_query_metrics("inventory_query", "GET /api/inventory/{sku}", 
                                         query_time, cache_hit, {"sku": sku, "result": "not_found"})
            return None
    
    async def get_product_locations(self, sku: str) -> List[Dict]:
        """Get all warehouse locations for a product"""
        start_time = time.time()
        cache_hit = False
        
        # Try cache first
        cached_data = await cache_service.get_product_location_cache(sku)
        if cached_data:
            cache_hit = True
            query_time = time.time() - start_time
            
            await self._log_query_metrics("product_location_query", "GET /api/inventory/{sku}/locations", 
                                         query_time, cache_hit, {"sku": sku})
            
            return cached_data
        
        query = """
        SELECT 
            w.code as warehouse_code, w.name as warehouse_name, w.location,
            i.quantity, i.available_quantity, i.zone, i.shelf,
            i.last_updated
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        JOIN warehouses w ON i.warehouse_id = w.id
        WHERE p.sku = :sku AND w.active = true AND i.available_quantity > 0
        ORDER BY i.available_quantity DESC
        """
        
        results = await database.fetch_all(query, {"sku": sku})
        query_time = time.time() - start_time
        
        locations = [dict(row) for row in results]
        
        # Cache the result
        await cache_service.set_product_location_cache(sku, locations)
        
        # Log metrics
        await self._log_query_metrics("product_location_query", "GET /api/inventory/{sku}/locations", 
                                     query_time, cache_hit, {"sku": sku, "locations_found": len(locations)})
        
        return locations
    
    async def _log_query_metrics(self, query_type: str, endpoint: str, response_time: float, 
                               cache_hit: bool, parameters: Dict):
        """Log query performance metrics"""
        try:
            await database.execute(
                """INSERT INTO query_metrics (query_type, endpoint, response_time, cache_hit, parameters)
                   VALUES (:query_type, :endpoint, :response_time, :cache_hit, :parameters)""",
                {
                    "query_type": query_type,
                    "endpoint": endpoint,
                    "response_time": response_time,
                    "cache_hit": cache_hit,
                    "parameters": str(parameters)
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log metrics: {e}")

class OrderQueryService:
    """Read-optimized service for order queries"""
    
    async def get_order_status(self, order_number: str) -> Dict:
        """Get order status with cache optimization"""
        start_time = time.time()
        cache_hit = False
        
        # Try cache first
        cached_data = await cache_service.get_order_status_cache(order_number)
        if cached_data:
            cache_hit = True
            query_time = time.time() - start_time
            
            await self._log_query_metrics("order_status_query", "GET /api/orders/{order_number}/status", 
                                         query_time, cache_hit, {"order_number": order_number})
            
            return cached_data
        
        query = """
        SELECT 
            o.order_number, o.client_id, o.status, o.total_amount,
            o.created_at, o.updated_at,
            COUNT(oi.id) as item_count,
            STRING_AGG(p.sku, ', ') as product_skus
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE o.order_number = :order_number
        GROUP BY o.id, o.order_number, o.client_id, o.status, o.total_amount, o.created_at, o.updated_at
        """
        
        result = await database.fetch_one(query, {"order_number": order_number})
        query_time = time.time() - start_time
        
        if result:
            order_data = dict(result)
            
            # Cache the result
            await cache_service.set_order_status_cache(order_number, order_data)
            
            # Log metrics
            await self._log_query_metrics("order_status_query", "GET /api/orders/{order_number}/status", 
                                         query_time, cache_hit, {"order_number": order_number})
            
            return order_data
        else:
            await self._log_query_metrics("order_status_query", "GET /api/orders/{order_number}/status", 
                                         query_time, cache_hit, {"order_number": order_number, "result": "not_found"})
            return None
    
    async def _log_query_metrics(self, query_type: str, endpoint: str, response_time: float, 
                               cache_hit: bool, parameters: Dict):
        """Log query performance metrics"""
        try:
            await database.execute(
                """INSERT INTO query_metrics (query_type, endpoint, response_time, cache_hit, parameters)
                   VALUES (:query_type, :endpoint, :response_time, :cache_hit, :parameters)""",
                {
                    "query_type": query_type,
                    "endpoint": endpoint,
                    "response_time": response_time,
                    "cache_hit": cache_hit,
                    "parameters": str(parameters)
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log metrics: {e}")

# Global service instances
inventory_query_service = InventoryQueryService()
order_query_service = OrderQueryService()
