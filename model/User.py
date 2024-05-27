import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

#Base = declarative_base()

#class User(Base):
#    __tablename__ = 'users'
#    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#    name = Column(String)
#    surname = Column(String)
#    mail = Column(String)
#    country = Column(String)
#    organization = Column(String)
#    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'))
#    role = relationship("Role", uselist=False)
