from typing import Optional
from sqlmodel import Field, SQLModel

class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    issuer_id: int = Field(index=True, unique=True)
    name: str
    sector: Optional[str] = None
    last_updated: Optional[str] = None # We can store the date we fetched it

    def __repr__(self):
        return f"<Company(id={self.id}, issuer_id={self.issuer_id}, name={self.name})>"
