""" database.py """

from flask_sqlalchemy import SQLAlchemy
from app import app
# import pymysql

# pymysql.install_as_MySQLdb()

SQLALCHEMY_BINDS = {
    'sensordata2' : 'mysql://***@***.mysql.pythonanywhere-services.com/***$***'
}

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://beastofwar:kmzway87aa@beastofwar.mysql.pythonanywhere-services.com/beastofwar$data"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
app.config["SQLALCHEMY_BINDS"] = SQLALCHEMY_BINDS


db = SQLAlchemy(app)

class UserData(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key = True)
    gold = db.Column(db.Integer())
    food = db.Column(db.Integer())
    slot = db.Column(db.Integer())
    total_win = db.Column(db.Integer())
    total_lose = db.Column(db.Integer())
    invitedBy = db.Column(db.Integer(), nullable = True)
    invited = db.Column(db.Integer())

    def __init__(self, id, gold, food, slot, total_win, total_lose, invitedBy, invited):
        self.id = id
        self.gold = gold
        self.food = food
        self.slot = slot
        self.total_win = total_win
        self.total_lose = total_lose
        self.invitedBy = invitedBy
        self.invited = invited


class CompanionData(db.Model):
    __tablename__ = "companion"
    companion_id = db.Column(db.Integer, primary_key = True)
    level = db.Column(db.Integer(), nullable = False, autoincrement = True)
    owner = db.Column(db.Integer())
    name = db.Column(db.Integer())
    previousClaim = db.Column(db.Integer())
    exp = db.Column(db.Integer())

    #Abilities
    ability1 = db.Column(db.VARCHAR())
    ability2 = db.Column(db.VARCHAR())
    ability3 = db.Column(db.VARCHAR())

    def __init__(self, level, owner, name, previousClaim, exp, ability1=None, ability2=None, ability3=None):
        self.level = level
        self.owner = owner
        self.name = name
        self.previousClaim = previousClaim
        self.exp = exp

        #Abilities
        self.ability1 = ability1
        self.ability2 = ability2
        self.ability3 = ability3


class PositionData(db.Model):
    __tablename__ = "position"
    id = db.Column(db.Integer, primary_key = True)
    position1 = db.Column(db.Integer())
    position2 = db.Column(db.Integer())
    position3 = db.Column(db.Integer())

    def __init__(self, id, position1, position2, position3):
        self.id = id
        self.position1 = position1
        self.position2 = position2
        self.position3 = position3

#Added by Gaëtan Poloin, https://poloin.ga
class BossArena(db.Model):
    __tablename__ = "arena"
    id = db.Column(db.Integer, primary_key=True)
    win = db.Column(db.Integer())
    defeat = db.Column(db.Integer())
    level = db.Column(db.Integer())
    b1_reward = db.Column(db.Integer())
    b2_reward = db.Column(db.Integer())
    b3_reward = db.Column(db.Integer())
    b4_reward = db.Column(db.Integer())
    b5_reward = db.Column(db.Integer())

    def __init__(self, id, win, defeat, level, b1_reward, b2_reward, b3_reward, b4_reward, b5_reward):
        self.id = id
        self.win = win
        self.defeat = defeat
        self.level = level
        self.b1_reward = b1_reward
        self.b2_reward = b2_reward
        self.b3_reward = b3_reward
        self.b4_reward = b4_reward
        self.b5_reward = b5_reward

'''
class AbilityStorage__(db.Model):
    __tablename__ = "ability"
    id = db.Column(db.Integer, primary_key=True)
    for loop in range(1, 14):
        pass

    books = []

    def __init__(self, id, books=[book1, book2, book3, book4, book5, book6, book7, book8, book9, book10, book11, book12, book13, book14]):
        self.id = id
        self.books = books
'''

class AbilityStorage(db.Model):
    __tablename__ = "ability"
    id = db.Column(db.Integer, primary_key=True)
    book1 = db.Column(db.Integer())
    book2 = db.Column(db.Integer())
    book3 = db.Column(db.Integer())
    book4 = db.Column(db.Integer())
    book5 = db.Column(db.Integer())
    book6 = db.Column(db.Integer())
    book7 = db.Column(db.Integer())
    book8 = db.Column(db.Integer())
    book9 = db.Column(db.Integer())
    book10 = db.Column(db.Integer())
    book11 = db.Column(db.Integer())
    book12 = db.Column(db.Integer())
    book13 = db.Column(db.Integer())
    book14 = db.Column(db.Integer())

    def __init__(self, id, book1, book2, book3, book4, book5, book6, book7, book8, book9, book10, book11, book12, book13, book14):
        self.id = id
        self.book1 = book1
        self.book2 = book2
        self.book3 = book3
        self.book4 = book4
        self.book5 = book5
        self.book6 = book6
        self.book7 = book7
        self.book8 = book8
        self.book9 = book9
        self.book10 = book10
        self.book11 = book11
        self.book12 = book12
        self.book13 = book13
        self.book14 = book14
