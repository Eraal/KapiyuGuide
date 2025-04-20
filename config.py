import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin@localhost/kapiyuguide'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'geraldpogi'