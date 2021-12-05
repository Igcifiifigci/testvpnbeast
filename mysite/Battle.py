""" Battle room """

from tbot import bot
from telebot import types
from database import db, UserData, CompanionData, PositionData, BossArena
import characters, boss, abilities
import module
import random, time, threading

allinfos = {}
IN_ROOM_BATTLE = {}
ROOM_BATTLE = {}
MSG_ID = {}



def checkUser(func):
    def inner(call):
        if MSG_ID.get(call.from_user.id) == call.message.message_id:
            return func(call)
        else:
            bot.answer_callback_query(callback_query_id = call.id, text = "Can't use this operation")

    return inner

def noInRoomBattle(tele_id):
    return not tele_id in IN_ROOM_BATTLE.keys()


class Timer:

    """ Refacto idea: Async/Await """


    PENDING = {}

    def __init__(self):
        self.id = random.randint(0, 1_000_000_000)

    def execute(self, when, call=None):
        def timeout(self, when):
            if when == self.state:

                """ Game started """
                if when.startswith("True"):
                    RoomBattle.timeout(self)

                elif when.startswith("False"):
                    RoomBattle.timeout(self)

                """ Before game start """
                if when == "before":
                    self.state = "autocancel"
                    try:
                        del ROOM_BATTLE[self.player1_info.id]
                        del ROOM_BATTLE[self.player2_info.id]
                    except:
                        pass
            else:
                pass

        try:
            threading.Timer(180, timeout, [self, when]).start()
        except:
            try:
                bot.answer_callback_query(callback_query_id=call, text="Sorry, I crashed. You can still play but without any timer")
            except:
                pass #Cuz when starting their is not call to reply..
        return #RuntimeError: can't start new thread

class RoomBattle:
    def __init__(self, group_info, player1_info, player2_info, msg_id, message):
        self.group_info = group_info
        self.player1_info = player1_info
        self.player2_info = player2_info
        self.player1_companions = []
        self.player2_companions = []
        self.msg_id = msg_id
        self.player1_turn = None
        self.crt_trn = 0
        self.msg = "Battle begins!"
        self.total_damage = {}
        self.getPosition()

        self.state = None
        self.turn = 0

        self.forfeit_count = 0
        self.forfeit_msg = None

        self.advtgs = None
        self.disadvtgs = None

        #Ability
        self.p1damage_sentA1 = {"damage": 0, "until": 0}
        self.p2damage_sentA1 = {"damage": 0, "until": 0}
        self.p1damage_receivedA1 = {"damage": 0, "until": 0}
        self.p2damage_receivedA1 = {"damage": 0, "until": 0}

        self.p1damage_sentA2 = {"damage": 0, "until": 0}
        self.p2damage_sentA2 = {"damage": 0, "until": 0}
        self.p1damage_receivedA2 = {"damage": 0, "until": 0}
        self.p2damage_receivedA2 = {"damage": 0, "until": 0}

        self.p1damage = 0
        self.p2damage = 0

        self.isFreeze = {"p1": False, "p2": False}
        self.isBurning = {"p1": {"state": False, "until": 0, "damage": None}, "p2": {"state": False, "until": 0, "damage": None}}
        self.isImmune = {"p1": {"state": False, "until": 0}, "p2": {"state": False, "until": 0}}
        self.isLocked = {"p1": {"state": False, "until": 0}, "p2": {"state": False, "until": 0}}

        self.inUse = {"p1": [], "p2": []}
        self.used = {"p1": [], "p2": []}
        self.leftUse = {"p1": 2, "p2": 2}

        self.FrozeArtifact = {'p1': 0, 'p2': 0}
        self.HealingRing = {'p1': 0, 'p2': 0}
        self.HealingRingII = {'p1': 0, 'p2': 0}
        self.BlueFragment = {'p1': 0, 'p2': 0}
        self.RedFragment = {'p1': 0, 'p2': 0}
        self.GreenFragment = {'p1': 0, 'p2': 0}
        self.BlueFragmentII = {'p1': 0, 'p2': 0}
        self.RedFragmentII = {'p1': 0, 'p2': 0}
        self.GreenFragmentII = {'p1': 0, 'p2': 0}
        self.BlackRelics = {'p1': 0, 'p2': 0}
        self.LightRelics = {'p1': 0, 'p2': 0}
        self.GodsEye = {'p1': 0, 'p2': 0}
        self.EmeraldShards = {'p1': 0, 'p2': 0}
        self.FrozeArtifact = {'p1': 0, 'p2': 0}
        self.HealingRing = {'p1': 0, 'p2': 0}
        self.HealingRingII = {'p1': 0, 'p2': 0}
        self.BlueFragment = {'p1': 0, 'p2': 0}
        self.RedFragment = {'p1': 0, 'p2': 0}
        self.GreenFragment = {'p1': 0, 'p2': 0}
        self.BlueFragmentII = {'p1': 0, 'p2': 0}
        self.RedFragmentII = {'p1': 0, 'p2': 0}
        self.GreenFragmentII = {'p1': 0, 'p2': 0}
        self.BlackRelics = {'p1': 0, 'p2': 0}
        self.LightRelics = {'p1': 0, 'p2': 0}
        self.GodsEye = {'p1': 0, 'p2': 0}
        self.EmeraldShards = {'p1': 0, 'p2': 0}

        self.battle_msg = message
        self.ability_msg = False

        MSG_ID[player1_info.id] = msg_id
        MSG_ID[player2_info.id] = msg_id

        IN_ROOM_BATTLE[player1_info.id] = int(time.time()) + 150
        IN_ROOM_BATTLE[player2_info.id] = int(time.time()) + 150

        self.p1_reward = round(sum([x.level * 1.5 for x in self.player2_companions]))
        self.p2_reward = round(sum([x.level * 1.5 for x in self.player1_companions]))

        self.startGame()


    def ability(self, book):
        msg = abilities.abilities[book].use(self)
        markup = module.Mkd()

        if self.player1_turn:
            self.p1UpdateAbility()
            mkp = self.p1AbilityMarkup(markup)
        else:
            self.p2UpdateAbility()
            mkp = self.p2AbilityMarkup(markup)

        messg = self.getMsg(self.p1Companion(), self.p2Companion())
        bot.edit_message_text(messg,
        	chat_id=self.group_info.id,
        	  message_id=self.msg_id,
        	  	reply_markup=mkp)

        return msg

    def startGame(self):
        self.state = "JustCreated"

        self.startTimer(self.state)

    def startTimer(self, when, call=None):

        Timer.execute(self, when, call=call)

    def cancel(self, tele_id, force=False):
        if not force:
            if tele_id != self.player1_info.id:
                return

        self.state = "Canceled"
        bot.edit_message_text("Battle cancelled",
        	chat_id=self.group_info.id,
        	  message_id=self.msg_id)

        self.doneBattle()

    def accept(self, tele_id):
        if tele_id != self.player2_info.id:
            return

        self.state = "Accepted"
        try:
            bot.edit_message_text("Battle accepted",
            	chat_id=self.group_info.id,
            	  message_id=self.msg_id)
        except:
            pass
        self.start()

    def reject(self, tele_id):
        if tele_id != self.player2_info.id:
            return

        self.state = "Rejected"
        bot.edit_message_text("Battle rejected",
        	chat_id=self.group_info.id,
        	  message_id=self.msg_id)
        self.doneBattle()


    def forfeit(self, tele_id):
        if self.forfeit_count == 2:
            bot.edit_message_text(module.createMention(self.player2_info) + " and " + module.createMention(self.player1_info) + " agreed to forfeit",
            	chat_id=self.group_info.id,
            	  message_id=self.forfeit_msg.message_id)
            return

        if self.forfeit_msg == None:

            if tele_id == self.player1_info.id:
                if self.forfeit_count == 0: #Prevent from executing multiple time for just one call. (All API error due to "message is not different" are due to that) ### Multi click / Too long to respond
                    self.forfeit_count += 1

                    self.forfeit_msg = bot.reply_to(self.battle_msg, module.createMention(self.player1_info) + " want to forfeit")
                    return

            if tele_id == self.player2_info.id:
                if self.forfeit_count == 0:
                    self.forfeit_count += 1

                    self.forfeit_msg = bot.reply_to(self.battle_msg, module.createMention(self.player2_info) + " want to forfeit")
                    return

        else:
            bot.edit_message_text(module.createMention(self.player2_info) + " and " + module.createMention(self.player1_info) + " agreed to forfeit",
            	chat_id=self.group_info.id,
            	  message_id=self.forfeit_msg.message_id)
            bot.edit_message_text("Cancelled due to forfeit of the two players\nNo stats were affected",
            	chat_id=self.group_info.id,
            	  message_id=self.msg_id)

            self.state = "forfeited"
            self.doneBattle()

    def getCharacterInfo(self, characterObject):

        return f"\n{characterObject.name}\n\nLevel : {characterObject.level}\nElement : {characterObject.element}\nHP : {characterObject.hp}\nAttack : {characterObject.attack}\nSpeed : {characterObject.speed}\n\n⚔️ Default Moveset :\n*{characterObject.first_skill_name}* : {characterObject.first_skill_info}\n\n⚔️ Moveset unlock at level 50:\n*{characterObject.second_skill_name}* : {characterObject.second_skill_info}"


    def getMsg(self, characterObject1, characterObject2):
        ability1=""
        ability2=""

        if self.player1_turn:
            currentTurn = module.createMention(self.player1_info)
        else:
            currentTurn = module.createMention(self.player2_info)

        i=0
        for elem in self.inUse['p1']:
            ability1 += f"{self.inUse['p1'][i]}"
            i+=1

        i=0
        for elem in self.inUse['p2']:
            ability2 += f"{self.inUse['p2'][i]}"
            i+=1

        msg = f"{self.msg}\nCurrent turn: {currentTurn}\n\n{ability1} {module.createMention(self.player1_info)} - *{characterObject1.name2}*\n*Lv.* {characterObject1.level}, *HP:* _{characterObject1.hp}/{characterObject1.totalHp}_\n{module.getBarPersentase(characterObject1.hp, characterObject1.totalHp)}\n\n{ability2} {module.createMention(self.player2_info)} - *{characterObject2.name2}*\n*Lv.* {characterObject2.level}, *HP:* _{characterObject2.hp}/{characterObject2.totalHp}_\n{module.getBarPersentase(characterObject2.hp, characterObject2.totalHp)}"
        return msg

    def getPosition(self):

        player1_companions = CompanionData.query.filter_by(owner = self.player1_info.id).all()
        player1_position = PositionData.query.filter_by(id = self.player1_info.id).first()

        if not player1_position:
            companionList = player1_companions[:3]
            position1 = companionList[0].name
            position2 = companionList[1].name if len(companionList) >= 2 else None
            position3 = companionList[2].name if len(companionList) >= 3 else None

            addData = PositionData(self.player1_info.id, position1, position2, position3)
            db.session.add(addData)
            db.session.commit()
            player1_position = PositionData.query.filter_by(id = self.player1_info.id).first()

        player1_position = (player1_position.position1, player1_position.position2, player1_position.position3)

        for x in player1_position:
            for y in player1_companions:
                if x == y.name:
                    self.player1_companions.append(characters.characters[x](y.level, companion_id = y.companion_id))
                    break


        player2_companions = CompanionData.query.filter_by(owner = self.player2_info.id).all()
        player2_position = PositionData.query.filter_by(id = self.player2_info.id).first()

        if not player2_position:
            companionList = player2_companions[:3]
            position1 = companionList[0].name
            position2 = companionList[1].name if len(companionList) >= 2 else None
            position3 = companionList[2].name if len(companionList) >= 3 else None

            addData = PositionData(self.player2_info.id, position1, position2, position3)
            db.session.add(addData)
            db.session.commit()
            player2_position = PositionData.query.filter_by(id = self.player2_info.id).first()

        player2_position = (player2_position.position1, player2_position.position2, player2_position.position3)

        for x in player2_position:
            for y in player2_companions:
                if x == y.name:
                    self.player2_companions.append(characters.characters[x](y.level, companion_id = y.companion_id))
                    break


    def start(self):
        self.getFirst()
        self.reload()


    def p1Companion(self, get=False):
        for i, x in enumerate(self.player1_companions.copy()):
            if not x.isDead():
                return x

            if not get:
                bot.edit_message_text(f"{x.name} died!",
                	chat_id=self.group_info.id,
                	  message_id=self.msg_id)

                self.leftUse['p1'] = 2
                del self.player1_companions[i]
                self.msg = "Battle begins!"
                time.sleep(2)

    def p2Companion(self, get=False):
        for i, x in enumerate(self.player2_companions.copy()):
            if not x.isDead():
                return x

            if not get:
                bot.edit_message_text(f"{x.name} died!",
                	chat_id=self.group_info.id,
                	  message_id=self.msg_id)

                self.leftUse['p2'] = 2
                del self.player2_companions[i]
                self.msg = "Battle begins!"
                time.sleep(2)


    def getFirst(self):
        if self.p1Companion().speed <= self.p2Companion().speed:
            self.player1_turn = True
        else:
            self.player1_turn = False

    def doneBattle(self):
        del IN_ROOM_BATTLE[self.player1_info.id]
        del IN_ROOM_BATTLE[self.player2_info.id]

        del MSG_ID[self.player1_info.id]
        del MSG_ID[self.player2_info.id]
        del ROOM_BATTLE[self.player1_info.id]
        del ROOM_BATTLE[self.player2_info.id]

        #Ability
        self.p1damage_sentA1 = {"damage": 0, "until": 0}
        self.p2damage_sentA1 = {"damage": 0, "until": 0}
        self.p1damage_receivedA1 = {"damage": 0, "until": 0}
        self.p2damage_receivedA1 = {"damage": 0, "until": 0}

        self.p1damage_sentA2 = {"damage": 0, "until": 0}
        self.p2damage_sentA2 = {"damage": 0, "until": 0}
        self.p1damage_receivedA2 = {"damage": 0, "until": 0}
        self.p2damage_receivedA2 = {"damage": 0, "until": 0}

        self.p1damage = 0
        self.p2damage = 0

        self.isFreeze = {"p1": False, "p2": False}
        self.isBurning = {"p1": {"state": False, "until": 0, "damage": None}, "p2": {"state": False, "until": 0, "damage": None}}
        self.isImmune = {"p1": {"state": False, "until": 0}, "p2": {"state": False, "until": 0}}
        self.isLocked = {"p1": {"state": False, "until": 0}, "p2": {"state": False, "until": 0}}

        self.inUse = {"p1": [], "p2": []}
        self.used = {"p1": [], "p2": []}
        self.leftUse = {"p1": 2, "p2": 2}

        self.ability_msg = False


        for companion_id, damage in self.total_damage.items():
            damage = abs(damage)
            module.addExp(companion_id, damage // 8)
        self.total_damage = {}


    def attack1(self, trn, call=None):
        if trn != self.crt_trn:
            return

        p1 = self.p1Companion()
        p2 = self.p2Companion()

        if self.player1_turn:
            p2hp = p2.hp
            damage, heal, affect = p1.attack1(p2)

            olddamage = damage
            if self.isImmune["p2"]["until"] == 0:
                #We check ability 1 of p1
                if self.p1damage_sentA1["damage"] > 0:
                    if self.p1damage_sentA1["until"] == -1:
                        damage += int((damage*self.p1damage_sentA1["damage"])/100)
                    elif self.p1damage_sentA1["until"] > 0:
                        damage += int((damage*self.p1damage_sentA1["damage"])/100)
                        self.p1damage_sentA1["until"] -= 1
                    else:
                        self.p1damage_sentA1["damage"] = 0
                #We check ability 2 of p1
                if self.p1damage_sentA2["damage"] > 0:
                    if self.p2damage_sentA2["until"] == -1:
                        damage += int((damage*self.p1damage_sentA2["damage"])/100)
                    elif self.p2damage_sentA2["until"] > 0:
                        damage += int((damage*self.p1damage_sentA2["damage"])/100)
                        self.p2damage_sentA2["until"] -= 1
                    else:
                        self.p1damage_sentA2["damage"] = 0
            else:
                self.isImmune["p2"]["until"] -= 1

            #We check ability 1 of p2
            if self.p2damage_receivedA1["damage"] > 0:
                if self.p2damage_receivedA1["until"] == -1:
                    damage -= int((damage*self.p2damage_receivedA1["damage"])/100)
                elif self.p2damage_receivedA1["until"] > 0:
                    damage -= int((damage*self.p2damage_receivedA1["damage"])/100)
                    self.p2damage_receivedA1["until"] -= 1
                else:
                    self.p2damage_receivedA1["damage"] = 0
            #We check ability 2 of p2
            if self.p2damage_receivedA2["damage"] > 0:
                if self.p2damage_receivedA2["until"] == -1:
                    damage -= int((damage*self.p2damage_receivedA2["damage"])/100)
                elif self.p2damage_receivedA2["until"] > 0:
                    damage -= int((damage*self.p2damage_receivedA2["damage"])/100)
                    self.p2damage_receivedA2["until"] -= 1
                else:
                    self.p2damage_receivedA2["damage"] = 0

            if self.p1damage > 0:
                damage += int((damage*self.p1damage)/100)
                self.p1damage = 0


            p2.hp -= (damage-olddamage)

            self.msg = f"{p1.name2} use *{p1.first_skill_name}*. Dealt {damage} damage."

            if affect and damage != 0:
                self.msg += f"\n{p1.name2} move is effective against {p2.name2}. Got 30% more of power"


            if not self.total_damage.get(p1.companion_id):
                self.total_damage[p1.companion_id] = 0

            self.total_damage[p1.companion_id] += (damage if p2hp > damage else p2hp)
        else:
            p1hp = p1.hp
            damage, heal, affect = p2.attack1(p1)
            if self.isImmune["p1"]["until"] == 0:
                #We check ability 1 of p2
                if self.p2damage_sentA1["damage"] > 0:
                    if self.p2damage_sentA1["until"] == -1:
                        damage += int((damage*self.p2damage_sentA1["damage"])/100)
                    elif self.p2damage_sentA1["until"] > 0:
                        damage += int((damage*self.p2damage_sentA1["damage"])/100)
                        self.p2damage_sentA1["until"] -= 1
                    else:
                        self.p2damage_sentA1["damage"] = 0
                #We check ability 2 of p2
                if self.p2damage_sentA2["damage"] > 0:
                    if self.p2damage_sentA2["until"] == -1:
                        damage += int((damage*self.p2damage_sentA2["damage"])/100)
                    elif self.p2damage_sentA2["until"] > 0:
                        damage += int((damage*self.p2damage_sentA2["damage"])/100)
                        self.p2damage_sentA2["until"] -= 1
                    else:
                        self.p2damage_sentA2["damage"] = 0
            else:
                self.isImmune["p1"]["until"] -= 1
            #We check ability 1 of p1
            if self.p1damage_receivedA1["damage"] > 0:
                if self.p1damage_receivedA1["until"] == -1:
                    damage -= int((damage*self.p1damage_receivedA1["damage"])/100)
                elif self.p1damage_receivedA1["until"] > 0:
                    damage -= int((damage*self.p1damage_receivedA1["damage"])/100)
                    self.p1damage_receivedA1["until"] -= 1
                else:
                    self.p1damage_receivedA1["damage"] = 0
            #We check ability 2 of p1
            if self.p1damage_receivedA2["damage"] > 0:
                if self.p1damage_receivedA2["until"] == -1:
                    damage -= int((damage*self.p1damage_receivedA2["damage"])/100)
                elif self.p1damage_receivedA2["until"] > 0:
                    damage -= int((damage*self.p1damage_receivedA2["damage"])/100)
                    self.p1damage_receivedA2["until"] -= 1
                else:
                    self.p1damage_receivedA2["damage"] = 0

            if self.p2damage > 0:
                print("p2 took self.p1damage in his ass", self.p2damage)
                damage += int((damage*self.p2damage)/100)
                self.p2damage = 0

            self.msg = f"{p2.name2} use *{p2.first_skill_name}*. Dealt {damage} damage."

            if affect and damage != 0:
                self.msg += f"\n{p2.name2} move is effective against {p1.name2}. Got 30% more of power"


            if not self.total_damage.get(p2.companion_id):
                self.total_damage[p2.companion_id] = 0
            self.total_damage[p2.companion_id] += (damage if p1hp > damage else p1hp)

        self.reload(call=call)

    def attack2(self, trn, call=None):
        if trn != self.crt_trn:
            return


        p1 = self.p1Companion()
        p2 = self.p2Companion()
        if self.player1_turn:
            p2hp = p2.hp
            damage, heal, affect = p1.attack2(p2)
            if self.isImmune["p2"]["until"] == 0:
                #We check ability 1 of p1
                if self.p1damage_sentA1["damage"] > 0:
                    if self.p1damage_sentA1["until"] == -1:
                        damage += int((damage*self.p1damage_sentA1["damage"])/100)
                    elif self.p1damage_sentA1["until"] > 0:
                        damage += int((damage*self.p1damage_sentA1["damage"])/100)
                        self.p1damage_sentA1["until"] -= 1
                    else:
                        self.p1damage_sentA1["damage"] = 0
                #We check ability 2 of p1
                if self.p1damage_sentA2["damage"] > 0:
                    if self.p2damage_sentA2["until"] == -1:
                        damage += int((damage*self.p1damage_sentA2["damage"])/100)
                    elif self.p2damage_sentA2["until"] > 0:
                        damage += int((damage*self.p1damage_sentA2["damage"])/100)
                        self.p2damage_sentA2["until"] -= 1
                    else:
                        self.p1damage_sentA2["damage"] = 0
            else:
                self.isImmune["p2"]["until"] -= 1
            #We check ability 1 of p2
            if self.p2damage_receivedA1["damage"] > 0:
                if self.p2damage_receivedA1["until"] == -1:
                    damage -= int((damage*self.p2damage_receivedA1["damage"])/100)
                elif self.p2damage_receivedA1["until"] > 0:
                    damage -= int((damage*self.p2damage_receivedA1["damage"])/100)
                    self.p2damage_receivedA1["until"] -= 1
                else:
                    self.p2damage_receivedA1["damage"] = 0
            #We check ability 2 of p2
            if self.p2damage_receivedA2["damage"] > 0:
                if self.p2damage_receivedA2["until"] == -1:
                    damage -= int((damage*self.p2damage_receivedA2["damage"])/100)
                elif self.p2damage_receivedA2["until"] > 0:
                    damage -= int((damage*self.p2damage_receivedA2["damage"])/100)
                    self.p2damage_receivedA2["until"] -= 1
                else:
                    self.p2damage_receivedA2["damage"] = 0

            if self.p1damage > 0:
                damage += int((damage*self.p1damage)/100)
                self.p1damage = 0

            self.msg = f"{p1.name2} use *{p1.second_skill_name}*. Dealt {damage} damage."

            if affect and damage != 0:
                self.msg += f"\n{p1.name2} move is effective against {p2.name2}. Got 30% more of power"


            if not self.total_damage.get(p1.companion_id):
                self.total_damage[p1.companion_id] = 0
            self.total_damage[p1.companion_id] += (damage if p2hp > damage else p2hp)
        else:
            p1hp = p1.hp
            damage, heal, affect = p2.attack2(p1)
            if self.isImmune["p1"]["until"] == 0:
                #We check ability 1 of p2
                if self.p2damage_sentA1["damage"] > 0:
                    if self.p2damage_sentA1["until"] == -1:
                        damage += int((damage*self.p2damage_sentA1["damage"])/100)
                    elif self.p2damage_sentA1["until"] > 0:
                        damage += int((damage*self.p2damage_sentA1["damage"])/100)
                        self.p2damage_sentA1["until"] -= 1
                    else:
                        self.p2damage_sentA1["damage"] = 0
                #We check ability 2 of p2
                if self.p2damage_sentA2["damage"] > 0:
                    if self.p2damage_sentA2["until"] == -1:
                        damage += int((damage*self.p2damage_sentA2["damage"])/100)
                    elif self.p2damage_sentA2["until"] > 0:
                        damage += int((damage*self.p2damage_sentA2["damage"])/100)
                        self.p2damage_sentA2["until"] -= 1
                    else:
                        self.p2damage_sentA2["damage"] = 0
            else:
                self.isImmune["p1"]["until"] -= 1
            #We check ability 1 of p1
            if self.p1damage_receivedA1["damage"] > 0:
                if self.p1damage_receivedA1["until"] == -1:
                    damage -= int((damage*self.p1damage_receivedA1["damage"])/100)
                elif self.p1damage_receivedA1["until"] > 0:
                    damage -= int((damage*self.p1damage_receivedA1["damage"])/100)
                    self.p1damage_receivedA1["until"] -= 1
                else:
                    self.p1damage_receivedA1["damage"] = 0
            #We check ability 2 of p1
            if self.p1damage_receivedA2["damage"] > 0:
                if self.p1damage_receivedA2["until"] == -1:
                    damage -= int((damage*self.p1damage_receivedA2["damage"])/100)
                elif self.p1damage_receivedA2["until"] > 0:
                    damage -= int((damage*self.p1damage_receivedA2["damage"])/100)
                    self.p1damage_receivedA2["until"] -= 1
                else:
                    self.p1damage_receivedA2["damage"] = 0

            if self.p2damage > 0:
                damage += int((damage*self.p2damage)/100)
                self.p2damage = 0

            self.msg = f"{p2.name2} use *{p2.second_skill_name}*. Dealt {damage} damage."

            if affect and damage != 0:
                self.msg += f"\n{p2.name2} move is effective against {p1.name2}. Got 30% more of power"



            if not self.total_damage.get(p2.companion_id):
                self.total_damage[p2.companion_id] = 0
            self.total_damage[p2.companion_id] += (damage if p1hp > damage else p1hp)

        self.reload(call=call)

    def timeout(self):
        msg = """{} didn't respond\n{} won the battle\n\nReward : 💰 {} Gold"""
        if self.player1_turn:

            UserData.query.filter_by(id = self.player2_info.id).update({UserData.gold: UserData.gold + self.p2_reward, UserData.total_win: UserData.total_win + 1})
            UserData.query.filter_by(id = self.player1_info.id).update({UserData.total_lose: UserData.total_lose + 1})
            db.session.commit()
            try:
                bot.edit_message_text(msg.format(module.createMention(self.player1_info), module.createMention(self.player2_info), self.p2_reward),
                	chat_id=self.group_info.id,
                	  message_id=self.msg_id)
            except:
                bot.reply_to(self.battle_msg, msg.format(module.createMention(self.player1_info), module.createMention(self.player2_info), self.p2_reward))

            self.doneBattle()

        else:

            UserData.query.filter_by(id = self.player1_info.id).update({UserData.gold: UserData.gold + self.p1_reward, UserData.total_win: UserData.total_win + 1})
            UserData.query.filter_by(id = self.player2_info.id).update({UserData.total_lose: UserData.total_lose + 1})
            db.session.commit()
            try:
                bot.edit_message_text(msg.format(module.createMention(self.player2_info), module.createMention(self.player1_info), self.p1_reward),
                	chat_id=self.group_info.id,
                	  message_id=self.msg_id)
            except:
                bot.reply_to(self.battle_msg, msg.format(module.createMention(self.player2_info), module.createMention(self.player1_info)))

            self.doneBattle()

    def p1AbilityMarkup(self, markup):
        p1 = self.p1Companion()

        markup.add(
            module.Btn(
            	text=p1.first_skill_name,
            	  calldata=f"attack1|{self.crt_trn}|{self.player1_info.id}"),
            module.Btn(
            	text=p1.second_skill_name,
            	  calldata=f"attack2|{self.crt_trn}|{self.player1_info.id}"),
            module.Btn(
            	text="Forfeit",
            	  calldata=f"forfeit|{self.crt_trn}|{self.player1_info.id}")
        )

        companion = self.p1Companion()
        cmpData = CompanionData.query.filter_by(owner=self.player1_info.id, name=int(companion.id)-1).first()

        try:
            ab1 = abilities.abilities[int(cmpData.ability1)]
        except:
            ab1 = None
        try:
            ab2 = abilities.abilities[int(cmpData.ability2)]
        except:
            ab2 = None
        try:
            ab3 = abilities.abilities[int(cmpData.ability3)]
        except:
            ab3 = None

        if self.leftUse['p1'] != 0:
            if cmpData.ability1 == None: #In fact, if 1 is null, others should be too.. but well.. in case of
                if cmpData.ability2 == None:
                    if cmpData.ability3 == None:
                        pass
                    else:
                        if not ab3.emote in self.used['p1']:
                            markup.add(module.Btn(
                            	text=f"📚 {ab3.name}",
                            	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player1_info.id}"))
                else:
                    if cmpData.ability3 == None:
                        if not ab2.emote in self.used['p1']:
                            markup.add(module.Btn(
                            	text=f"📚 {ab2.name}",
                            	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player1_info.id}"))
                    else:
                        if not ab2.emote in self.used['p1']:
                            if not ab3.emote in self.used['p1']:
                                markup.add(
                                    module.Btn(
                                    	text=f"📚 {ab2.name}",
                                    	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player1_info.id}"),
                                    module.Btn(
                                    	text=f"📚 {ab3.name}",
                                    	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player1_info.id}")
                                )
                            else:
                                markup.add(module.Btn(
                                	text=f"📚 {ab2.name}",
                                	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player1_info.id}"))

            else:
                if cmpData.ability2 == None:
                    if cmpData.ability3 == None:
                        if not ab1.emote in self.used['p1']:
                            markup.add(module.Btn(
                            	text=f"📚 {ab1.name}",
                            	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player1_info.id}"))
                    else:
                        if not ab1.emote in self.used['p1']:
                            if not ab3.emote in self.used['p1']:
                                markup.add(
                                    module.Btn(
                                    	text=f"📚 {ab1.name}",
                                    	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player1_info.id}"),
                                    module.Btn(
                                    	text=f"📚 {ab3.name}",
                                    	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player1_info.id}")
                                )
                            else:
                                markup.add(module.Btn(
                                	text=f"📚 {ab1.name}",
                                	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player1_info.id}"))

                else:
                    if cmpData.ability3 == None:
                        if not ab1.emote in self.used['p1']:
                            if not ab2.emote in self.used['p1']:
                                markup.add(
                                    module.Btn(
                                    	text=f"📚 {ab1.name}",
                                    	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player1_info.id}"),
                                    module.Btn(
                                    	text=f"📚 {ab2.name}",
                                    	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player1_info.id}")
                                )
                            else:
                                markup.add(module.Btn(
                                	text=f"📚 {ab1.name}",
                                	  calldata=f"useA{cmpData.ability1}|{self.player1_info.id}"))

                    else:
                        if not ab1.emote in self.used['p1']:
                            if not ab2.emote in self.used['p1']:
                                if not ab3.emote in self.used['p1']:
                                    markup.add(
                                        module.Btn(
                                        	text=f"📚 {ab1.name}",
                                        	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player1_info.id}"),
                                        module.Btn(
                                        	text=f"📚 {ab2.name}",
                                        	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player1_info.id}"),
                                        module.Btn(
                                        	text=f"📚 {ab3.name}",
                                        	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player1_info.id}")
                                    )
                                else:
                                    markup.add(
                                        module.Btn(
                                        	text=f"📚 {ab1.name}",
                                        	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player1_info.id}"),
                                        module.Btn(
                                        	text=f"📚 {ab2.name}",
                                        	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player1_info.id}")
                                    )
                            else:
                                markup.add(module.Btn(
                                	text=f"📚 {ab1.name}",
                                	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player1_info.id}"))
                        else:
                            if not ab2.emote in self.used['p1']:
                                if not ab3.emote in self.used['p1']:
                                    markup.add(
                                        module.Btn(
                                        	text=f"📚 {ab2.name}",
                                        	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player1_info.id}"),
                                        module.Btn(
                                        	text=f"📚 {ab3.name}",
                                        	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player1_info.id}")
                                    )
                                else:
                                    markup.add(
                                        module.Btn(
                                        	text=f"📚 {ab2.name}",
                                        	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player1_info.id}"),
                                    )
                            else:
                                if not ab3.emote in self.used['p1']:
                                    markup.add(
                                        module.Btn(
                                        	text=f"📚 {ab3.name}",
                                        	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player1_info.id}")
                                    )



        return markup

    def p2AbilityMarkup(self, markup):
        p2 = self.p2Companion()

        markup.add(
            module.Btn(
            	text=p2.first_skill_name,
            	  calldata=f"attack1|{self.crt_trn}|{self.player2_info.id}"),
            module.Btn(
            	text=p2.second_skill_name,
            	  calldata=f"attack2|{self.crt_trn}|{self.player2_info.id}"),
            module.Btn(
            	text="Forfeit",
            	  calldata=f"forfeit|{self.crt_trn}|{self.player2_info.id}")
        )

        companion = self.p2Companion()
        cmpData = CompanionData.query.filter_by(owner=self.player2_info.id, name=int(companion.id)-1).first()


        try:
            ab1 = abilities.abilities[int(cmpData.ability1)]
        except:
            pass
        try:
            ab2 = abilities.abilities[int(cmpData.ability2)]
        except:
            pass
        try:
            ab3 = abilities.abilities[int(cmpData.ability3)]
        except:
            pass


        if self.leftUse['p2'] != 0:
            if cmpData.ability1 == None: #In fact, if 1 is null, others should be too.. but well.. in case of
                if cmpData.ability2 == None:
                    if cmpData.ability3 == None:
                        pass
                    else:
                        if not ab3.emote in self.used['p2']:
                            markup.add(module.Btn(
                            	text=f"📚 {ab3.name}",
                            	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player2_info.id}"))
                else:
                    if cmpData.ability3 == None:
                        if not ab2.emote in self.used['p2']:
                            markup.add(module.Btn(
                            	text=f"📚 {ab2.name}",
                            	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player2_info.id}"))
                    else:
                        if not ab2.emote in self.used['p2']:
                            if not ab3.emote in self.used['p2']:
                                markup.add(
                                    module.Btn(
                                    	text=f"📚 {ab2.name}",
                                    	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player2_info.id}"),
                                    module.Btn(
                                    	text=f"📚 {ab3.name}",
                                    	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player2_info.id}")
                                )
                            else:
                                markup.add(module.Btn(
                                	text=f"📚 {ab2.name}",
                                	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player2_info.id}"))

            else:
                if cmpData.ability2 == None:
                    if cmpData.ability3 == None:
                        if not ab1.emote in self.used['p2']:
                            markup.add(module.Btn(
                            	text=f"📚 {ab1.name}",
                            	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player2_info.id}"))
                    else:
                        if not ab1.emote in self.used['p2']:
                            if not ab3.emote in self.used['p2']:
                                markup.add(
                                    module.Btn(
                                    	text=f"📚 {ab1.name}",
                                    	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player2_info.id}"),
                                    module.Btn(
                                    	text=f"📚 {ab3.name}",
                                    	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player2_info.id}")
                                )
                            else:
                                markup.add(module.Btn(
                                	text=f"📚 {ab1.name}",
                                	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player2_info.id}"))

                else:
                    if cmpData.ability3 == None:
                        if not ab1.emote in self.used['p2']:
                            if not ab2.emote in self.used['p2']:
                                markup.add(
                                    module.Btn(
                                    	text=f"📚 {ab1.name}",
                                    	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player2_info.id}"),
                                    module.Btn(
                                    	text=f"📚 {ab2.name}",
                                    	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player2_info.id}")
                                )
                            else:
                                markup.add(module.Btn(
                                	text=f"📚 {ab1.name}",
                                	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player2_info.id}"))

                    else:
                        if not ab1.emote in self.used['p2']:
                            if not ab2.emote in self.used['p2']:
                                if not ab3.emote in self.used['p2']:
                                    markup.add(
                                        module.Btn(
                                        	text=f"📚 {ab1.name}",
                                        	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player2_info.id}"),
                                        module.Btn(
                                        	text=f"📚 {ab2.name}",
                                        	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player2_info.id}"),
                                        module.Btn(
                                        	text=f"📚 {ab3.name}",
                                        	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player2_info.id}")
                                    )
                                else:
                                    markup.add(
                                        module.Btn(
                                        	text=f"📚 {ab1.name}",
                                        	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player2_info.id}"),
                                        module.Btn(
                                        	text=f"📚 {ab2.name}",
                                        	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player2_info.id}")
                                    )
                            else:
                                markup.add(module.Btn(
                                	text=f"📚 {ab1.name}",
                                	  calldata=f"useA{cmpData.ability1}|{self.crt_trn}|{self.player2_info.id}"))
                        else:
                            if not ab2.emote in self.used['p2']:
                                if not ab3.emote in self.used['p2']:
                                    markup.add(
                                        module.Btn(
                                        	text=f"📚 {ab2.name}",
                                        	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player2_info.id}"),
                                        module.Btn(
                                        	text=f"📚 {ab3.name}",
                                        	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player2_info.id}")
                                    )
                                else:
                                    markup.add(
                                        module.Btn(
                                        	text=f"📚 {ab2.name}",
                                        	  calldata=f"useA{cmpData.ability2}|{self.crt_trn}|{self.player2_info.id}"),
                                    )
                            else:
                                if not ab3.emote in self.used['p2']:
                                    markup.add(
                                        module.Btn(
                                        	text=f"📚 {ab3.name}",
                                        	  calldata=f"useA{cmpData.ability3}|{self.crt_trn}|{self.player2_info.id}")
                                    )


        return markup

    def p1UpdateAbility(self):
        if self.FrozeArtifact['p1'] == 0:
            try:
                self.inUse['p1'].remove("❄️")
            except:
                pass
        if self.HealingRing['p1'] == 0:
            try:
                self.inUse['p1'].remove("💛")
            except:
                pass
        if self.HealingRingII['p1'] == 0:
            try:
                self.inUse['p1'].remove("💛")
            except:
                pass
        if self.BlueFragment['p1'] == 0:
            try:
                self.inUse['p1'].remove("💀")
            except:
                pass
        if self.RedFragment['p1'] == 0:
            try:
                self.inUse['p1'].remove("📕")
            except:
                pass
        if self.GreenFragment['p1'] == 0:
            try:
                self.inUse['p1'].remove("📗")
            except:
                pass
        if self.BlueFragmentII['p1'] == 0:
            try:
                self.inUse['p1'].remove("📘")
            except:
                pass
        if self.RedFragmentII['p1'] == 0:
            try:
                self.inUse['p1'].remove("📕")
            except:
                pass
        if self.GreenFragmentII['p1'] == 0:
            try:
                self.inUse['p1'].remove("📗")
            except:
                pass
        if self.BlackRelics['p1'] == 0:
            try:
                self.inUse['p1'].remove("🔐")
            except:
                pass
        if self.LightRelics['p1'] == 0:
            try:
                self.inUse['p1'].remove("🔑")
            except:
                pass
        if self.GodsEye['p1'] == 0:
            try:
                self.inUse['p1'].remove("👁")
            except:
                pass
        if self.EmeraldShards['p1'] == 0:
            try:
                self.inUse['p1'].remove("✳️")
            except:
                pass

        if self.FrozeArtifact['p1'] != 0:
            self.FrozeArtifact['p1'] -= 1
        if self.HealingRing['p1'] != 0:
            self.HealingRing['p1'] -= 1
        if self.HealingRingII['p1'] != 0:
            self.HealingRingII['p1'] -= 1
        if self.BlueFragment['p1'] != 0:
            self.BlueFragment['p1'] -= 1
        if self.RedFragment['p1'] != 0:
            self.RedFragment['p1'] -= 1
        if self.GreenFragment['p1'] != 0:
            self.GreenFragment['p1'] -= 1
        if self.BlueFragmentII['p1'] != 0:
            self.BlueFragmentII['p1'] -= 1
        if self.RedFragmentII['p1'] != 0:
            self.RedFragmentII['p1'] -= 1
        if self.GreenFragmentII['p1'] != 0:
            self.GreenFragmentII['p1'] -= 1
        if self.BlackRelics['p1'] != 0 and self.player1_turn:
            self.BlackRelics['p1'] -= 1
        if self.LightRelics['p1'] != 0:
            self.LightRelics['p1'] -= 1
        if self.GodsEye['p1'] != 0:
            self.GodsEye['p1'] -= 1
        if self.EmeraldShards['p1'] != 0:
            self.EmeraldShards['p1'] -= 1

    def p2UpdateAbility(self):
        if self.FrozeArtifact['p2'] == 0:
            try:
                self.inUse['p2'].remove("❄️")
            except:
                pass
        if self.HealingRing['p2'] == 0:
            try:
                self.inUse['p2'].remove("💛")
            except:
                pass
        if self.HealingRingII['p2'] == 0:
            try:
                self.inUse['p2'].remove("💛")
            except:
                pass
        if self.BlueFragment['p2'] == 0:
            try:
                self.inUse['p2'].remove("💀")
            except:
                pass
        if self.RedFragment['p2'] == 0:
            try:
                self.inUse['p2'].remove("📕")
            except:
                pass
        if self.GreenFragment['p2'] == 0:
            try:
                self.inUse['p2'].remove("📗")
            except:
                pass
        if self.BlueFragmentII['p2'] == 0:
            try:
                self.inUse['p2'].remove("📘")
            except:
                pass
        if self.RedFragmentII['p2'] == 0:
            try:
                self.inUse['p2'].remove("📕")
            except:
                pass
        if self.GreenFragmentII['p2'] == 0:
            try:
                self.inUse['p2'].remove("📗")
            except:
                pass
        if self.BlackRelics['p2'] == 0:
            try:
                self.inUse['p2'].remove("🔐")
            except:
                pass
        if self.LightRelics['p2'] == 0:
            try:
                self.inUse['p2'].remove("🔑")
            except:
                pass
        if self.GodsEye['p2'] == 0:
            try:
                self.inUse['p2'].remove("👁")
            except:
                pass
        if self.EmeraldShards['p2'] == 0:
            try:
                self.inUse['p2'].remove("✳️")
            except:
                pass


        if self.FrozeArtifact['p2'] != 0:
            self.FrozeArtifact['p2'] -= 1
        if self.HealingRing['p2'] != 0:
            self.HealingRing['p2'] -= 1
        if self.HealingRingII['p2'] != 0:
            self.HealingRingII['p2'] -= 1
        if self.BlueFragment['p2'] != 0:
            self.BlueFragment['p2'] -= 1
        if self.RedFragment['p2'] != 0:
            self.RedFragment['p2'] -= 1
        if self.GreenFragment['p2'] != 0:
            self.GreenFragment['p2'] -= 1
        if self.BlueFragmentII['p2'] != 0:
            self.BlueFragmentII['p2'] -= 1
        if self.RedFragmentII['p2'] != 0:
            self.RedFragmentII['p2'] -= 1
        if self.GreenFragmentII['p2'] != 0:
            self.GreenFragmentII['p2'] -= 1

        if self.BlackRelics['p2'] != 0 and not self.player1_turn:
            self.BlackRelics['p2'] -= 1
        if self.LightRelics['p2'] != 0:
            self.LightRelics['p2'] -= 1
        if self.GodsEye['p2'] != 0:
            self.GodsEye['p2'] -= 1
        if self.EmeraldShards['p2'] != 0:
            self.EmeraldShards['p2'] -= 1


    def reload(self, change_turn=True, call=None):
        if change_turn:
            self.player1_turn = not self.player1_turn
            self.state = str(self.player1_turn) + str(self.turn+1) + str(random.randint(99, 9999))
            self.crt_trn += 1

        p1 = self.p1Companion()
        p2 = self.p2Companion()

        msg = "{} won the battle\n\nReward : 💰 {} Gold"
        if not p1:
            UserData.query.filter_by(id = self.player2_info.id).update({UserData.gold: UserData.gold + self.p2_reward, UserData.total_win: UserData.total_win + 1})
            UserData.query.filter_by(id = self.player1_info.id).update({UserData.total_lose: UserData.total_lose + 1})
            db.session.commit()

            bot.edit_message_text(msg.format(module.createMention(self.player2_info), self.p2_reward),
            	chat_id=self.group_info.id,
            	  message_id=self.msg_id)

            self.doneBattle()
            return

        if not p2:
            UserData.query.filter_by(id = self.player1_info.id).update({UserData.gold: UserData.gold + self.p1_reward, UserData.total_win: UserData.total_win + 1})
            UserData.query.filter_by(id = self.player2_info.id).update({UserData.total_lose: UserData.total_lose + 1})
            db.session.commit()

            bot.edit_message_text(msg.format(module.createMention(self.player1_info), self.p1_reward),
            	chat_id=self.group_info.id,
            	  message_id=self.msg_id)

            self.doneBattle()
            return

        msg = ""
        if self.player1_turn:
            markup = module.Mkd()
            markup = self.p1AbilityMarkup(markup)

            if self.isBurning["p1"]["state"] and not self.isImmune["p1"]["state"]:
                if self.isBurning["p1"]["until"] > 0:
                    msg = f"You're still burning. You lose {self.isBurning['p1']['damage']} Hp"
                    p1.hp -= self.isBurning["p1"]["damage"]

                    self.isBurning["p1"]["until"] -= 1
                else:
                    self.isBurning["p1"]["state"] = False
                    self.isBurning["p1"]["until"] = None

        else:
            markup = module.Mkd()
            markup = self.p2AbilityMarkup(markup)

            if self.isBurning["p2"]["state"] and not self.isImmune["p2"]["state"]:
                if self.isBurning["p2"]["until"] > 0:
                    msg = f"You're still burning. You lose {self.isBurning['p2']['damage']} Hp"
                    p2.hp -= self.isBurning["p2"]["damage"]

                    self.isBurning["p2"]["until"] -= 1
                else:
                    self.isBurning["p2"]["state"] = False
                    self.isBurning["p2"]["until"] = None


        msg += self.getMsg(self.p1Companion(), self.p2Companion())
        bot.edit_message_text(msg,
        	chat_id=self.group_info.id,
        	  message_id=self.msg_id,
        	  	reply_markup = markup)


        if self.player1_turn:
            if self.isFreeze["p2"] and not self.isImmune["p2"]["state"]:
                time.sleep(0.1)
                bot.edit_message_text("You are froze due to opponent ability.",
                	chat_id=self.group_info.id,
                	  message_id=self.msg_id)
                time.sleep(2)

                self.isFreeze["p2"] = False
                self.reload(call=call)

        else:
            if self.isFreeze["p1"] and not self.isImmune["p1"]["state"]:
                time.sleep(0.1)
                bot.edit_message_text("You are froze due to opponent ability.",
                	chat_id=self.group_info.id,
                	  message_id=self.msg_id)
                time.sleep(2)

                self.isFreeze["p1"] = False
                self.reload(call=call)


        if self.isImmune["p1"]["until"] != 0 and self.isImmune["p1"]["until"] != -1:
            self.isImmune["p1"]["until"] -= 1
            if self.isImmune["p1"]["until"] == 0:
                self.isImmune["p1"]["state"] = False
        if self.isImmune["p2"]["until"] != 0 and self.isImmune["p2"]["until"] != -1:
            self.isImmune["p2"]["until"] -= 1
            if self.isImmune["p2"]["until"] == 0:
                self.isImmune["p2"]["state"] = False

        if self.isLocked["p1"]["until"] != 0 and self.isLocked["p1"]["until"] != -1:
            self.isLocked["p1"]["until"] -= 1
            if self.isLocked["p1"]["until"] == 0:
                self.isLocked["p1"]["state"] = False
        if self.isLocked["p2"]["until"] != 0 and self.isLocked["p2"]["until"] != -1:
            self.isLocked["p2"]["until"] -= 1
            if self.isLocked["p2"]["until"] == 0:
                self.isLocked["p2"]["state"] = False


        self.p1UpdateAbility()
        self.p2UpdateAbility()

        self.startTimer(self.state, call=call)
