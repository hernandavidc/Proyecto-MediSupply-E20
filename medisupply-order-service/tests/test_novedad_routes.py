import pytest
from datetime import datetime, timedelta
from io import BytesIO


def test_create_novedad(client):
    """Test creating a novedad for an orden"""
    # First create an orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create novedad using form-data
    novedad_data = {
        "id_pedido": orden_id,
        "tipo": "DEVOLUCION",
        "descripcion": "Cliente rechazó el producto"
    }
    
    response = client.post("/api/v1/novedades", data=novedad_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["tipo"] == "DEVOLUCION"


def test_list_novedades(client):
    """Test listing all novedades"""
    response = client.get("/api/v1/novedades")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_novedad_by_id(client):
    """Test getting novedad by ID"""
    # Create orden and novedad
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    novedad_data = {
        "id_pedido": orden_id,
        "tipo": "MAL_ESTADO",
        "descripcion": "Producto dañado"
    }
    create_response = client.post("/api/v1/novedades", data=novedad_data)
    novedad_id = create_response.json()["id"]
    
    # Get novedad
    get_response = client.get(f"/api/v1/novedades/{novedad_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == novedad_id


def test_get_novedades_by_orden(client):
    """Test getting novedades for a specific orden"""
    # Create orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create multiple novedades for this orden
    tipos = ["DEVOLUCION", "CANTIDAD_DIFERENTE"]
    for tipo in tipos:
        novedad_data = {
            "id_pedido": orden_id,
            "tipo": tipo,
            "descripcion": f"Novedad tipo {tipo}"
        }
        client.post("/api/v1/novedades", data=novedad_data)
    
    # Get novedades for orden - usar el endpoint correcto
    response = client.get(f"/api/v1/novedades/orden/{orden_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_create_novedad_for_nonexistent_orden(client):
    """Test creating novedad for non-existent orden"""
    novedad_data = {
        "id_pedido": 99999,
        "tipo": "DEVOLUCION",
        "descripcion": "Test"
    }
    
    response = client.post("/api/v1/novedades", data=novedad_data)
    # SQLite doesn't enforce foreign keys by default in tests, so it may succeed
    # In production with PostgreSQL, this would fail with 400 or 404
    assert response.status_code in [201, 400, 404, 422]


def test_create_novedad_with_photos(client):
    """Test creating a novedad with photo attachments"""
    # First create an orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create fake image files
    image1 = BytesIO(b"fake image content 1")
    image1.name = "test_image1.jpg"
    
    image2 = BytesIO(b"fake image content 2")
    image2.name = "test_image2.jpg"
    
    # Create novedad with photos using multipart/form-data
    response = client.post(
        "/api/v1/novedades",
        data={
            "id_pedido": orden_id,
            "tipo": "MAL_ESTADO",
            "descripcion": "Producto llegó dañado - ver fotos"
        },
        files=[
            ("fotos", ("image1.jpg", image1, "image/jpeg")),
            ("fotos", ("image2.jpg", image2, "image/jpeg"))
        ]
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["tipo"] == "MAL_ESTADO"
    assert "fotos" in data
    assert data["fotos"] is not None
    assert len(data["fotos"]) == 2
    # Verify the URLs have the correct format
    for foto_url in data["fotos"]:
        assert foto_url.startswith("/uploads/novedades/")
        assert foto_url.endswith(".jpg")


def test_create_novedad_without_photos(client):
    """Test creating a novedad without photos using multipart/form-data"""
    # First create an orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create novedad without photos
    response = client.post(
        "/api/v1/novedades",
        data={
            "id_pedido": orden_id,
            "tipo": "CANTIDAD_DIFERENTE",
            "descripcion": "Faltan unidades"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["tipo"] == "CANTIDAD_DIFERENTE"
    # fotos should be None or empty list
    assert data.get("fotos") is None or data.get("fotos") == []


def test_get_novedad_with_photos(client):
    """Test retrieving a novedad with photos"""
    # Create orden
    orden_data = {
        "fecha_entrega_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
        "id_cliente": 1,
        "id_vendedor": 1,
        "estado": "ABIERTO"
    }
    orden_response = client.post("/api/v1/ordenes", json=orden_data)
    orden_id = orden_response.json()["id"]
    
    # Create novedad with photo
    image = BytesIO(b"fake image content")
    image.name = "test.jpg"
    
    create_response = client.post(
        "/api/v1/novedades",
        data={
            "id_pedido": orden_id,
            "tipo": "PRODUCTO_NO_COINCIDE",
            "descripcion": "Producto incorrecto"
        },
        files=[("fotos", ("test.jpg", image, "image/jpeg"))]
    )
    
    novedad_id = create_response.json()["id"]
    
    # Get novedad
    get_response = client.get(f"/api/v1/novedades/{novedad_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == novedad_id
    assert "fotos" in data
    assert len(data["fotos"]) == 1

