import os

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency to get a database session for each request
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

    accounts = relationship("Account", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="accounts")
    sub_accounts = relationship("SubAccount", back_populates="account")


class SubAccount(Base):
    __tablename__ = "sub_accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="sub_accounts")


Base.metadata.create_all(bind=engine)
