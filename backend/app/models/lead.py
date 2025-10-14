from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    
    # Lead Information
    name = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Real Estate Specific Fields
    purpose = Column(String(50), nullable=True)  # 'buy', 'sell', 'rent', 'invest'
    selected_category = Column(String(50), nullable=True)
    location = Column(String(200), nullable=True)
    budget = Column(String(100), nullable=True)
    timeline = Column(String(100), nullable=True)
    property_type = Column(String(100), nullable=True)  # 'apartment', 'villa', 'plot', etc.
    
    # Status & Metadata
    lead_status = Column(String(50), default='new')  # 'new', 'qualified', 'contacted', 'closed'
    lead_score = Column(Integer, default=0)  # 0-100 qualification score
    is_qualified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional Info
    notes = Column(Text, nullable=True)  # Any additional information captured


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    
    # Message Details
    role = Column(String(20))  # 'user' or 'assistant'
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    intent = Column(String(100), nullable=True)  # Detected intent: 'greeting', 'inquiry', 'objection', etc.
    sentiment = Column(String(50), nullable=True)  # 'positive', 'neutral', 'negative'


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    
    # Session Info
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Tracking
    message_count = Column(Integer, default=0)
    lead_captured = Column(Boolean, default=False)
    
    # User Info (optional, for analytics)
    user_ip = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)