import time
from typing import Dict, List
from database import database
from cache_service import cache_service
import logging

logger = logging.getLogger(__name__)

class InventoryCommandService:
    """Write-optimized service for inventory updates"""
    
    async def update_inventory(self, sku: str, warehouse_code: str, quantity_delta: int) -> Dict:
        """Update inventory quantity and invalidate cache"""
        start_time = time.time()
        
        try:
            # Start transaction
            async with database.transaction():
                # Get current inventory
                current_query = """
                SELECT i.id, i.quantity, i.available_quantity, p.sku
                FROM inventory i
                JOIN products p ON i.product_id = p.id
                JOIN warehouses w ON i.warehouse_id = w.id
                WHERE p.sku = :sku AND w.code = :warehouse_code
                FOR UPDATE
                """
                
                current = await database.fetch_one(current_query, 
                                                 {"sku": sku, "warehouse_code": warehouse_code})
                
                if not current:
                    raise ValueError(f"Inventory not found for SKU {sku} in warehouse {warehouse_code}")
                
                new_quantity = current["quantity"] + quantity_delta
                new_available = current["available_quantity"] + quantity_delta
                
                if new_quantity < 0:
                    raise ValueError("Insufficient inventory")
                
                # Update inventory
                update_query = """
                UPDATE inventory 
                SET quantity = :quantity, 
                    available_quantity = :available_quantity,
                    last_updated = NOW()
                WHERE id = :inventory_id
                """
                
                await database.execute(update_query, {
                    "quantity": new_quantity,
                    "available_quantity": new_available,
                    "inventory_id": current["id"]
                })
                
                # Invalidate cache
                await cache_service.invalidate_inventory_cache(sku)
                
                operation_time = time.time() - start_time
                
                return {
                    "sku": sku,
                    "warehouse_code": warehouse_code,
                    "previous_quantity": current["quantity"],
                    "new_quantity": new_quantity,
                    "delta": quantity_delta,
                    "operation_time": operation_time
                }
                
        except Exception as e:
            logger.error(f"Inventory update failed: {e}")
            raise

class OrderCommandService:
    """Write-optimized service for order operations"""
    
    async def update_order_status(self, order_number: str, new_status: str) -> Dict:
        """Update order status and invalidate cache"""
        start_time = time.time()
        
        try:
            # Update order status
            update_query = """
            UPDATE orders 
            SET status = :status, updated_at = NOW()
            WHERE order_number = :order_number
            """
            
            result = await database.execute(update_query, {
                "status": new_status,
                "order_number": order_number
            })
            
            if result == 0:
                raise ValueError(f"Order {order_number} not found")
            
            # Invalidate cache
            cache_key_pattern = f"order_status:*{order_number}*"
            keys = await cache_service.redis.keys(cache_key_pattern)
            if keys:
                await cache_service.redis.delete(*keys)
            
            operation_time = time.time() - start_time
            
            return {
                "order_number": order_number,
                "new_status": new_status,
                "operation_time": operation_time
            }
            
        except Exception as e:
            logger.error(f"Order status update failed: {e}")
            raise
    
    async def create_order(self, client_id: str, items: List[Dict]) -> Dict:
        """Create new order with inventory validation"""
        start_time = time.time()
        
        try:
            async with database.transaction():
                # Generate order number
                order_count = await database.fetch_val("SELECT COUNT(*) FROM orders") + 1
                order_number = f"ORD{order_count:06d}"
                
                # Calculate total amount
                total_amount = sum(item["quantity"] * item["unit_price"] for item in items)
                
                # Create order
                order_query = """
                INSERT INTO orders (order_number, client_id, status, total_amount)
                VALUES (:order_number, :client_id, :status, :total_amount)
                RETURNING id
                """
                
                order_id = await database.fetch_val(order_query, {
                    "order_number": order_number,
                    "client_id": client_id,
                    "status": "pending",
                    "total_amount": total_amount
                })
                
                # Create order items and reserve inventory
                for item in items:
                    # Insert order item
                    item_query = """
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
                    SELECT :order_id, p.id, :quantity, :unit_price, :total_price
                    FROM products p WHERE p.sku = :sku
                    """
                    
                    await database.execute(item_query, {
                        "order_id": order_id,
                        "sku": item["sku"],
                        "quantity": item["quantity"],
                        "unit_price": item["unit_price"],
                        "total_price": item["quantity"] * item["unit_price"]
                    })
                    
                    # Reserve inventory (simplified - reserve from first available warehouse)
                    reserve_query = """
                    UPDATE inventory 
                    SET reserved_quantity = reserved_quantity + :quantity,
                        available_quantity = available_quantity - :quantity
                    WHERE product_id = (SELECT id FROM products WHERE sku = :sku)
                    AND available_quantity >= :quantity
                    AND id = (
                        SELECT id FROM inventory 
                        WHERE product_id = (SELECT id FROM products WHERE sku = :sku)
                        AND available_quantity >= :quantity
                        ORDER BY available_quantity DESC
                        LIMIT 1
                    )
                    """
                    
                    rows_updated = await database.execute(reserve_query, {
                        "quantity": item["quantity"],
                        "sku": item["sku"]
                    })
                    
                    if rows_updated == 0:
                        raise ValueError(f"Insufficient inventory for SKU {item['sku']}")
                    
                    # Invalidate inventory cache
                    await cache_service.invalidate_inventory_cache(item["sku"])
                
                operation_time = time.time() - start_time
                
                return {
                    "order_number": order_number,
                    "order_id": order_id,
                    "total_amount": total_amount,
                    "items_count": len(items),
                    "operation_time": operation_time
                }
                
        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            raise

# Global service instances
inventory_command_service = InventoryCommandService()
order_command_service = OrderCommandService()
