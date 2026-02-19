from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    grade = Column(String, nullable=False)

    students = relationship("Student", back_populates="classroom")
    wali = relationship("User", back_populates="classroom")

class User(Base):
    __tablename__ = "penggunas"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)

    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    classroom = relationship("Class", back_populates="wali")
    student = relationship("Student", back_populates="user", uselist=False)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("penggunas.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))

    user = relationship("User", back_populates="student")
    classroom = relationship("Class", back_populates="students")
    grades = relationship("Grade", back_populates="student")

class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject = Column(String, nullable=False)
    score = Column(Integer, nullable=False)

    student = relationship("Student", back_populates="grades")

