import pytest
from datetime import datetime

from app.services.visita_service import create_visita, get_visitas_for_vendedor
from app.models.catalogs import Pais
from app.models.vendedor import Vendedor


def test_create_visita_success(db_session):
    # preparar datos mínimos: país y vendedor
    pais = Pais(nombre='Testland')
    db_session.add(pais)
    db_session.commit()
    db_session.refresh(pais)

    vendedor = Vendedor(nombre='Juan', email='juan@test.local', pais=pais.id)
    db_session.add(vendedor)
    db_session.commit()
    db_session.refresh(vendedor)

    payload = {
        'lat': 10.0,
        'lon': -70.0,
        'direccion': 'Calle Falsa 123',
        'notas': 'Visita de prueba'
    }

    visita = create_visita(db_session, vendedor.id, payload)
    assert visita.id is not None
    assert visita.vendedor_id == vendedor.id
    assert abs(visita.lat - 10.0) < 1e-6


def test_create_visita_invalid_coords_non_numeric(db_session):
    pais = Pais(nombre='Nowhere')
    db_session.add(pais)
    db_session.commit()
    db_session.refresh(pais)

    vendedor = Vendedor(nombre='Ana', email='ana@test.local', pais=pais.id)
    db_session.add(vendedor)
    db_session.commit()
    db_session.refresh(vendedor)

    payload = {'lat': 'not-a-number', 'lon': 0}
    with pytest.raises(Exception) as exc:
        create_visita(db_session, vendedor.id, payload)
    assert 'Coordenadas inválidas' in str(exc.value)


def test_create_visita_coords_out_of_range(db_session):
    pais = Pais(nombre='Farland')
    db_session.add(pais)
    db_session.commit()
    db_session.refresh(pais)

    vendedor = Vendedor(nombre='Luis', email='luis@test.local', pais=pais.id)
    db_session.add(vendedor)
    db_session.commit()
    db_session.refresh(vendedor)

    payload = {'lat': 200.0, 'lon': 0}
    with pytest.raises(Exception) as exc:
        create_visita(db_session, vendedor.id, payload)
    assert 'Coordenadas fuera de rango' in str(exc.value)


def test_get_visitas_for_vendedor(db_session):
    pais = Pais(nombre='Some')
    db_session.add(pais)
    db_session.commit()
    db_session.refresh(pais)

    vendedor = Vendedor(nombre='Sara', email='sara@test.local', pais=pais.id)
    db_session.add(vendedor)
    db_session.commit()
    db_session.refresh(vendedor)

    # crear dos visitas directamente usando create_visita
    payload1 = {'lat': 1.0, 'lon': 1.0}
    payload2 = {'lat': 2.0, 'lon': 2.0}
    v1 = create_visita(db_session, vendedor.id, payload1)
    v2 = create_visita(db_session, vendedor.id, payload2)

    visitas = get_visitas_for_vendedor(db_session, vendedor.id)
    assert len(visitas) >= 2
    ids = {v.id for v in visitas}
    assert v1.id in ids and v2.id in ids
