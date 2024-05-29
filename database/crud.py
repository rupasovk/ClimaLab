from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import User, Role
import config

engine = create_engine(config.DB_URL)
SessionLocal = None


def get_db():
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(bind=engine)()
    return SessionLocal


def create_user(name, hashed_password, mail):
    print(name)
    print(hashed_password)
    print(mail)
    session = get_db()
    new_user = User(name=name, hashed_password=hashed_password, mail=mail)
    session.add(new_user)
    session.commit()
    session.close()
    return new_user


def read_users():
    session = get_db()
    users = session.query(User).all()
    session.close()
    return users


def update_user(user_id, name, password, email):
    session = get_db()
    user_to_update = session.query(User).filter_by(id=user_id).first()
    user_to_update.name = name
    user_to_update.password = password
    user_to_update.email = email
    session.commit()
    session.close()
    return user_to_update


def delete_user(user_id):
    session = get_db()
    user_to_delete = session.query(User).filter_by(id=user_id).first()
    session.delete(user_to_delete)
    session.commit()
    session.close()


# Аналогичные функции для CRUD-операций с Rule