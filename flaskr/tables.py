from sqlalchemy import exists, Column, Integer, String, ForeignKey, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# 实例化官宣模型 - Base 就是 ORM 模型
Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username =Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created = Column(DateTime, onupdate=datetime.now(), nullable=False, default=datetime.now())
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
