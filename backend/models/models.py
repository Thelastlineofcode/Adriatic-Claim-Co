"""
SQLAlchemy models for Adriatic Claim Co claim business.
All models include necessary fields and relationships.
Includes indexing for optimized queries.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum, Text, Index
from sqlalchemy.orm import relationship
from db import db
import enum


Base = db.Model

class ClaimStatusEnum(str, enum.Enum):
    submitted = "submitted"
    under_review = "under_review"
    pending_documents = "pending_documents"
    approved = "approved"
    paid = "paid"
    denied = "denied"
    abandoned = "abandoned"

class Owner(Base):
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    middle_name = Column(String(64), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    ssn = Column(String(11), nullable=True, index=True)  # formatted ###-##-####
    tax_id = Column(String(20), nullable=True, index=True)
    email = Column(String(120), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    address_line1 = Column(String(128), nullable=True)
    address_line2 = Column(String(128), nullable=True)
    city = Column(String(64), nullable=True)
    state = Column(String(2), nullable=True, index=True)
    postal_code = Column(String(12), nullable=True)
    country = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claims = relationship("Claim", back_populates="owner", cascade="all, delete-orphan")

class Holder(Base):
    __tablename__ = "holders"

    id = Column(Integer, primary_key=True)
    holder_name = Column(String(128), nullable=False, unique=True)
    holder_type = Column(String(64), nullable=True)
    contact_name = Column(String(128), nullable=True)
    contact_email = Column(String(120), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    address_line1 = Column(String(128), nullable=True)
    address_line2 = Column(String(128), nullable=True)
    city = Column(String(64), nullable=True)
    state = Column(String(2), nullable=True, index=True)
    postal_code = Column(String(12), nullable=True)
    country = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    claims = relationship("Claim", back_populates="holder", cascade="all, delete-orphan")
    holder_reports = relationship("HolderReport", back_populates="holder", cascade="all, delete-orphan")

class HolderReport(Base):
    __tablename__ = "holder_reports"

    id = Column(Integer, primary_key=True)
    holder_id = Column(Integer, ForeignKey('holders.id'), nullable=False)
    report_year = Column(Integer, nullable=False)
    report_file = Column(String(256), nullable=True)  # URL or file path
    file_hash = Column(String(64), nullable=True)
    submitted_at = Column(DateTime, nullable=True)

    holder = relationship("Holder", back_populates="holder_reports")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True)
    claim_number = Column(String(64), nullable=False, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey('owners.id'), nullable=False, index=True)
    holder_id = Column(Integer, ForeignKey('holders.id'), nullable=False, index=True)
    property_type = Column(String(64), nullable=False, index=True)
    reported_value = Column(Float, nullable=False, index=True)
    claim_status = Column(Enum(ClaimStatusEnum), default=ClaimStatusEnum.submitted, index=True)
    reporting_state = Column(String(2), nullable=False, index=True)
    dormancy_date = Column(DateTime, nullable=True, index=True)
    due_diligence_deadline = Column(DateTime, nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("Owner", back_populates="claims")
    holder = relationship("Holder", back_populates="claims")
    workflow_steps = relationship("WorkflowStep", back_populates="claim", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="claim", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_claims_state_dormancy_due_diligence', 'reporting_state', 'dormancy_date', 'due_diligence_deadline'),
    )

class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey('claims.id'), nullable=False, index=True)
    step_name = Column(String(128), nullable=False)
    status = Column(String(64), nullable=False)  # e.g., pending, completed
    assigned_to = Column(String(128), nullable=True)
    due_date = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)

    claim = relationship("Claim", back_populates="workflow_steps")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey('claims.id'), nullable=False, index=True)
    document_type = Column(String(64), nullable=False)
    file_name = Column(String(256), nullable=False)
    file_url = Column(String(512), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="documents")

class DueDiligenceAction(Base):
    __tablename__ = "due_diligence_actions"

    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey('claims.id'), nullable=False, index=True)
    action_type = Column(String(64), nullable=False)  # e.g., notice_sent, phone_call
    action_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    claim = relationship("Claim")
