from database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey


class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    ftype = Column(String(255), nullable=False, default='text')
    filepath = Column(String(255), unique=True)
    ctime = Column(DateTime())
    mtime = Column(DateTime())
    presentation_id = Column('presentation_id', Integer(), ForeignKey('presentation.id'))
    language = Column(String(30))

class PresentationUser(Base):
    __tablename__ = 'presentations_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    presentation_id = Column('presentation_id', Integer(), ForeignKey('presentation.id'))


class Presentation(Base):
    __tablename__ = 'presentation'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, default="New Presentation")
    ctime = Column(DateTime())
    mtime = Column(DateTime())
    translate = Column(Boolean())
    genimages = Column(Boolean())
    files = relationship('File', backref=backref('File'))