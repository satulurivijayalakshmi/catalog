import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class GmailUser(Base):
    __tablename__ = 'gmailuser'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class GameType(Base):
    __tablename__ = 'gametype'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('gmailuser.id'))
    user = relationship(GmailUser, backref="gametype")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class GameName(Base):
    __tablename__ = 'gamename'
    id = Column(Integer, primary_key=True)
    name = Column(String(350), nullable=False)
    year = Column(String(150))
    developer = Column(String(150))
    publisher = Column(String(150))
    mode = Column(String(250))
    gameprogrammer = Column(String(500))
    gametypeid = Column(Integer, ForeignKey('gametype.id'))
    gametype = relationship(
        GameType, backref=backref('gamename', cascade='all, delete'))
    gmailuser_id = Column(Integer, ForeignKey('gmailuser.id'))
    gmailuser = relationship(GmailUser, backref="gamename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'year': self. year,
            'developer': self. developer,
            'publisher': self. publisher,
            'mode': self. mode,
            'gameprogrammer': self. gameprogrammer,
            'id': self. id
        }

engin = create_engine('sqlite:///games.db')
Base.metadata.create_all(engin)
