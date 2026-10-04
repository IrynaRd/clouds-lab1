from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DATE, TEXT
from sqlalchemy.dialects.mysql import YEAR
from sqlalchemy.orm import relationship
from my_project.database import Base

class Film(Base):
    __tablename__ = 'film'
    id = Column(Integer, primary_key = True, autoincrement = True)
    title = Column(String(200), nullable = False)
    year = Column(YEAR, nullable = False)
    description = Column(String(450), nullable = False)
    budget = Column(DECIMAL(12, 3), nullable = False)
    
    facts = relationship("Fact", back_populates = "film", cascade = "all, delete-orphan")
    ratings = relationship("Rating", back_populates ="film", cascade = "all, delete-orphan")
    reviews = relationship("Review", back_populates ="film", cascade = "all, delete-orphan")

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True, autoincrement = True)
    nick_name = Column(String(45), nullable = False)
    email = Column(String(60), nullable = False, unique = True)
    registration_date = Column(DATE, nullable = False)
    
    ratings = relationship("Rating", back_populates ="user", cascade ="all, delete-orphan")
    reviews = relationship("Review", back_populates ="user", cascade ="all, delete-orphan")

class Fact(Base):
    __tablename__ = 'facts'
    id = Column(Integer, primary_key = True, autoincrement = True)
    description = Column(TEXT, nullable = False)
    film_id = Column(Integer, ForeignKey('film.id', ondelete = 'CASCADE', onupdate = 'CASCADE'), nullable = False)
    
    film = relationship("Film", back_populates ="facts")


class Rating(Base):
    __tablename__ = 'rating'
    film_id = Column(Integer, ForeignKey('film.id', ondelete ='CASCADE', onupdate ='CASCADE'), primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete ='CASCADE', onupdate ='CASCADE'), primary_key = True)
    points = Column(Integer, nullable=False)
    
    film = relationship("Film", back_populates = "ratings")
    user = relationship("User", back_populates = "ratings")

class Review(Base):
    __tablename__ = 'review'
    film_id = Column(Integer, ForeignKey('film.id', ondelete = 'CASCADE', onupdate = 'CASCADE'), primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete ='CASCADE', onupdate ='CASCADE'), primary_key = True)
    review_text = Column(TEXT, nullable=False)
    review_date = Column(DATE, nullable=False)
    
    film = relationship("Film", back_populates = "reviews")
    user = relationship("User", back_populates = "reviews")