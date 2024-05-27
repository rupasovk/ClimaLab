from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import UUID
import uuid
import config

Base = declarative_base()

# Создание engine
engine = create_engine(config.DB_URL)
#Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    surname = Column(String)
    mail = Column(String)
    country = Column(String)
    organization = Column(String)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'))
    role = relationship("Role", uselist=False)


class Post(Base):
    __tablename__ = 'roles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    # Добавьте другие столбцы для роли по вашему усмотрению