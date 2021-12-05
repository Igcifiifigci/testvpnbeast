""" module.py """

from telebot import types
from characters import characters
import time, re
from database import db, UserData, CompanionData, PositionData

DATA = {}

def setData(unique, data):
    DATA[unique] = data


def getData(unique, reset = True):
    rv = DATA.get(unique)
    if rv and reset:
        del DATA[unique]

    return rv




def Mkd():
    return types.InlineKeyboardMarkup()

def Btn(txt: str=None,text: str=None, calldata: str="btn call"):
    if txt:
        return types.InlineKeyboardButton(txt, callback_data=calldata)
    elif text:
        return types.InlineKeyboardButton(text, callback_data=calldata)


def button(*args, **kwargs):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True, **kwargs)
    for arg in args:
        instance = type(arg)
        if instance == str:
            markup.row(types.KeyboardButton(arg))
        elif instance in [list, tuple]:
            markup.row(*[types.KeyboardButton(x) for x in arg])

    return markup


def inline(*args, **kwargs):
    markup = types.InlineKeyboardMarkup(**kwargs)
    for arg in args:
        instance = type(arg)
        if instance == str:
            markup.row(types.InlineKeyboardButton(arg, callback_data = arg))
        elif instance in [list, tuple]:
            markup.row(*[types.InlineKeyboardButton(x, callback_data = x) for x in arg])

    return markup


def getTotalGold(previousClaim, gpm, max = None):
    timeNow = int(time.time())

    if (timeNow - previousClaim <= 60):
        return 0

    total = ((timeNow - previousClaim) // 60) * gpm

    if max and total > max:
        total = max

    return total


def removeMarkdown(string):
    return re.sub(r"[*_`]", "", string)


def createMention(from_user):
    return f"[{removeMarkdown(from_user.first_name)}](tg://user?id={from_user.id})"


def getBarPersentase(current, total):
    a = "█"
    b = "▒"

    persen = round(current / total * 100)

    if persen <= 0:
        string = a * 1 + b * 9
    elif persen >= 100:
        string = a * 10
    elif persen >= 90:
        string = a * 9 + b * 1
    elif persen >= 80:
        string = a * 8 + b * 2
    elif persen >= 70:
        string = a * 7 + b * 3
    elif persen >= 60:
        string = a * 6 + b * 4
    elif persen >= 50:
        string = a * 5 + b * 5
    elif persen >= 40:
        string = a * 4 + b * 6
    elif persen >= 30:
        string = a * 3 + b * 7
    elif persen >= 20:
        string = a * 2 + b * 8
    else:
        string = a * 1 + b * 9

    return string


def getExpRequirement(level):
    return round(30 * (level + 1) ** 1.8)


def getTotalExpRequirement(levelFrom, levelTo):
    return sum([getExpRequirement(level) for level in range(levelFrom, levelTo)])


def addExp(companion_id, exp, companion = None):
    if not companion:
        # cur.execute(f"SELECT * FROM companion WHERE companion_id = {companion_id}")
        # companion = cur.fetchone()
        companion = CompanionData.query.filter_by(companion_id = companion_id).first()

    if companion.level >= 100:
        return

    companionClass = characters[companion.name]
    currentExp = companion.exp
    totalExp = currentExp + exp

    for i in range(companion.level, 101):
        a = getTotalExpRequirement(companion.level, i)
        if a > totalExp:
            nextLevel = i - 1
            break
    else:
        totalExp = 0
        nextLevel = 100

    b = getTotalExpRequirement(companion.level, nextLevel)

    # print(a, b, totalExp, exp)
    if totalExp >= b:
        exp = totalExp - b
    else:
        exp = totalExp

    # cur.execute(f"UPDATE companion SET level = {nextLevel}, exp = {exp} WHERE companion_id = {companion_id}")
    CompanionData.query.filter_by(companion_id = companion_id).update({CompanionData.level: nextLevel, CompanionData.exp: exp})
    db.session.commit()
