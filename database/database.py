from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#engine = create_engine('postgresql+psycopg2://admin:1234@localhost:5432/ClimaLabTEST', echo=True)
#Session = sessionmaker(bind=engine)
#session = Session()

#Base = declarative_base()
#Base.metadata.create_all(engine)