from sqlalchemy.orm import Session
from typing import List
from app.models.client import Cliente


class ClientService:
    """Service to fetch clients assigned to a vendor.

    This service is read-only: clients are seeded in the DB (not created/updated via API).
    """

    def __init__(self, db: Session):
        self.db = db

    def get_clients_by_vendor(self, vendedor_id: int, skip: int = 0, limit: int = 100) -> List[Cliente]:
        return (
            self.db.query(Cliente)
            .filter(Cliente.vendedor_id == vendedor_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
