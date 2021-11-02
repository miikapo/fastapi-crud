from __future__ import annotations
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from fastapi_crud.config import CRUDConfig

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"

    id: str = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    employees: list[Employee] = relationship("Employee", back_populates="company")

    class Config(CRUDConfig):
        create_schema_skip_fields = ["id"]


class Employee(Base):
    __tablename__ = "employees"

    id: str = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    birthday = Column(Date)
    salary = Column(Numeric)
    shares_owned = Column(Integer)

    company_id: str = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    company: Company = relationship("Company", back_populates="employees")
