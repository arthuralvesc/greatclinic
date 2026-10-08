import uuid
from datetime import date

from sqlalchemy import Date, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all ORM models. ORM models never leave the infrastructure layer."""


class PatientModel(Base):
    __tablename__ = "patients"
    __table_args__ = (
        UniqueConstraint("phone", name="patients_phone_key"),
        UniqueConstraint("email", name="patients_email_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320))
    phone: Mapped[str] = mapped_column(String(20))
    birth_date: Mapped[date] = mapped_column(Date)
