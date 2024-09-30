from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    telegram_id = Column(String, unique=True, nullable=False)
    registrations = relationship('Registration', back_populates='user')

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    registrations = relationship('Registration', back_populates='course')
    lessons = relationship('Lesson', back_populates='course')

class Registration(Base):
    __tablename__ = 'registrations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    user = relationship('User', back_populates='registrations')
    course = relationship('Course', back_populates='registrations')

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    bio = Column(Text)
    lessons = relationship('Lesson', back_populates='teacher')

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    date_time = Column(DateTime, nullable=False)
    topic = Column(String, nullable=False)
    
    course = relationship('Course', back_populates='lessons')
    teacher = relationship('Teacher', back_populates='lessons')
