"""
Modèles de base de données - SQLAlchemy
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

Base = declarative_base()

class Report(Base):
    """Modèle pour les rapports importés"""
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    file_size = Column(Integer, default=0)
    total_entries = Column(Integer, default=0)
    valid_entries = Column(Integer, default=0)
    error_entries = Column(Integer, default=0)
    status = Column(String(50), default='completed')  # pending, processing, completed, failed
    file_path = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    entries = relationship('FaxEntry', back_populates='report', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'file_size': self.file_size,
            'entries': self.total_entries,
            'valid': self.valid_entries,
            'errors': self.error_entries,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class FaxEntry(Base):
    """Modèle pour les entrées FAX individuelles"""
    __tablename__ = 'fax_entries'
    
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('reports.id'), nullable=False)
    fax_number = Column(String(20))
    caller_id = Column(String(100))
    recipient = Column(String(100))
    duration = Column(Integer, default=0)  # en secondes
    page_count = Column(Integer, default=0)
    status = Column(String(20), default='valid')  # valid, error
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    report = relationship('Report', back_populates='entries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'fax_number': self.fax_number,
            'caller_id': self.caller_id,
            'recipient': self.recipient,
            'duration': self.duration,
            'page_count': self.page_count,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }

class User(Base):
    """Modèle pour les utilisateurs"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255))
    full_name = Column(String(255))
    role = Column(String(20), default='user')  # admin, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active
        }

class AuditLog(Base):
    """Modèle pour les logs d'audit"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    action = Column(String(100))
    resource = Column(String(100))
    resource_id = Column(Integer)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'details': self.details,
            'created_at': self.created_at.isoformat()
        }
