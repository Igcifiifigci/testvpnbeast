""" run.py """

from flask import request
from telebot import types

#from room import *
from Battle import *
from Arena import *
from Quest import *

from tbot import bot
from decorators import loadingFixed
from app import app
from database import db, UserData, CompanionData, PositionData, BossArena, AbilityStorage
from util import *

import boss
import characters
import elements
import module
import abilities

import time, datetime, re, os, sys, traceback


BOSS = boss.bossList
QUEST_TIMER = {'last_reset': 0}

SELECTED_COMPANION = {}
DATA = {}
CHARACTERS_NAME = [character.name for character in characters.characters]
ABILITIES_NAME = [ability.name for ability in abilities.abilities]
CHARACTERS_NAME_ASCII_ONLY = [
    character.name.encode("ascii", "ignore")\
      .decode()\
        .strip()\
    for character in characters.characters
]


PROCESSED = []
admin_data = read_json("mysite/admin.json")
ADMINS = list(admin_data.values())


'''
@app.errorhandler(Exception)
def error400(e):
    #bot.send_message(862672392, str(e))
    #return str(e)
    return "OK"
'''
@app.errorhandler(400)
def error400(e):
    #Too old msg
    #can't edit
    #can't delete
    return ".OK"

#'''
"""
@app.errorhandler(Exception)
def error(e):
    #if "Too Many Requests:" in str(e):
    #    return "OK"
    if "query is too old and response timeout expired or query ID is invalid" in str(e):
        return "OK"
    #elif "specified new message content and reply markup are exactly the same" in str(e):
    #    return "OK"


    #print("#######################\n"+str(e)+"\n#######################")
    exception_type, exception_object, exception_traceback = sys.exc_info()

    bot.send_message(1293332725, f"## Exception occured ##\nError type: {exception_type}\nError: {e}\n#######################")
    return ".OK"
"""
#'''

TEMP_ALLOWED = []

@app.route("/" + bot.token, methods=["POST"])
def getMessage():
    global PROCESSED

    message = request.get_json()
    if not message:
        return "OK"

    try:
        x = message['message']['text']
    except: #IF NOT MESSAGE/COMMAND
        try:
            x = message['callback_query'] #IF NOT CALLBACK
        except:
            return "OK" #CANCEL

    message = types.Update.de_json(message)
    if not message.update_id in PROCESSED:
        try:
            if message.message.text != None: #Edited messages #New member, channel, etc..
                if time.time()-(60*15) > message.message.date:
                    return ".OK" #Message was sent AND not processed since more than 15 minutes ago, so we don't care to avoid spam when bot goes off for some times
            #if (not message.message.from_user.id in ADMINS or not message.message.from_user.id in TEMP_ALLOWED ) and not message.message.text.startswith("/quest"):
            #    print(message.message.from_user.id, "tried to use the bot")
            #    return ".OK"
        except:
            pass

        bot.process_new_updates([message])
        PROCESSED.append(message.update_id)

    if len(PROCESSED) > 50_000:
        PROCESSED = []

    #if datetime.datetime.now().hour == 1:
    #    QUEST_TIMER = {}
    global QUEST_TIMER
    if int(time.time()) - 60*60*24 > QUEST_TIMER['last_reset']:
        QUEST_TIMER = {}
        QUEST_TIMER['last_reset'] = int(time.time())

    return ".OK"


@app.route("/", methods=["GET"])
def home():
    #print("Something got home page")
    return "OK"

@bot.message_handler(commands=["test"])
def test(message):

    bot.reply_to(message, "Test achieved, message is: " + str(message))
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    bot.send_message(message.from_user.id, "Test achieved, message is: " + str(message))
    print("YEAAAH", datetime.datetime.now())
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    """
    def timeout(when):
        print("TIMED OUT IT IS", time.time(), "and it was", when)

    x = threading.Timer(20, timeout, [time.time()])
    x.start()

    print("OK OK OK OK")
    x.stop()
    print("STOPPED")
    """

@bot.message_handler(commands=["mk"])
def markdown(message):

    bot.reply_to(message, "*Bold*, _Italic_")



@bot.message_handler(commands=["start"])
def start(message):
    if "group" in message.chat.type:
        bot.reply_to(message, "To start your adventure, please go in pm")
        return

    user = UserData.query.filter_by(id=message.from_user.id).first()
    if not user is None:
        bot.reply_to(message, "You already started your aventure in the past!")
        return


    try:
        invitedBy = message.text.split(" ")[-1]
        invitedBy = invitedBy if invitedBy.isdigit() else None
        addData = UserData(message.from_user.id, 1000, 500, 1, 0, 0, 0, invitedBy)
        db.session.add(addData)
        db.session.commit()
    except:
        try:
            db.session.rollback()
        except:
            pass

        if CompanionData.query.filter_by(owner=message.from_user.id).first():
            commands(message)
            return


    if invitedBy:
        invit = UserData.query.filter_by(id=invitedBy).first()
        if invit.invited in [10,20,30,40,50]:
            a = abilities.abilities

            book = a[ random.randint(0, len(a)-1) ]

            bot.send_message(invitedBy, f"*Congratulation !* You reached {invit.invited} referral.\nYou won 1 {book.emote}{book.name} book")


    char_name = [CHARACTERS_NAME[i:i + 2]
        for i in range(0, len(CHARACTERS_NAME), 2)]
    markup = module.inline(*char_name)
    bot.send_photo(message.from_user.id,
                    open("mysite/images/Angel.jpg", "rb"),
                      caption="To begin your adventure 🚩, select one companion to follow you ⚔️",
                        reply_markup=markup)


@bot.message_handler(commands=["commands"])
def commands(message):
    if isInBattleOrArena(message) == 0:
        return

    msg = "/start - to start this bot\n/storage - to check your inventory\n/companion - to check your companion\n/team - create your team and battle with friends\n/store - to check items to buy\n/battle - reply to someone in group to have a battle\n/arena - Launch an Arena and fight boss in pm!\n/feed - to feed companion in order to gain exp\n/referral - invite friends and get rewards"

    if message.chat.type in ["supergroup", "group"]:
        bot.reply_to(message, msg)
    else:
        bot.send_message(message.from_user.id, msg)


@bot.callback_query_handler(func=lambda call: call.data in CHARACTERS_NAME)
@loadingFixed
def selectChar(call):
    index = CHARACTERS_NAME.index(call.data)
    character = characters.characters[index]

    msg = f"""        {character.name}\n\nElement : {character.element}\nHP : {character.hp}\nAttack : {character.attack}\nSpeed : {character.speed}\n\n💰 Gold production/min : {character.gpm}\n🗄 Max gold : {character.maxGold}\n\n⚔️ Default Moveset :\n*{character.first_skill_name}* : {character.first_skill_info}\n\n⚔️ Moveset unlock at level 50:\n*{character.second_skill_name}* : {character.second_skill_info}\n    """


    SELECTED_COMPANION[call.message.chat.id] = character
    markup = module.inline(["Confirm", "Back"])
    bot.edit_message_media(types.InputMedia("photo",
                            open(character.imagePath, "rb"),
                              caption=msg,
                                parse_mode="Markdown"),
                            chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                                reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "Back")
@loadingFixed
def backToSelectChar(call):
    bot.answer_callback_query(callback_query_id=call.id)
    msg = "Select one companion to follow you ⚔️"
    char_name = [CHARACTERS_NAME[i:i + 2]
        for i in range(0, len(CHARACTERS_NAME), 2)]
    markup = module.inline(*char_name)
    bot.edit_message_media(types.InputMedia("photo", open("mysite/images/Angel.jpg", "rb"), caption=msg),
                           chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "Confirm")
def confirmSelect(call):
    #bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

    data = CompanionData.query.filter_by(owner=call.message.chat.id).all()
    myCompanionNameList = [CHARACTERS_NAME[x.name] for x in data]

    user = UserData.query.filter_by(id=call.message.chat.id).first()
    if user.slot <= len(myCompanionNameList):
        bot.answer_callback_query(callback_query_id=call.id, text="You don't have enough slot")
        return

    character = SELECTED_COMPANION[call.message.chat.id]
    del SELECTED_COMPANION[call.message.chat.id]
    if character.name in myCompanionNameList:
        bot.answer_callback_query(callback_query_id=call.id, text="You already have this companion")
        return

    addData = CompanionData(1, call.message.chat.id, CHARACTERS_NAME.index(
        character.name), int(time.time()), 0)
    db.session.add(addData)
    db.session.commit()

    msg = f"""Congratulations 🎊\nYou have selected {character.name} to be your companion.\n\nUse /commands to see command lists.\n\nLet the adventure begin ⚔️\n        """
    bot.edit_message_text(msg, chat_id=call.message.chat.id, message_id=call.message.message_id)



def isInBattleOrArena(msg, isCall=False):
    if not isCall:
        if not noInRoomBattle(msg.from_user.id):
            try:
                bot.delete_message(msg.chat.id, msg.message_id)
            except:
                bot.reply_to(msg, "You are in battle. End it before doing anything else")
            return 0

        if not noInArena(msg.from_user.id):
            try:
                bot.delete_message(msg.chat.id, msg.message_id)
            except:
                bot.reply_to(msg, "You opened Arena's gate. Close them before doing anything else")
            return 0

        return 1

    elif isCall:
        if not noInRoomBattle(msg.from_user.id):
            return 0
        if not noInArena(msg.from_user.id):
            return 0

        return 1

def sortAbilityList(a):
    bkL = []
    bkrL = []

    for book in a.__dict__:
        if book == "_sa_instance_state" or book == "id":
            pass
        else:
            bkL.append(book)

    aa = [x for x in bkL if len(x) > 5]
    b = [x for x in bkL if len(x) == 5]
    aa = sorted(aa)
    b = sorted(b)
    bkL = b+aa

    for elem in bkL:
        nbOfBook = a.__dict__[elem]
        bkrL.append(nbOfBook)

    return bkL, bkrL

def getAbilityMsg(ability, message):
    usableBy = ""
    for user in ability.useBy:
        usableBy += " "+user

    msg = f"*Name:*\n _{ability.name}_\n\n *Effect:*\n _{ability.skills}_\n\n *Can be used by:*\n _{usableBy}_"


    if not isInBattleOrArena(message) == 0:
        mkp = module.Mkd()
        mkp.add(
            module.Btn(
              txt="Learn",
                calldata = f"learnA{ability.number}|{message.from_user.id}"
            )
        )

    return msg, mkp


@bot.message_handler(commands=["storage"])
def getStorageData(message):
    if isInBattleOrArena(message) == 0:
        return

    if message.from_user.id in ADMINS and len(message.text.split(" ")) > 1:
        user = message.text.split(" ")[1]
    else:
        user = message.from_user.id

    data = UserData.query.filter_by(id=user).first()
    ability = AbilityStorage.query.filter_by(id=user).first()

    if data is None:
        return bot.reply_to(message, "Sorry, this user does not exist")

    if ability is None:
        try:
            createUser = AbilityStorage(user, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            db.session.add(createUser)
            db.session.commit()
            ability = AbilityStorage.query.filter_by(id=user).first()
        except Exception as e:
            bot.reply_to(message, "Hi, sorry but a bug occured.\nCould you transfer this message to the bot developer? Thanks.\n\n"+int(time.time())+" "+str(e))
            return

    bkL, bkrL = sortAbilityList(ability)

    for x in bkrL:
        if x == 0:
            books = "\nYou have 0 books yet."
        else:
            books = ""
            break
    i=0
    for elem in bkL:
        book = bkL[i]
        numb = bkrL[i]
        nb = int(book[4:])
        name = abilities.abilities[nb-1].name

        if numb > 0:
            books += f"\n /a{nb}  {name} book ({numb})"

        i+=1

    if message.chat.type in ["supergroup", "group"]:
        if not data:
            bot.reply_to(message, "Data not found")
        else:
            if user != message.from_user.id:
                bot.reply_to(message, f"Stats of {user}\n\n💰 Gold: _{data.gold}_\n🍇 Food: _{data.food}_\n\n*Ability's books:* _{books}_")
                return
            bot.reply_to(message, f"💰 Gold: _{data.gold}_\n🍇 Food: _{data.food}_\n\n*Ability's books:* _{books}_")


    else:
        if user != message.from_user.id:
            bot.send_message(message.from_user.id, f"Stats of {user}\n\n💰 Gold: _{data.gold}_\n🍇 Food: _{data.food}_\n\n*Ability's books:* _{books}_")
        else:
            bot.send_message(message.from_user.id, f"💰 Gold: _{data.gold}_\n🍇 Food: _{data.food}_\n\n*Ability's books:* _{books}_")


@bot.message_handler(commands=["send"])
def send(message):
    if isInBattleOrArena(message) == 0:
        return

    sender = message.from_user.id

    #Check if it's a reply
    if message.chat.type in ["supergroup", "group"] and message.reply_to_message:
        #Check if it's not a self reply
        if message.reply_to_message.from_user.id != message.from_user.id:
            amount = message.text.split(" ")[1]
            receiver = message.reply_to_message.from_user

            #We do the transfer, but first, check if sender have enough gold
            try:
                data = UserData.query.filter_by(id=sender).first()
            except:
                bot.reply_to(message, "Cannot fetch data")
                return

            if int(amount) > 0:
                if int(data.gold) >= int(amount): #Sender have enough
                    #So, we remove gold from sender
                    UserData.query.filter_by(id = sender).update({UserData.gold: UserData.gold - int(amount)})
                    #We add gold to recipient
                    UserData.query.filter_by(id = receiver.id).update({UserData.gold: UserData.gold + int(amount)})
                    db.session.commit()

                    bot.reply_to(message, "You successfully sent " + str(amount) + " Gold 💰 to " + module.createMention(receiver) + "!")
                    bot.send_message(sender, "You sent " + str(amount) + "💰 to " + module.createMention(receiver))

                else:
                    bot.reply_to(message, "You don't have enough gold. Check your balance with /storage \n If you have enough, you probably misspelled the command. It's /send <amount> <recipient>")
            else:
                bot.reply_to(message, "Amount of sent gold can't be negative. Send at least 1💰 gold")

        else:
            bot.reply_to(message, "You can't send money to yourself..")

    else: #It's not, so we fallback with default command
        try:
            amount = message.text.split(" ")[1]
            receiver = message.text.split(" ")[2]

            if amount.isdigit(): #If amount is an amount
                if receiver.isdigit(): #If receiver is stated with his ID
                    #Check if it's not the sender ID
                    if message.from_user.id != receiver:

                        #We check if sender have enough gold
                        data = UserData.query.filter_by(id=message.from_user.id).first()

                        if int(amount) > 0:
                            if int(data.gold) >= int(amount): #Sender have enough
                                try:
                                    #So, we remove gold from sender
                                    UserData.query.filter_by(id = sender).update({UserData.gold: UserData.gold - int(amount)})
                                    #We add gold to recipient
                                    UserData.query.filter_by(id = receiver).update({UserData.gold: UserData.gold + int(amount)})
                                    db.session.commit()

                                    try:
                                        bot.reply_to(message, "You successfully sent " + str(amount) + " Gold 💰 to " + str(receiver) + "!")
                                        bot.send_message(sender, "You sent " + str(amount) + "💰 to " + str(receiver))
                                    except:
                                        bot.reply_to(message, "ERROR: Can't send messages (If you see this, there is big problem lmao)")
                                except:
                                    bot.reply_to(message, "ERROR: Can't send money")
                            else:
                                bot.reply_to(message, "You don't have enough gold. Check your balance with /storage \n or maybe you misspelled the command. It's /send <amount> <recipient>")
                        else:
                            bot.reply_to(message, "Amount of sent gold can't be negative. Send at least 1💰 gold")
                    else:
                        bot.reply_to(message, "You can't send to yourself..")
                else:
                    bot.reply_to(message, "You need to state the receiver with their ID")
            else:
                bot.reply_to(message, "You need to give the amount with numbers")
        except:
            bot.reply_to(message, "You didn't stated the recipient and/or the amount of the transfer. Try replying to the recipient and type /send <amount>")


@bot.message_handler(commands=["companion"])
def getCompanionData(message):
    if isInBattleOrArena(message) == 0:
        return

    if "group" in message.chat.type:
        bot.reply_to(message, "This is a PM only command.")
    else:
        companionList = CompanionData.query.filter_by(owner=message.from_user.id).all()

        if len(companionList) == 0:
            bot.reply_to(message, "You don't have any companion yet. Buy one in /store")
            return

        module.setData(message.from_user.id, companionList)
        msg = ""
        current_gold = 0
        for i, companion in enumerate(companionList):
            companionObject = characters.characters[companion.name](companion.level)
            name = companionObject.name

            user = UserData.query.filter_by(id=message.from_user.id).first()
            companions = CompanionData.query.filter_by(owner=message.from_user.id).all()

            msg += f"{i + 1}. _{name}_ - _Level {companion.level}_\n"
            current_gold += module.getTotalGold(companion.previousClaim, companionObject.gpm, max=companionObject.maxGold)

        msg += f"\nSlots used: {len(companions)}/{user.slot}"
        msg += f"\nCurrent gold: _{round(current_gold)}_"
        markup = module.inline(["Claim gold", "Increase slot"])

        bot.reply_to(message, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "Claim gold")
def claimGold(call):
    if isInBattleOrArena(call) == 0:
        return

    #bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

    def getTotalGold(companion):
        companionObject = characters.characters[companion.name](companion.level)
        return module.getTotalGold(companion.previousClaim, companionObject.gpm, max=companionObject.maxGold)

    user = UserData.query.filter_by(id=call.message.chat.id).first()
    companionList = module.getData(call.message.chat.id)
    current_gold = map(getTotalGold, companionList)
    current_gold = round(sum(list(current_gold)))

    if current_gold < 10:
        bot.answer_callback_query(callback_query_id=call.id, text="Minimum claim: 10")
        return

    if user.invitedBy:
        UserData.query.filter_by(id=user.invitedBy).update({UserData.gold: UserData.gold + 10000})
        bot.send_message(user.invitedBy, f"*Congratulation !* {module.removeMarkdown(call.from_user.first_name)} claimed their gold 💰 for the first time , you received 10,000 💰 into your storage")

    user.gold += current_gold
    user.invitedBy = None

    CompanionData.query.filter_by(owner=call.message.chat.id).update({CompanionData.previousClaim: int(time.time())})
    db.session.commit()
    bot.answer_callback_query(callback_query_id=call.id, text=f"Successfully claim {current_gold} gold")

    msg = call.message.text[:-2] + " 0"
    markup = module.inline(["Increase slot"])

    bot.edit_message_text(msg, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "Increase slot")
@loadingFixed
def increaseSlot(call):
    if isInBattleOrArena(call) == 0:
        return

    #bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)

    user = UserData.query.filter_by(id=call.message.chat.id).first()

    if user.slot >= 12:
        bot.answer_callback_query(callback_query_id=call.id, text="You already reached maximum slot capacity")
        return

    price = [25000, 50000, 75000, 125000, 200000, 350000, 450000, 700000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000]

    msg = f"Are you sure you want to spend {price[user.slot - 1]} to increase slot to {user.slot + 1}?\nYour current gold is : {user.gold}"

    markup = module.Mkd()
    markup.add(
        module.Btn(txt="Confirm", calldata="ConfirmSlot"),
        module.Btn(txt="Back", calldata="BackSlot")
    )
    bot.edit_message_text(msg, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "BackSlot")
@loadingFixed
def backToCompanion(call):
    if isInBattleOrArena(call) == 0:
        return

    timeNow = int(time.time())

    companionList = CompanionData.query.filter_by(
        owner=call.message.chat.id).all()

    module.setData(call.message.chat.id, companionList)
    msg = ""
    current_gold = 0

    for i, companion in enumerate(companionList):
        companionObject = characters.characters[companion.name](companion.level)
        name = companionObject.name
        msg += f"{i + 1}. _{name}_ - _Level {companion.level}_\n"
        current_gold += module.getTotalGold(companion.previousClaim,
                                              companionObject.gpm,
                                                max=companionObject.maxGold)

    msg += f"\nCurrent gold: _{round(current_gold)}_"
    markup = module.inline(["Claim gold", "Increase slot"])
    bot.edit_message_text(msg,
                            chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                                reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "ConfirmSlot")
@loadingFixed
def confirmAddSlot(call):
    if isInBattleOrArena(call) == 0:
        return

    #bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)

    user = UserData.query.filter_by(id=call.message.chat.id).first()
    price = [25000, 50000, 75000, 125000, 200000, 350000, 450000, 700000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000]
    price = price[user.slot - 1]

    if price > user.gold:
        bot.send_message(call.message.chat.id, f"You don't have {price} gold")
        return

    user.slot += 1
    user.gold -= price
    db.session.commit()

    bot.send_message(call.message.chat.id, "You successfully bought a new slot!")



""" Abilities """

@bot.message_handler(func=lambda message: message.text.startswith("/a") and len(message.text) <= 4)
def ViewAbilities(message):
    if message.text[2:].isdigit():
        ab = int(message.text[2:])
        ab = ab-1

        for ability in abilities.abilities:
            if ability.number == ab:
                a = ability
                break

        msg, mkp = getAbilityMsg(a, message)
        bot.reply_to(message, msg, reply_markup=mkp)

@bot.callback_query_handler(func=lambda call: call.data.startswith("useA"))
@loadingFixed
def useAbility(call):
    if isInBattleOrArena(call, isCall=True) == 1:
        return

    book = int(call.data[4:].split("|")[0])
    roomBattle = ROOM_BATTLE[call.from_user.id]

    if roomBattle.player1_info.id == call.from_user.id:
        c = roomBattle.p1Companion(get=True)
    elif roomBattle.player2_info.id == call.from_user.id:
        c = roomBattle.p2Companion(get=True)
    else:
        bot.answer_callback_query(callback_query_id=call.id, text="Not your ability page")
        return

    if roomBattle.player1_turn:
        if roomBattle.isLocked["p1"]["state"]:
            if roomBattle.ability_msg:
                bot.edit_message_text(f"You are locked, for still {roomBattle.isLocked['p1']['until']} rounds", chat_id=roomBattle.ability_msg.chat.id, message_id=roomBattle.ability_msg.id)
            else:
                bot.reply_to(call.message, f"You are locked, for still {roomBattle.isLocked['p1']['until']} rounds")
            return

        if roomBattle.leftUse["p1"] == 0:
            bot.answer_callback_query(callback_query_id=call.id, text="You used all of your available abilities - nd you shouldn't see this")
            return

    else:
        if roomBattle.isLocked["p2"]["state"]:
            bot.answer_callback_query(callback_query_id=call.id, text=f"Abilities locked for still {roomBattle.isLocked['p2']['until']} rounds")
            #if roomBattle.ability_msg:
                #bot.edit_message_text(f"You are locked, for still {roomBattle.isLocked['p2']['until']} rounds", chat_id=roomBattle.ability_msg.chat.id, message_id=roomBattle.ability_msg.id)
            #else:
                #bot.reply_to(call.message, f"You are locked, for still {roomBattle.isLocked['p2']['until']} rounds")
            return

        if roomBattle.leftUse["p2"] == 0:
            if roomBattle.ability_msg:
                bot.answer_callback_query(callback_query_id=call.id, text="You used all of your available abilities - nd you shouldn't see this")
            return


    cmpData = CompanionData.query.filter_by(owner=call.from_user.id, name=c.id-1).first()

    if int(cmpData.ability1) == book or int(cmpData.ability2) == book or int(cmpData.ability3) == book:
        msg = roomBattle.ability(book)
        msg = ""

        if roomBattle.ability_msg:
            msg = bot.edit_message_text(f"*{c.name}* used an ability, *{abilities.abilities[book].name}*\n\nEffects: _{abilities.abilities[book].skills}_\n{msg}", chat_id=roomBattle.ability_msg.chat.id, message_id=roomBattle.ability_msg.id)
            roomBattle.ability_msg = msg
        else:
            msg = bot.reply_to(call.message, f"*{c.name}* used an ability, *{abilities.abilities[book].name}*\n\nEffects: _{abilities.abilities[book].skills}_\n{msg}")
            roomBattle.ability_msg = msg

    else:
        try:
            bot.edit_message_text("Your companion didn't learned this Ability - wtf?", chat_id=roomBattle.ability_msg.chat.id, message_id=roomBattle.ability_msg.id)
        except:
            pass

@bot.callback_query_handler(func=lambda call: call.data.startswith("learnA"))
def whoLearnAbility(call):
    book = str(int(call.data[6:].split("|")[0]))
    ability = abilities.abilities[int(book)]
    data = AbilityStorage.query.filter_by(id=call.from_user.id).first()
    bkL, bkrL = sortAbilityList(data)


    bookTc = "book"+str(int(book)+1)

    i=0
    for elem in bkL:
        if elem == bookTc:
            value = bkrL[i]

            if value == 0:
                bot.send_message(call.message.chat.id, "You don't have this Ability's book")
                return
        i+=1


    data = CompanionData.query.filter_by(owner=call.from_user.id).all()
    markup = module.Mkd()

    Book = int(book)
    i=1
    for cmps in data:
        Companion = characters.characters[cmps.name]
        if Companion.elem.emote in ability.useBy:

            if cmps.ability1 == Book or cmps.ability2 == Book or cmps.ability3 == Book:
                if len(data) == i:
                    bot.answer_callback_query(callback_query_id=call.id, text="Your companion(s) already learned this ability.")
                    return
            else:
                markup.add(
                    module.Btn(
                        text=Companion.name,
                          calldata = f"learnC-{Companion.name_ne}-{Book}-{cmps.name}|{call.from_user.id}"
                    )
                )
        i+=1

    bot.edit_message_text(f"Please, select the companion you want to learn *{ability.name}*",
        chat_id=call.message.chat.id,
          message_id=call.message.message_id,
            reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("learnC-"))
def learnAbility(call):
    charac_name = call.data.split("-")[1]
    book = call.data.split("-")[2]
    abN = int(book)
    charac_id = int(call.data.split("-")[3].split("|")[0])

    ability = abilities.abilities[abN]

    #Does companion has enough abilities left
    cmpData = CompanionData.query.filter_by(owner=call.from_user.id, name=charac_id).first()

    if cmpData.ability1 != None and cmpData.ability2 != None and cmpData.ability3 != None:

        ab1 = abilities.abilities[int(cmpData.ability1)]
        ab2 = abilities.abilities[int(cmpData.ability2)]
        ab3 = abilities.abilities[int(cmpData.ability3)]

        markup = module.Mkd()
        markup.add(
            module.Btn(
              text=ab1.name,
                calldata = f"abilityR{1}-B{ability.number}-O{charac_id}|{call.from_user.id}"),
            module.Btn(
              text=ab2.name,
                calldata = f"abilityR{2}-B{ability.number}-O{charac_id}|{call.from_user.id}"),
            module.Btn(
              text=ab3.name,
                calldata = f"abilityR{3}-B{ability.number}-O{charac_id}|{call.from_user.id}")
        )
        markup.add(
            module.Btn(
              text="Cancel",
                calldata = f"abilityC|{call.from_user.id}")
        )

        bot.edit_message_text("Your 3 abilities slots are full.. \nYou can replace one of them or just cancel",
            chat_id=call.message.chat.id,
              message_id=call.message.message_id,
                reply_markup=markup)

        return

    # cmpData.ability1 == None or cmpData.ability2 == None or cmpData.ability3 == None:

    #We remove the book from the user
    remBook(call.from_user.id, abN)

    #We give the ability to the selected companion
    if cmpData.ability1 == None and not cmpData.ability1 == ability.number:
        CompanionData.query.filter_by(owner=call.from_user.id, name=charac_id).update({CompanionData.ability1: ability.number})
    elif cmpData.ability2 == None and not cmpData.ability2 == ability.number:
        CompanionData.query.filter_by(owner=call.from_user.id, name=charac_id).update({CompanionData.ability2: ability.number})
    elif cmpData.ability3 == None and not cmpData.ability3 == ability.number:
        CompanionData.query.filter_by(owner=call.from_user.id, name=charac_id).update({CompanionData.ability3: ability.number})

    else:
        bot.edit_message_text("Thanks you spammy user. One more and your account will be reset.",
            chat_id=call.message.chat.id,
              message_id=call.message.message_id)

    db.session.commit()

    comp = characters.characters[charac_id]

    bot.edit_message_text(f"Congrats, *{comp.name}* learned *{ability.name}*",
        chat_id=call.message.chat.id,
          message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ability"))
def handleAbility(call):
    action = call.data[7:8]

    if action == "C":
        bot.answer_callback_query(callback_query_id=call.id, text="You cancelled the process")
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif action == "R":
        replaceSlotn = call.data[8:].split("-")[0]
        byAbilityn = int(call.data[8:].split("-")[1][1:])
        Ofn = int(call.data[8:].split("-")[2].split("|")[0][1:])

        data = AbilityStorage.query.filter_by(id=call.from_user.id).first()

        if int(data.__dict__['book' + str(byAbilityn+1)]) <= 0:
            bot.answer_callback_query(callback_query_id=call.id, text="You don't have this Ability's book")
            return

        #We remove the book from the user
        ok = remBook(call.from_user.id, byAbilityn)
        if not ok:
            #We shouldn't be there since the verification was done few lines up
            bot.answer_callback_query(callback_query_id=call.id, text="You don't have this Ability's book -- Strange thing happened")
            return

        #We give the ability to the selected companion
        if int(replaceSlotn) == 1:
            CompanionData.query.filter_by(owner=call.from_user.id, name=Ofn).update({CompanionData.ability1: byAbilityn})
            db.session.commit()
        elif replaceSlotn == 2:
            CompanionData.query.filter_by(owner=call.from_user.id, name=Ofn).update({CompanionData.ability2: byAbilityn})
            db.session.commit()
        elif replaceSlotn == 3:
            CompanionData.query.filter_by(owner=call.from_user.id, name=Ofn).update({CompanionData.ability3: byAbilityn})
            db.session.commit()

        data = CompanionData.query.filter_by(owner=call.from_user.id, name=Ofn).first()
        comp = int(data.name)

        comp = characters.characters[comp]
        abil = abilities.abilities[int(byAbilityn)]

        bot.edit_message_text(f"Congrats, *{comp.name}* learned *{abil.name}*",
            chat_id=call.message.chat.id,
              message_id=call.message.message_id)


def addBook(who, which):
    which = int(which)
    data = AbilityStorage.query.filter_by(id=who).first()
    if data == None:
        createUser = AbilityStorage(who, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        db.session.add(createUser)
        db.session.commit()


    # Replace with for loop, hint: use exec or idk
    if which == 0:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book1: AbilityStorage.book1 + 1})
    elif which == 1:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book2: AbilityStorage.book2 + 1})
    elif which == 2:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book3: AbilityStorage.book3 + 1})
    elif which == 3:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book4: AbilityStorage.book4 + 1})
    elif which == 4:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book5: AbilityStorage.book5 + 1})
    elif which == 5:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book6: AbilityStorage.book6 + 1})
    elif which == 6:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book7: AbilityStorage.book7 + 1})
    elif which == 7:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book8: AbilityStorage.book8 + 1})
    elif which == 8:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book9: AbilityStorage.book9 + 1})
    elif which == 9:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book10: AbilityStorage.book10 + 1})
    elif which == 10:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book11: AbilityStorage.book11 + 1})
    elif which == 11:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book12: AbilityStorage.book12 + 1})
    elif which == 12:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book13: AbilityStorage.book13 + 1})
    elif which == 13:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book14: AbilityStorage.book14 + 1})

    db.session.commit()

def remBook(who, which):
    which = int(which)
    data = AbilityStorage.query.filter_by(id=who).first()

    if data == None:
        bot.send_message(who, "Ehm, failed to remove you a book because.. you do not exist")
        #Uhm
        return

    for book in data.__dict__:
        if book == "_sa_instance_state" or book == "id":
            pass

        else:
            if int(book[4:]) == int(which)+1 and int(data.__dict__[f"book{int(book[4:])}"]) <= 0:
                bot.send_message(who, f"Ehm, failed to remove you a book because.. you don't have it || {book}, {book[4:]}, {which}, {data.__dict__[book]}")
                return False

    # Replace with for loop, hint: use exec or idk
    if which == 0:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book1: AbilityStorage.book1 - 1})
    elif which == 1:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book2: AbilityStorage.book2 - 1})
    elif which == 2:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book3: AbilityStorage.book3 - 1})
    elif which == 3:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book4: AbilityStorage.book4 - 1})
    elif which == 4:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book5: AbilityStorage.book5 - 1})
    elif which == 5:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book6: AbilityStorage.book6 - 1})
    elif which == 6:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book7: AbilityStorage.book7 - 1})
    elif which == 7:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book8: AbilityStorage.book8 - 1})
    elif which == 8:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book9: AbilityStorage.book9 - 1})
    elif which == 9:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book10: AbilityStorage.book10 - 1})
    elif which == 10:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book11: AbilityStorage.book11 - 1})
    elif which == 11:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book12: AbilityStorage.book12 - 1})
    elif which == 12:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book13: AbilityStorage.book13 - 1})
    elif which == 13:
        AbilityStorage.query.filter_by(id=who).update({AbilityStorage.book14: AbilityStorage.book14 - 1})

    db.session.commit()
    return True



""" Stats commands """

@bot.message_handler(commands=["mystats"])
def mystats(message):
    if not noInRoomBattle(message.from_user.id):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            bot.reply_to(message, "You are in battle. End it before doing anything else")
        return

    user = UserData.query.filter_by(id=message.from_user.id).first()
    if not user:
        return

    msg = f"*{module.removeMarkdown(message.from_user.first_name)}*\n*{message.from_user.id}*\n\n⚔️ Total battle played : *{user.total_win + user.total_lose}*\n✅ Total win : *{user.total_win}*\n❌ Total lose : *{user.total_lose}*\n"

    if message.chat.type in ["supergroup", "group"]:
        try:
            bot.reply_to(message, msg)
        except:
            pass #API 403/400 a lot of  times (because user deleted msgs, blocked from user/group, etc..)
    else:
        try:
            bot.send_message(message.from_user.id, msg)
        except:
            pass #API 403/400 a lot of  times (because user deleted msgs, etc..)

@bot.message_handler(commands=["stats"])
def getCompanionDataStats(message):
    if isInBattleOrArena(message) == 0:
        return

    companionName = message.text.split(" ")[-1].capitalize()
    if not companionName in CHARACTERS_NAME_ASCII_ONLY:
        try:
            bot.reply_to(message, "Companion not found or wrong command used , try /stats <yourCompanionName>")
        except:
            pass #API 403/400 a lot of  times (because user deleted msgs, etc..)
        return

    myCompanion = CompanionData.query.filter_by(owner=message.from_user.id).all()

    companion = list(filter(
        lambda x: CHARACTERS_NAME_ASCII_ONLY[x.name] == companionName, myCompanion))

    if not companion:
        bot.reply_to(message, "You don't have that companion. Buy it in /store")
        return

    companionInDb = companion[0]
    companion = characters.characters[companionInDb.name](companionInDb.level)

    exp = (f"{companionInDb.exp}/{module.getExpRequirement(companionInDb.level)}") if companionInDb.level < 100 else "Max"

    msg = f"      {companion.name}\n\nLevel : {companion.level}\nExp : {exp}\nElement : {companion.element}\nHP : {companion.hp}\nAttack : {companion.attack}\nSpeed : {companion.speed}\n\n💰 Gold production/min : {companion.gpm}\n🗄 Max gold : {companion.maxGold}\n\n⚔️ Default Moveset :\n*{companion.first_skill_name}* : {companion.first_skill_info}\n\n⚔️ Moveset unlock at level 50:\n*{companion.second_skill_name}* : {companion.second_skill_info}\n"

    companionInDb = CompanionData.query.filter_by(owner=message.from_user.id, name=int(companion.id)-1).first()

    msg += "📚 Acquired abilities:"

    if companionInDb.ability1 != None:
        msg += f"\n1: *{abilities.abilities[int(companionInDb.ability1)].name}*"
    else:
        msg += "\n1: *None*"
    if companionInDb.ability2 != None:
        msg += f"\n2: *{abilities.abilities[int(companionInDb.ability2)].name}*"
    else:
        msg += "\n2: *None*"
    if companionInDb.ability3 != None:
        msg += f"\n3: *{abilities.abilities[int(companionInDb.ability3)].name}*"
    else:
        msg += "\n3: *None*"

    markup = module.Mkd()
    mkp = module.Mkd()
    markup.add(
        module.Btn(
          text="Feed",
            calldata="Feed")
    )
    SELECTED_COMPANION[message.from_user.id] = companionName

    try:
        if message.chat.type in ["supergroup", "group"]:
            bot.send_photo(message.chat.id, open(companion.imagePath, "rb"),
                caption=msg,
                  reply_to_message_id=message.message_id,
                    reply_markup=mkp)
        else:
            bot.send_photo(message.from_user.id, open(companion.imagePath, "rb"),
                caption=msg,
                  reply_markup=markup)
    except:
        pass #403



""" Food """

@bot.callback_query_handler(func=lambda call: call.data == "Feed")
def giveFoodInStat(call):
    call.message.from_user.id = call.message.chat.id
    call.message.text = SELECTED_COMPANION[call.message.chat.id]
    del SELECTED_COMPANION[call.message.chat.id]
    bot.delete_message(call.message.chat.id, call.message.message_id)
    giveFood(call.message)

@bot.message_handler(commands=["feed"])
def giveFood(message):
    if isInBattleOrArena(message) == 0:
        return

    if "group" in message.chat.type:
        bot.reply_to(message, "Use this in PM")
        return

    companionName = message.text.split(" ")[-1].capitalize()
    if companionName == None in CHARACTERS_NAME_ASCII_ONLY:
        bot.reply_to(message, "Companion not found")
        return

    myCompanion = CompanionData.query.filter_by(owner=message.from_user.id).all()
    companion = list(filter(
        lambda x: CHARACTERS_NAME_ASCII_ONLY[x.name] == companionName, myCompanion))

    if not companion:
        bot.reply_to(message, "You don't have that companion")
        return

    companion = companion[0]
    companionClass = characters.characters[companion.name]

    user = UserData.query.filter_by(id=message.from_user.id).first()

    module.setData(message.from_user.id, (user, companion))

    exp = (f"{companion.exp}/{module.getExpRequirement(companion.level)}") if companion.level < 100 else "Max"

    msg = f"{companionClass.name}\n\nLevel : {companion.level}\nExp : {exp}\n\nYour foods: {user.food} 🍇"
    markup = types.ForceReply()

    bot.send_photo(message.chat.id, open(companionClass.imagePath, "rb"),
        caption=msg)
    bot.send_message(message.chat.id,
        "Enter food amount :",
          reply_markup=markup)

@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text == "Enter food amount :")
def giveFood_(message):
    if isInBattleOrArena(message) == 0:
        return

    foodNeeded = message.text

    if not foodNeeded.isdigit():
        bot.reply_to(message, "Total food not valid!")
        return

    foodNeeded = int(foodNeeded)
    try:
        user, companion = module.getData(message.from_user.id)
    except:
        return #TypeError: cannot unpack non-iterable NoneType object

    if companion.level >= 100:
        bot.reply_to(message, "This companion already reached the maximum level! Feed the others")
        return

    companionClass = characters.characters[companion.name]

    if user.food < foodNeeded:
        bot.reply_to(message, f"You don't have {foodNeeded} food")
        return

    module.addExp(companion.companion_id, foodNeeded, companion=companion)
    UserData.query.filter_by(id=message.from_user.id).update(
        {UserData.food: UserData.food - foodNeeded})
    db.session.commit()

    bot.reply_to(message, "Yummyy !!")



""" Shop """

@bot.message_handler(commands=["store"])
def shop(message):
    if isInBattleOrArena(message) == 0:
        return

    if "group" in message.chat.type:
        bot.reply_to(message, "Use this in PM")
        return

    msg = "_Welcome to store_ 🏫\n\n*Here you can buy:*\n 📦 New companions\n 📦 Foods for companions\n 📦 Ability books\n 📦 Others stuffs\n    "

    markup = module.inline(["Buy Food"], ["Buy Companion"], ["Buy books"])
    bot.send_message(message.from_user.id, msg, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "Buy books")
@loadingFixed
def buyBook(call):
    a = abilities.abilities

    sellable = [a[4], a[5], a[6]]

    user = UserData.query.filter_by(id=call.from_user.id).first()
    if not user.invited is None:
        for _ in range(user.invited // 10):
            if len(sellable) == len(a):
                break

            ab = a[ random.randint(0, len(a)-1) ]

            while ab in sellable:
                ab = a[ random.randint(0, len(a)-1) ]

            sellable.append(ab)


    SELLABLE = []
    for abi in sellable:
        SELLABLE.append(abi.number)

    available = ""
    for ab in sellable:
        available += f"{ab.emote}{ab.name} ({ab.price}💰)\n"

    ability_name = [SELLABLE[i:i + 2]
        for i in range(0, len(SELLABLE), 2)]

    markup = module.Mkd()
    for x in ability_name:
        markup.row(
            *(
                [module.Btn(text=a[y].name, calldata=f"AbilityBookBuy {a[y].number}-s|{call.from_user.id}") for y in x]
            )
        )

    msg = f"_Welcome in the BookShop!_\n\n*Books for sale:*\n\n{available}"
    bot.edit_message_text(msg,
        chat_id=call.message.chat.id,
          message_id=call.message.message_id,
            reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("AbilityBookBuy"))
@loadingFixed
def buyBook_(call):
    ability = int(call.data[14:].split("-")[0])
    src = call.data[14:].split("-")[1].split("|")[0]

    ab = abilities.abilities[ability]
    user = UserData.query.filter_by(id=call.message.chat.id).first()

    if user.gold > ab.price:
        user.gold -= ab.price
        db.session.commit()

        addBook(call.from_user.id, ability)

        if src == "s":
            msg = f"You succesfully bought *{ab.emote}{ab.name} book*. \nLook at your /storage !"
            markup = module.Mkd()
            markup.add(module.Btn(text="↩️ Buy another", calldata="Buy books"))

            bot.edit_message_text(msg,
                chat_id=call.message.chat.id,
                  message_id=call.message.message_id,
                    reply_markup=markup)

        elif src == "t":
            msg = f"Trader sold you *{ab.emote}{ab.name}* book.\nIt's now in your /storage !"
            bot.edit_message_text(msg,
                chat_id=call.message.chat.id,
                  message_id=call.message.message_id)

            del QUEST_RING[call.from_user.id]
            del BOOKS[call.from_user.id]

    else:
        msg = f"You don't have enough gold to buy {ab.name} book!"
        bot.answer_callback_query(callback_query_id=call.id, text=msg)


@bot.callback_query_handler(func=lambda call: call.data == "Buy Food")
@loadingFixed
def buyFood(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    markup = types.ForceReply()

    user = UserData.query.filter_by(id=call.message.chat.id).first()
    module.setData(call.message.chat.id, user)

    msg = f"Enter your food amount :\n\n3 💰 =  1 🍇\n\nYour golds: _{user.gold}_"

    #bot.edit_message_text(msg, chat_id=call.message.chat.id, message_id=call.message.message_id)
    #bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    bot.send_message(call.message.chat.id, msg, reply_markup=markup)

@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text and "Enter your food amount :" in message.reply_to_message.text)
def confirmBuyFood(message):
    if isInBattleOrArena(message) == 0:
        return

    user = module.getData(message.chat.id)
    total = message.text
    if not total.isdigit():
        bot.send_message(message.from_user.id, "Total food not valid")
        return

    total = int(total)
    price = total * 3
    if price > user.gold:
        bot.send_message(message.from_user.id, f"You don't have {price} gold")
        return

    UserData.query.filter_by(id=message.from_user.id).update({UserData.gold: UserData.gold - price, UserData.food: UserData.food + total})
    db.session.commit()
    bot.send_message(message.chat.id, "Successfully bought food")


@bot.callback_query_handler(func=lambda call: call.data == "Buy Companion")
@loadingFixed
def buyCompanion(call):
    char_name = [CHARACTERS_NAME[i:i + 2]
        for i in range(0, len(CHARACTERS_NAME), 2)]

    markup = module.Mkd()
    for x in char_name:
        markup.row(*([module.Btn(text=y, calldata="Buy " + y) for y in x]))

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_photo(call.message.chat.id, open("mysite/images/Angel.jpg", "rb"),
        caption="Select one companion to follow you ⚔️",
          reply_markup=markup)

@bot.callback_query_handler(func=lambda call: re.search(r"^Buy ", call.data))
@loadingFixed
def selectCompanion(call):
    index = CHARACTERS_NAME.index(call.data.replace("Buy ", ""))
    character = characters.characters[index]

    myCompanion = CompanionData.query.filter_by(owner=call.message.chat.id)
    myCompanionName = [CHARACTERS_NAME[x.name] for x in myCompanion]
    companionPrice = [10000, 20000, 40000, 80000, 160000, 320000, 640000, 1280000, 2560000]
    companionPrice = companionPrice[len(myCompanionName) - 1]

    if call.data.replace("Buy ", "") in myCompanionName:
        bot.answer_callback_query(callback_query_id=call.id, text="You already have this companion")
        return

    user = UserData.query.filter_by(id=call.message.chat.id).first()
    module.setData(call.message.chat.id, (user, myCompanion))

    msg = f"{character.name}\n\nElement : {character.element}\nHP : {character.hp}\nAttack : {character.attack}\nSpeed : {character.speed}\n\n💰 Gold production/min : {character.gpm}\n🗄 Max gold : {character.maxGold}\n\n⚔️ Default Moveset :\n*{character.first_skill_name}* : {character.first_skill_info}\n\n⚔️ Moveset unlock at level 50:\n*{character.second_skill_name}* : {character.second_skill_info}\n\nYour golds: {user.gold}\n    "

    SELECTED_COMPANION[call.message.chat.id] = character
    #markup = module.inline(f"Buy Companion ({companionPrice} gold)", "Back")
    markup = module.Mkd()
    markup.add(
        module.Btn(
            text=f"Buy Companion ({companionPrice} gold)",
              calldata="BuyCompanion")
    )
    markup.add(
        module.Btn(
            text="Back",
              calldata="BackToCompanionShop")
    )
    bot.edit_message_media(
        types.InputMedia("photo",
          open(character.imagePath, "rb"),
            caption=msg,
              parse_mode="Markdown"),
        chat_id=call.message.chat.id,
          message_id=call.message.message_id,
            reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "BackToCompanionShop")
@loadingFixed
def backToCompanionShop(call):
    char_name = [CHARACTERS_NAME[i:i + 2]
        for i in range(0, len(CHARACTERS_NAME), 2)]
    markup = module.Mkd()
    for x in char_name:
        markup.row(*([module.Btn(y, calldata="Buy " + y) for y in x]))

    bot.edit_message_media(
        types.InputMedia("photo",
          open("mysite/images/Angel.jpg", "rb"),
            caption="Select one companion to follow you ⚔️",
              parse_mode="Markdown"),
        chat_id=call.message.chat.id,
          message_id=call.message.message_id,
            reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "BuyCompanion")
@loadingFixed
def confirmBuyCompanion(call):
    #user = UserData.query.filter_by(id=call.message.chat.id).first()
    d = module.getData(call.message.chat.id)#CompanionData.query.filter_by(owner=call.message.chat.id).all() ?
    if d == None:
        bot.answer_callback_query(callback_query_id=call.id, text="Failed. /store again please")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        return

    user = d[0]
    myCompanion = d[1]
    myCompanionName = [CHARACTERS_NAME[x.name] for x in myCompanion]
    companionPrice = [10000, 20000, 40000, 80000, 160000, 320000, 640000, 1280000, 2560000]
    companionPrice = companionPrice[len(myCompanionName) - 1]
    character = SELECTED_COMPANION[call.message.chat.id]
    del SELECTED_COMPANION[call.message.chat.id]

    if character.name in myCompanionName:
        bot.answer_callback_query(callback_query_id=call.id, text="You already have this companion")
        return

    if user.slot <= len(myCompanionName):
        bot.answer_callback_query(callback_query_id=call.id, text="You don't have enough slot")
        return

    if companionPrice > user.gold:
        need = companionPrice - user.gold
        bot.answer_callback_query(callback_query_id=call.id, text=f"You're short of {need} golds. Companion cost is {companionPrice} but you only have {user.gold}")
        return

    addData = CompanionData(1, call.message.chat.id, CHARACTERS_NAME.index(character.name), int(time.time()), 0)
    db.session.add(addData)
    #user.gold -= companionPrice
    UserData.query.filter_by(id=call.message.chat.id).update({UserData.gold: UserData.gold - companionPrice})
    db.session.commit()

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    msg = f"Congratulations 🎊\nYou have selected {character.name} to be your companion.\n\nUse /commands to see command lists.\n\nLet the adventure begin ⚔️\n"
    bot.send_message(call.message.chat.id, msg)



""" Team """

@bot.message_handler(commands=["team"])
def editTeam(message):
    if isInBattleOrArena(message) == 0:
        return

    if "group" in message.chat.type:
        bot.reply_to(message, "Use this in PM")
        return

    inlineButton = ["Change positions",  "Reset"]

    myCompanionList = CompanionData.query.filter_by(owner=message.from_user.id).all()
    position = PositionData.query.filter_by(id=message.from_user.id).first()

    if not position:
        companionList = myCompanionList[:3]
        position1 = companionList[0].name
        position2 = companionList[1].name if len(companionList) >= 2 else None
        position3 = companionList[2].name if len(companionList) >= 3 else None

        addData = PositionData(message.from_user.id, position1, position2, position3)
        db.session.add(addData)
        db.session.commit()
        position = PositionData.query.filter_by(id=message.from_user.id).first()

    position = (position.position1, position.position2, position.position3)

    if len(myCompanionList) > 3:
        inlineButton.insert(0, "Edit")
    markup = module.inline(*inlineButton)

    msg = ""
    for i, companionName in enumerate(position):
        if companionName == None:
            continue
        msg += f"{i + 1}. {CHARACTERS_NAME[companionName]}\n"

    bot.send_message(message.from_user.id, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "Reset")
def resetTeam(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)

    PositionData.query.filter_by(id=call.message.chat.id).delete()
    db.session.commit()
    bot.send_message(call.message.chat.id, "Team was successfully reset")

@bot.callback_query_handler(func=lambda call: call.data == "Done")
def done(call):

    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "Edit")
@loadingFixed
def editTeam_(call):
    myCompanionList = CompanionData.query.filter_by(owner=call.message.chat.id).all()
    position = PositionData.query.filter_by(id=call.message.chat.id).first()
    position = (position.position1, position.position2, position.position3)

    module.setData(call.message.chat.id, (myCompanionList, position))

    markup = module.Mkd()
    for companion in myCompanionList:
        if not companion.name in position:
            markup.add(
                module.Btn(
                  text=CHARACTERS_NAME[companion.name],
                    calldata=f"ChangeTeam|{companion.name}")
            )

    bot.edit_message_text("Select companion to enter your team:",
        chat_id=call.message.chat.id,
          message_id=call.message.message_id,
            reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ChangeTeam"))
@loadingFixed
def changeTeam(call):
    myCompanionList, position = module.getData(call.message.chat.id, reset=False)

    markup = module.Mkd()
    for i, companionName in enumerate(position):
        markup.add(
            module.Btn(
              text=CHARACTERS_NAME[companionName],
                calldata=f"ConfirmChangeTeam|{call.data.split('|')[1]}|{i + 1}")
        )

    bot.edit_message_text("Change to:",
        chat_id=call.message.chat.id,
          message_id=call.message.message_id,
            reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ConfirmChangeTeam"))
@loadingFixed
def confirmChangeTeam(call):
    bot.answer_callback_query(callback_query_id=call.id)
    target = call.data.split("|")[1]
    change_to = call.data.split("|")[2]

    myCompanionList, position = module.getData(call.message.chat.id)

    if target in position:
        bot.answer_callback_query(
            callback_query_id=call.id,
              text="This companion has entered the team")
        return

    PositionData.query.filter_by(id=call.message.chat.id).update({f"position{change_to}": target})
    db.session.commit()

    inlineButton = ["Change positions", "Reset"]

    position = PositionData.query.filter_by(id=call.message.chat.id).first()
    position = (position.position1, position.position2, position.position3)

    if len(myCompanionList) > 3:
        inlineButton.insert(0, "Edit")
    markup = module.inline(*inlineButton)

    msg = ""
    for i, companionName in enumerate(position):
        if companionName == None:
            continue
        msg += f"{i + 1}. {CHARACTERS_NAME[companionName]}\n"

    bot.edit_message_text(msg,
        chat_id=call.message.chat.id,
          message_id=call.message.message_id,
            reply_markup=markup)


""" Team positions """

@bot.callback_query_handler(func=lambda call: call.data == "Change positions")
@loadingFixed
def changePosition(call):
    myCompanionList = CompanionData.query.filter_by(
        owner=call.message.chat.id).all()
    position = PositionData.query.filter_by(id=call.message.chat.id).first()

    if not position:
        companionList = myCompanionList[:3]
        position1 = companionList[0].name
        position2 = companionList[1].name if len(companionList) >= 2 else None

        addData = PositionData(call.message.chat.id, position1, position2, position3)
        db.session.add(addData)
        db.session.commit()
        position = PositionData.query.filter_by(id=call.message.chat.id).first()

    position = (position.position1, position.position2, position.position3)

    module.setData(call.message.chat.id, (companionList, position))
    markup = module.Mkd()
    for i, companionName in enumerate(position):
        if companionName == None:
            continue

        markup.add(
            module.Btn(
                text=CHARACTERS_NAME[companionName],
                  calldata=f"ChangePosition|{i + 1}")
        )

    bot.edit_message_text("Select companion to swap position:",
        chat_id=call.message.chat.id,
          message_id=call.message.message_id,
            reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ChangePosition"))
@loadingFixed
def changePosition_(call):
    myCompanionList, position = module.getData(call.message.chat.id, reset=False)

    markup = module.Mkd()
    for i, companionName in enumerate(position):
        if companionName == None:
            continue

        markup.add(
            module.Btn(
                text=CHARACTERS_NAME[companionName],
                  calldata=f"ConfirmChangePosition|{call.data.split('|')[1]}|{i + 1}")
        )

    bot.edit_message_text("Swap to:",
        chat_id=call.message.chat.id,
          message_id=call.message.message_id,
            reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ConfirmChangePosition"))
@loadingFixed
def confirmChangePosition(call):
    target = call.data.split("|")[1]
    swap_to = call.data.split("|")[2]

    db.engine.execute(
        f"UPDATE position SET position{target}=(@temp:=position{target}), position{target} = position{swap_to}, position{swap_to} = @temp WHERE id = {call.message.chat.id}")
    db.session.commit()

    inlineButton = ["Change positions", "Reset"]

    position = PositionData.query.filter_by(id=call.message.chat.id).first()
    position = (position.position1, position.position2, position.position3)
    myCompanionList = module.getData(call.message.chat.id)[0]

    if len(myCompanionList) > 3:
        inlineButton.insert(0, "Edit")
    markup = module.inline(*inlineButton)

    msg = ""
    for i, companionName in enumerate(position):
        if companionName == None:
            continue
        msg += f"{i + 1}. {CHARACTERS_NAME[companionName]}\n"

    bot.edit_message_text(msg,
        chat_id=call.message.chat.id,
           message_id=call.message.message_id,
             reply_markup=markup)



""" Referral """

@bot.message_handler(commands=["referral"])
def referall(message):
    if isInBattleOrArena(message) == 0:
        return

    user = UserData.query.filter_by(id=message.from_user.id).first()

    msg = f"Invite friends to join and receive great reward\n\nYou have invited : *{user.invited}* friends\n\nHere is your link :\n[https://t.me/{bot.bot_info.username}?start={message.from_user.id}](https://t.me/{bot.bot_info.username}?start={message.from_user.id})"
    bot.send_message(message.from_user.id, msg)




@bot.message_handler(commands=["forceleave"])
def forceLeaveEverything(message):
    try:
        a = BOSS_ARENA[message.from_user.id]
        a.cancel(message.from_user.id)
    except:
        pass

    try:
        b = ROOM_BATTLE[message.from_user.id]
        b.cancel(message.from_user.id, force=True)
    except:
        pass

    try:
        q = QUEST_RING[message.from_user.id]
        q.leave()
    except:
        pass

    bot.reply_to(message, "You have left any currently running arena or battle.")


""" Arena """

@bot.message_handler(commands=["arenastats"])
def arenastats(message):
    #if isInBattleOrArena(message) == 0:
    #    return

    sender = message.from_user
    if BossArena.query.filter_by(id=sender.id).first() == None:
        #bot.reply_to(message, "It's your first time here. Let's create your data")
        createUser = BossArena(sender.id, 0, 0, 0, 0, 0, 0, 0, 0)
        db.session.add(createUser)
        db.session.commit()

    stats = BossArena.query.filter_by(id=sender.id).first()

    badges = {}
    bdgs = ""
    if stats.b1_reward > 0:
        badges['b1'] = "🎖" + f"Basilisk Slaughterer ({stats.b1_reward})"
    if stats.b2_reward > 0:
        badges['b2'] = "🎖" + f"Chimera Killer ({stats.b2_reward})"
    if stats.b3_reward > 0:
        badges['b3'] = "🎖" + f"Divine Arrow ({stats.b3_reward})"
    if stats.b4_reward > 0:
        badges['b4'] = "🎖" + f"Anubis Assassinator ({stats.b4_reward})"
    if stats.b5_reward > 0:
        badges['b5'] = "🎖" + f"Demon King Executer ({stats.b5_reward})"

    if len(badges) == 0:
        bdgs = "You don't have any. Try to fight some Boss!"

    for key in badges:
        bdgs += badges[key] + "\n"

    msg = f"👤{module.createMention(sender)} arena's stats:\n—————————————\n⚔️ Highest floor: **{stats.level}**\n\n**B͟a͟d͟g͟e͟s͟ :**\n\n{bdgs}\n"
    bot.reply_to(message, msg)


@bot.message_handler(commands=["arena"])
def arena(message):
    if isInBattleOrArena(message) == 0:
        return

    sender = message.from_user
    bossArena = ArenaBoss(sender, message.chat, message)
    BOSS_ARENA[sender.id] = bossArena

@bot.callback_query_handler(func=lambda call: call.data.startswith("boss"))
def verifyBoss(call):
    if not noInArena(call.from_user.id):
        bossArena = BOSS_ARENA[call.from_user.id]
        bossToFight = call.data[:5][-1]
        if call.message.id == bossArena.arena_message.id:
            bossArena.sure(bossToFight)
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")

@bot.callback_query_handler(func=lambda call: call.data.startswith("enter"))
def enterBoss(call):
    if not noInArena(call.from_user.id):
        bossArena = BOSS_ARENA[call.from_user.id]
        bossToFight = call.data[:6][-1]
        bossArena.start(bossToFight)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cancelboss"))
def cancelArenab(call):
    if not noInArena(call.from_user.id):
        bossArena = BOSS_ARENA[call.from_user.id]
        bossArena.cancel(call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("forcecancel"))
def cancelArena(call):
    if not noInArena(call.from_user.id):
        bossArena = BOSS_ARENA[call.from_user.id]
        bossArena.cancel(call.from_user.id)
        bot.edit_message_text("Arena leaved",
            chat_id=call.message.chat.id,
              message_id=call.message.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("gohome"))
def goHome(call):
    if not noInArena(call.from_user.id):
        bossArena = BOSS_ARENA[call.from_user.id]
        bossArena.home()

@bot.callback_query_handler(func=lambda call: call.data.startswith("arenattack1"))
@loadingFixed
def arenaattack1(call):
    #There we suppose that arena is effectively not in a group.
    #Cuz if it is, anyone could click and put the arena AFK
    if noInArena(call.from_user.id):
        bot.edit_message_text("You were AFK for too long, the Arena Gate closed. ⛓\n\n🗝 No stats were affected", chat_id=call.message.chat.id, message_id=call.message.id)
        return

    if not call.from_user.id in BOSS_ARENA:
        return bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")

    bossArena = BOSS_ARENA[call.from_user.id]

    if bossArena.crt_trn != int(call.data.split("|")[1]):
        return

    if not bossArena.player_info.id == call.from_user.id:
        bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")
        return

    bossArena.attack1(int(call.data.split("|")[1]), call=call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("arenattack2"))
@loadingFixed
def arenaattack2(call):
    #There we suppose that arena is effectively not in a group.
    #Cuz if it is, anyone could click and put the arena AFK
    if noInArena(call.from_user.id):
        bot.edit_message_text("You were AFK for too long, the Arena Gate closed. ⛓\n\n🗝 No stats were affected", chat_id=call.message.chat.id, message_id=call.message.id)
        return

    if not call.from_user.id in BOSS_ARENA:
        return bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")

    bossArena = BOSS_ARENA[call.from_user.id]
    if bossArena.crt_trn != int(call.data.split("|")[1]):
        return

    if not bossArena.player_info.id == call.from_user.id:
        bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")
        return

    if bossArena.companion().level < 50:
        bot.answer_callback_query(callback_query_id=call.id, text="Need level 50 to unlock this")
        return

    bossArena.attack2(int(call.data.split("|")[1]), call=call.id)



""" Battle """

@bot.message_handler(commands=["battle"])#, func=lambda message: message.chat.type in ["supergroup", "group"])
def battle(message):
    if isInBattleOrArena(message) == 0:
        return

    if message.reply_to_message: #If it's a reply to a message
        if message.reply_to_message.from_user.id != message.from_user.id: #If it's not a reply to own message

            creator = message.from_user
            recipient = message.reply_to_message.from_user

            if noInRoomBattle(creator.id): #If creator isn't already in a battle
                if noInRoomBattle(recipient.id): #If recipient isn't already too
                    #We check if they have any companion

                    user1 = UserData.query.filter_by(id=recipient.id).first()
                    companion1 = CompanionData.query.filter_by(owner=recipient.id).first()

                    if not user1 or not companion1: #We first check the battle recipient
                        bot.reply_to(message, module.createMention(recipient) + " don't have a companion")
                        return

                    user2 = UserData.query.filter_by(id=creator.id).first()
                    companion2 = CompanionData.query.filter_by(owner=creator.id).first()

                    if not user2 or not companion2: #Then the battle creator
                        bot.reply_to(message, module.createMention(creator) + " don't have companion")
                        return

                    #Everything is good
                    msg = bot.reply_to(message, module.createMention(creator) + " inviting " + module.createMention(recipient) + " to battle!", reply_markup = module.inline(["Accept", "Reject", "Cancel"]))

                    roomBattle = RoomBattle(message.chat, creator, recipient, msg.message_id, message)
                    ROOM_BATTLE[creator.id] = roomBattle

                    ROOM_BATTLE[recipient.id] = roomBattle

                else:
                    bot.reply_to(message, module.createMention(recipient) + " is already in a battle. Wait for the end of its battle.")
            else:
                bot.reply_to(message, "You already are in a battle. You can't be in more than one at a time")
        else:
            bot.reply_to(message, "You can't battle with yourself")
    else:
        bot.reply_to(message, "You need to reply to someone message to battle with.")

@bot.callback_query_handler(func=lambda call: call.data == "Accept")
@checkUser
def acceptBattle(call):

    if not call.from_user.id in ROOM_BATTLE:
        return bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")

    roomBattle = ROOM_BATTLE[call.from_user.id]
    roomBattle.accept(call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == "Reject")
@checkUser
def rejectBattle(call):

    if not call.from_user.id in ROOM_BATTLE:
        return bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")


    roomBattle = ROOM_BATTLE[call.from_user.id]
    roomBattle.reject(call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == "Cancel")
@checkUser
def cancelBattle(call):

    if not call.from_user.id in ROOM_BATTLE:
        return bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")


    roomBattle = ROOM_BATTLE[call.from_user.id]
    roomBattle.cancel(call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("attack1"))
@checkUser
@loadingFixed
def attack1(call):

    if not call.from_user.id in ROOM_BATTLE:
        return bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")


    roomBattle = ROOM_BATTLE[call.from_user.id]

    if roomBattle.crt_trn != int(call.data.split("|")[1]):
        return

    if not roomBattle.player1_turn and roomBattle.player1_info.id == call.from_user.id:
        bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")
        return

    if roomBattle.player1_turn and roomBattle.player2_info.id == call.from_user.id:
        bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")
        return

    roomBattle.attack1(int(call.data.split("|")[1]), call=call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("attack2"))
@checkUser
@loadingFixed
def attack2(call):

    if not call.from_user.id in ROOM_BATTLE:
        return bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")


    roomBattle = ROOM_BATTLE[call.from_user.id]

    if roomBattle.crt_trn != int(call.data.split("|")[1]):
        return

    if not roomBattle.player1_turn and roomBattle.player1_info.id == call.from_user.id:
        bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")
        return

    if roomBattle.player1_turn and roomBattle.player2_info.id == call.from_user.id:
        bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")
        return

    if roomBattle.player1_turn and roomBattle.p1Companion().level < 50:
        bot.answer_callback_query(callback_query_id=call.id, text="Need level 50 to unlock this")
        return

    if not roomBattle.player1_turn and roomBattle.p2Companion().level < 50:
        bot.answer_callback_query(callback_query_id=call.id, text="Need level 50 to unlock this")
        return

    roomBattle.attack2(int(call.data.split("|")[1]), call=call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("forfeit"))
@checkUser
def forfeitBattle(call):

    if not call.from_user.id in ROOM_BATTLE:
        return bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")


    roomBattle = ROOM_BATTLE[call.from_user.id]

    if roomBattle.crt_trn != int(call.data.split("|")[1]):
        return

    roomBattle.forfeit(call.from_user.id)



""" Quest """

@bot.message_handler(commands=["quest"])
def quest(message):
    if isInBattleOrArena(message) == 0:
        return

    if not message.chat.id == message.from_user.id:
        return bot.reply_to(message, "This is a PM only command.")

    if not message.from_user.id in QUEST_TIMER:
        QUEST_TIMER[message.from_user.id] = 0

    QUEST_TIMER[message.from_user.id] += 1

    if QUEST_TIMER[message.from_user.id] > 25:
        bot.reply_to(message, "Sorry. You reached the 25 daily quests limit.\nThe limit reset every day at 1am UTC ")
        return

    if message.from_user.id in QUEST_RING:
        if QUEST_RING[message.from_user.id].state == 1:
            bot.reply_to(message, "You already started a quest! Finish it")
            return
        else:
            previous = QUEST_RING[message.from_user.id]
            previous.leave()

            del QUEST_RING[message.from_user.id]

    quest = Quest(message, message.from_user)
    QUEST_RING[message.from_user.id] = quest

    quest.start(n=QUEST_TIMER[message.from_user.id])

@bot.callback_query_handler(func=lambda call: call.data.startswith("quest"))
def questAction(call):
    action = call.data[5:6]
    data = call.data[6:].split("|")[0]
    target = int(call.data.split("|")[1])

    if call.from_user.id != target:
        bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")
        return

    if action == "F":
        try:
            quest = QUEST_RING[call.from_user.id]
        except:
            return bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")

        quest.state = 1
        quest.attack()

    elif action == "A":
        if data[0] == "1":
            try:
                quest = QUEST_RING[call.from_user.id]
            except:
                return bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")

            quest.attack1()
        elif data[0] == "2":
            try:
                quest = QUEST_RING[call.from_user.id]
            except:
                return bot.answer_callback_query(callback_query_id=call.id, text="Can't use this operation")

            quest.attack2()

    elif action == "C":
        #quest = QUEST_RING[call.from_user.id]
        gold = data.split("-")[1].split("g")[1]
        book = data.split("-")[2].split("b")[1]

        #Add gold
        UserData.query.filter_by(id=target).update({UserData.gold: UserData.gold + gold})
        db.session.commit()

        books = ""

        if not book == "rip":
            #Add book
            addBook(target, book)
            b = abilities.abilities[int(book)]
            books = f"and a {b.emote}{b.name} book"

        bot.edit_message_text(f"You successfully claimed {gold}💰 {books}.",
            chat_id=call.message.chat.id,
              message_id=call.message.message_id)

        del QUEST_RING[call.from_user.id]

    elif action == "L":
        bot.edit_message_text("Hope to see you soon!",
            chat_id=call.message.chat.id,
              message_id=call.message.message_id)

        try:
            del QUEST_RING[call.from_user.id]
            del BOOKS[call.from_user.id]
        except:
            pass


    elif action == "T":
        aN = int(data)
        a = abilities.abilities[aN]
        u = UserData.query.filter_by(id=target).first()
        msg = f"You asked {a.emote}{a.name} book to the Trader.\nHe has it in stock, but it'll cost {a.price}💰\n\n"
        mkp = module.Mkd()
        if u.gold >= a.price:
            msg += f"You have {u.gold} golds."
            mkp.add(module.Btn(f"Buy", calldata=f"AbilityBookBuy {a.number}-t|{target}"))
        else:
            msg += f"You don't have enough gold.. Current balance is {u.gold}💰"

        mkp.add(module.Btn(f"Look others book", calldata=f"questR|{target}"))
        bot.edit_message_text(msg, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=mkp)

    elif action == "R":
        msg = "__Welcome in Quest!__\n\nYou just found the book trader!\nClick the book you want to buy (You can buy only one)"
        mkp = module.Mkd()

        for b in BOOKS[call.from_user.id]:
            a = abilities.abilities[b]
            mkp.add(module.Btn(f"{a.emote}{a.name}", calldata=f"questT{a.number}|{call.from_user.id}"))

        bot.edit_message_text(msg, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=mkp)


    #bot.answer_callback_query(callback_query_id=call.id, text = action+"-"+data)




""" Administrations commands """

@bot.message_handler(commands=["get_gold"], func=lambda message: message.from_user.id in ADMINS)
def getGold(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    text = message.text.split(" ")[1:]
    if len(text) == 1:
        if not text[0].isdigit():
            bot.send_message(message.from_user.id, "Total gold not valid")
        else:
            UserData.query.filter_by(id=message.from_user.id).update(
                {UserData.gold: UserData.gold + text[0]})
            db.session.commit()
            bot.send_message(message.from_user.id, "Done. Added " + str(text[0]) + "💰 to you")

    elif len(text) == 2:
        if not text[1].isdigit():
            bot.send_message(message.from_user.id, "Total gold not valid")
        else:
            UserData.query.filter_by(id=text[0]).update({UserData.gold: UserData.gold + text[1]})
            db.session.commit()
            bot.send_message(message.from_user.id, "Done. Added " + str(text[1]) + "💰 to " + str(text[0]) + " !")

@bot.message_handler(commands=["get_food"], func=lambda message: message.from_user.id in ADMINS)
def getFood(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    text = message.text.split(" ")[1:]
    if len(text) == 1:
        if not text[0].isdigit():
            bot.send_message(message.from_user.id, "Total food not valid")
        else:
            UserData.query.filter_by(id=message.from_user.id).update({UserData.food: UserData.food + text[0]})
            db.session.commit()
            bot.send_message(message.from_user.id, "Done. Added " + str(text[0]) + "🍇 to you")

    elif len(text) == 2:
        if not text[1].isdigit():
            bot.send_message(message.from_user.id, "Total food not valid")
        else:
            try:
                UserData.query.filter_by(id=text[0]).update({UserData.food: UserData.food + text[1]})
                db.session.commit()
                bot.send_message(message.from_user.id, "Done. Added " + str(text[1]) + "🍇 to " + str(text[0]) + " !")
            except Exception as e:
                bot.send_message(message.from_user.id, "Failed:", str(e))

@bot.message_handler(commands=["get_invite"], func=lambda message: message.from_user.id in ADMINS)
def getInvite(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    text = message.text.split(" ")[1:]
    if len(text) == 1:
        if not text[0].isdigit():
            bot.send_message(message.from_user.id, "Total invites not valid")
        else:
            if not UserData.query.filter_by(id=message.from_user.id).first().invited is None:
                UserData.query.filter_by(id=message.from_user.id).update({UserData.invited: UserData.invited + text[0]})
            else:
                UserData.query.filter_by(id=message.from_user.id).update({UserData.invited: text[0]})
            db.session.commit()
            bot.send_message(message.from_user.id, "Done. Added " + str(text[0]) + "invites to you")

    elif len(text) == 2:
        if not text[1].isdigit():
            bot.send_message(message.from_user.id, "Total invites not valid")
        else:
            try:
                if not UserData.query.filter_by(id=int(text[0])).first().invited is None:
                    UserData.query.filter_by(id=int(text[0])).update({UserData.invited: UserData.invited + text[1]})
                else:
                    UserData.query.filter_by(id=int(text[0])).update({UserData.invited: text[1]})

                db.session.commit()
                bot.send_message(message.from_user.id, "Done. Added " + str(text[1]) + "invites to " + str(text[0]) + " !")
            except Exception as e:
                bot.send_message(message.from_user.id, "Failed:", str(e))

@bot.message_handler(func=lambda message: message.text.startswith("/get_book") and message.from_user.id in ADMINS)
def getBook(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    if message.text.split(" ")[0][9:].isdigit():
        ab = int(message.text.split(" ")[0][9:])
        ab = ab-1

        a = None
        for ability in abilities.abilities:
            if ability.number == ab:
                a = ability
                break

        if a is None:
            return bot.send_message(message.from_user.id, "This ability does not exist")

        if len(message.text.split(" ")) == 2:
            user = message.text.split(" ")[1]
            msg = f"It's look like a *{a.emote}{a.name} book* spawned in the /storage of {user}!"
        else:
            user = message.from_user.id
            msg = f"A *{a.emote}{a.name} book* spawned in your inventory!"

        addBook(user, ab)
        bot.send_message(message.from_user.id, msg)


#billy making /take_food
@bot.message_handler(commands=["take_food"], func=lambda message: message.from_user.id in ADMINS)
def takefood(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    text = message.text.split(" ")[1:]
    if len(text) == 1:
        if not text[0].isdigit():
            bot.send_message(message.from_user.id, "Total food not valid")
        else:
            UserData.query.filter_by(id=message.from_user.id).update({UserData.food: UserData.food - text[0]})
            db.session.commit()
            bot.send_message(message.from_user.id, "Done. Took " + str(text[0]) + "🍇 from you")

    elif len(text) == 2:
        if not text[1].isdigit():
            bot.send_message(message.from_user.id, "Total food not valid")
        else:
            try:
                UserData.query.filter_by(id=text[0]).update({UserData.food: UserData.food - text[1]})
                db.session.commit()
                bot.send_message(message.from_user.id, "Done. Took " + str(text[1]) + "🍇from " + str(text[0]) + " !")
            except:
                bot.send_message(message.from_user.id, "Failed")

#billy trying to make take gold cmd , idk if it's correct lol, just mimicking get_gold but with minus
@bot.message_handler(commands=["take_gold"], func=lambda message: message.from_user.id in ADMINS)
def takeGold(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    text = message.text.split(" ")[1:]
    if len(text) == 1:
        if not text[0].isdigit():
            bot.send_message(message.from_user.id, "Total gold not valid")
        else:
            user = UserData.query.filter_by(id=message.from_user.id).first()
            if user.gold < int(text[0]):
                UserData.query.filter_by(id=message.from_user.id).update({UserData.gold: 0})
                db.session.commit()
            else:
                UserData.query.filter_by(id=message.from_user.id).update({UserData.gold: UserData.gold - int(text[0])})
                db.session.commit()

            bot.send_message(message.from_user.id, str(text[0]) + "💰 just got withdrawned straight from your account")

    elif len(text) == 2:
        if not text[1].isdigit():
            bot.send_message(message.from_user.id, "Total gold not valid")
        else:
            user = UserData.query.filter_by(id=text[0]).first()
            if user.gold < int(text[1]):
                UserData.query.filter_by(id=text[0]).update({UserData.gold: 0})
                db.session.commit()
            else:
                UserData.query.filter_by(id=text[0]).update({UserData.gold: UserData.gold - int(text[1])})
                db.session.commit()

            bot.send_message(message.from_user.id, str(text[1]) + "💰 where removed from " + str(text[0]) + " account !")

@bot.message_handler(commands=["take_book"], func=lambda message: message.from_user.id in ADMINS and len(message.text.split(" ")) >= 3)
def takeBook(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    user = message.text.split(" ")[1]
    book = int(message.text.split(" ")[2])-1
    quantity = 1
    if len(message.text.split(" ")) == 4:
        quantity = int(message.text.split(" ")[3])

    for loop in range(quantity):
        remBook(user, book-1)

    book = abilities.abilities[book].name

    bot.send_message(message.from_user.id, f"{user} lost {quantity} {book} book(s)")

@bot.message_handler(commands=["take_companion"], func=lambda message: message.from_user.id in ADMINS and len(message.text.split(" ")) == 3)
def takeCompanion(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    owner = message.text.split(" ")[1]
    companion_n = message.text.split(" ")[2]

    companions = CompanionData.query.filter_by(owner=owner).all()

    for companion in companions:
        for character in characters.characters:
            if character.name_ne == companion_n:
                companion_id = character.id-1

                CompanionData.query.filter_by(owner=owner, name=companion_id).delete()
                db.session.commit()

                team = PositionData.query.filter_by(id=owner).first()

                for comp in team:
                    if comp == companion_id:
                        comp = None


                db.session.commit()

                bot.send_message(message.from_user.id, f"{owner} lost a companion. RIP {companion_n}")
                return

    bot.send_message(message.from_user.id, f"It seems that {owner} doesn't have this companion.")

@bot.message_handler(commands=["take_ability"], func=lambda message: message.from_user.id in ADMINS and len(message.text.split(" ")) == 4)
def takeAbility(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    user = message.text.split(" ")[1]
    companion_name = message.text.split(" ")[2]
    slot = int(message.text.split(" ")[3])-1
    companion_id, companion_abilities = None, None


    for Companion in characters.characters:
        if Companion.name_ne.lower() == companion_name.lower():
            companion_id = characters.characters.index(Companion)
            break

    if companion_id is None:
        bot.send_message(message.from_user.id, "Companion not found. Please check that you wrote his name correctly")
        return

    companionData = CompanionData.query.filter_by(owner=user).all()
    for Companion in companionData:
        if Companion.name == companion_id:
            companion_abilities = [Companion.ability1, Companion.ability2, Companion.ability3]
            break

    if companion_abilities is None:
        bot.send_message(message.from_user.id, f"User `{user}` does not have the companion `{companion_name}`")
        return

    companion_abilities[slot] = None

    CompanionData.query.filter_by(owner=user, name=companion_id).update(
        {CompanionData.ability1: companion_abilities[0],
            CompanionData.ability2: companion_abilities[1],
                CompanionData.ability3: companion_abilities[2]})
    db.session.commit()

    bot.send_message(message.from_user.id, f"Removed learnt ability in slot {slot+1} of the {companion_name} who's owner is {user}.")


@bot.message_handler(commands=["reset_user"], func=lambda message: message.from_user.id in ADMINS)
def resetUser(message):
    if len(message.text.split(' ')) == 1:
        return bot.reply_to(message, "You need to confirm into the command. `/reset_user YES`")

    else:
        if not message.text.split(' ')[1] == "YES":
            return bot.reply_to(message, "You need to confirm into the command. `/reset_user YES`")

        """ TODO """
        bot.reply_to(message, "todo")


@bot.message_handler(commands=["getid", "get_id"], func=lambda message: message.from_user.id in ADMINS)
def getId(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    bot.send_message(message.from_user.id, "The id of " + module.createMention(message.reply_to_message.from_user) + " is `" + str(message.reply_to_message.from_user.id) + "`")

@bot.message_handler(commands=["makeAdmin"], func=lambda message: message.from_user.id in ADMINS)
def makeAdmin(message):
    target = message.reply_to_message.from_user.id
    target_data = message.reply_to_message.from_user
    ADMINS.append(target)
    admin_data["admin" + str(len(ADMINS)+1)] = target
    write_json("mysite/admin.json", admin_data)
    bot.send_message(message.from_user.id, f"{module.createMention(target_data)} is now admin")
    bot.send_message(target, "You are now admin")

    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass



#billy trying to make removeAdmin lol
#@bot.message_handler(commands=["removeAdmin"], func=lambda message: message.from_user.id in ADMINS)
#def removeAdmin(message):
#    target = message.reply_to_message.from_user.id
#    target_data = message.reply_to_message.from_user
#    ADMINS.remove(target)
#    admin_data["admin" + str(len(ADMINS)-1)] = target
#    write_json("admin.json", admin_data)
#    bot.reply_to(message, f"{module.createMention(target_data)} is now dismissed as admin")
#    bot.send_message(target, "You are removed from admin list")
#    return


#billy making send global message
#def globale_data():
#    try:
#        groups = DB.conn.execute(f"SELECT group_id FROM data_groups WHERE group_id").fetchall()
#        return groups
#    except:
#        return

#@bot.message_handler(commands=['global', 'Global'])
#def globale(message):
#    user_id = message.from_user.id in ADMINS
#    if user_id != dev:
#        return
#    else:
#        arg = message.text[7:]
#        data = globale_data()
#        for group_id in data:
#            bot.send_message(group_id[0], f'{arg}')



# if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
