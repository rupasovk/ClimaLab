import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

#Base = declarative_base()

#class Role(Base):
#    __tablename__ = 'roles'
#    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#    name = Column(String)
#    # Добавьте другие столбцы для роли по вашему усмотрению
