""" Quest room """

from tbot import bot
from telebot import types
from database import db, UserData, CompanionData, PositionData, BossArena
import characters, boss, abilities
import module
import random, time, threading


QUEST_RING = {}
BOOKS = {}



class Quest:
    def __init__(self, message, player):
        self.quest_msg = message
        self.quest_chat = message.chat

        self.questMsg = None #Bot quest message
        self.questMessage = "Start fighting with your opponent for awesome rewards!!"

        self.state = 0

        self.player = player
        self.player_id = player.id

        self.character = None
        self.player_companions = []

        self.position()
        self.total_damage = {}

    def start(self, n):
        msg = f"You're on your *{n}/25* daily quest!\n"

        #if random.randint(0, 1) == 1:
        if random.randint(0, 99) == 69:
            #Cool, 1% of poping this trader
            msg += "__Welcome in Quest!__\n\nYou just found the book trader!\nClick the book you want to buy (You can buy only one)"
            mkp = module.Mkd()

            PROBA = [1, 10, 3, 7, 14, 14, 14, 5, 5, 4, 5, 5, 2, 6]
            nums = []
            BOOKS[self.player_id] = []

            for b in PROBA:
                nums.append( (b*14)/100 )

            for loop in range(3):
                x = random.choice(nums)
                while nums.index(x) in BOOKS[self.player_id]:
                    x = random.choice(nums)
                BOOKS[self.player_id].append(nums.index(x))

            for b in BOOKS[self.player_id]:
                a = abilities.abilities[b]
                mkp.add(module.Btn(f"{a.emote}{a.name}", calldata=f"questT{a.number}|{self.player_id}"))

            self.questMsg = bot.reply_to(self.quest_msg, msg, reply_markup=mkp)
            return

        ch_list = characters.characters
        rndm = random.randint(0, len(ch_list)-1)
        ch = ch_list[rndm]

        #self.character = ch
        self.character = characters.characters[rndm](random.randint(1, 100), companion_id=6660666)

        msg += f"__Welcome in Quest!__\n\n*{ch.name}* lvl{self.character.level} just popped in! Let's fight"

        mkp = module.Mkd()
        mkp.add(module.Btn(f"Attack ⚔️", calldata=f"questF{rndm}|{self.player_id}"))
        self.questMsg = bot.reply_to(self.quest_msg, msg, reply_markup=mkp)

    def attack(self):

        msg = self.getMsg()

        mkp = module.Mkd()
        mkp.add(module.Btn(f"{self.character.first_skill_name}️", calldata=f"questA1|{self.player_id}"), module.Btn(f"{self.character.second_skill_name}", calldata=f"questA2|{self.player_id}"))
        mkp.add(module.Btn(f"Forfeit", calldata=f"questL|{self.player_id}"))
        bot.edit_message_text(msg, chat_id=self.quest_chat.id, message_id=self.questMsg.id, reply_markup=mkp)

    def attack1(self):
        #Attack
        p1 = self.getCompanion()
        p2 = self.character

        damage, heal, affect = p1.attack1(p2)
        if heal is None:
            #p2.hp -= damage
            self.questMessage = f"🗡You inflicted *{abs(damage)}* damage to {p2.name} with *{p1.first_skill_name}*"

        else:
            if damage is None:
                #p1.hp += heal
                #if p1.hp > p1.totalHp:
                #    p1.hp = p1.totalHp

                self.questMessage = f"❤️ You just healed of *{abs(heal)}HP* with *{p1.first_skill_name}*"
            else:
                #p2.hp -= damage
                #p1.hp += heal
                self.questMessage = f"""❤️🗡 You just healed of *{abs(heal)}HP* and inflicted *{damage}*HP tp {p2.name} with *{p1.first_skill_name}*"""


        if not self.total_damage.get(p1.companion_id):
            self.total_damage[p1.companion_id] = 0
        self.total_damage[p1.companion_id] += (damage if p2.hp > damage else p2.hp)


        msg = self.getMsg()
        mkp = module.Mkd()
        mkp.add(module.Btn(f"{p1.first_skill_name}️", calldata=f"questA1|{self.player_id}"), module.Btn(f"{p1.second_skill_name}", calldata=f"questA2|{self.player_id}"))
        mkp.add(module.Btn(f"Forfeit", calldata=f"questL|{self.player_id}"))
        bot.edit_message_text(msg, chat_id=self.quest_chat.id, message_id=self.questMsg.id, reply_markup=mkp)
        self.reload()

    def attack2(self):
        #Attack
        p1 = self.getCompanion()
        p2 = self.character

        damage, heal, affect = p1.attack2(p2)

        if heal is None:
            #p2.hp -= damage
            self.questMessage = f"🗡You inflicted *{abs(damage)}* damage to {p2.name} with *{p1.second_skill_name}*"

        else:
            if damage is None:
                #p1.hp += heal
                #if p1.hp > p1.totalHp:
                #    p1.hp = p1.totalHp

                self.questMessage = f"❤️ You just healed of *{abs(heal)}HP* with *{p1.second_skill_name}*"
            else:
                #p2.hp -= damage
                #p1.hp += heal
                self.questMessage = f"""❤️🗡 You just healed of *{abs(heal)}HP* and inflicted *{damage}*HP to {p2.name} with *{p1.second_skill_name}*"""


        if not self.total_damage.get(p1.companion_id):
            self.total_damage[p1.companion_id] = 0
        self.total_damage[p1.companion_id] += (damage if p2.hp > damage else p2.hp)


        msg = self.getMsg()
        mkp = module.Mkd()
        mkp.add(module.Btn(f"{p1.first_skill_name}️", calldata=f"questA1|{self.player_id}"), module.Btn(f"{p1.second_skill_name}", calldata=f"questA2|{self.player_id}"))
        mkp.add(module.Btn(f"Forfeit", calldata=f"questL|{self.player_id}"))
        bot.edit_message_text(msg, chat_id=self.quest_chat.id, message_id=self.questMsg.id, reply_markup=mkp)
        self.reload()

    def reload(self):
        p1 = self.companion()
        if p1 is None:
            self.won("p2")
            return

        p2 = self.character

        if p2.hp <= 0:
            self.won("p1")
            return

        time.sleep(2)
        if random.randint(0,1) == 1:
            if p2.level >= 50:
                skill = p2.second_skill_name
                damage, heal, affect = p2.attack2(p1)
            else:
                skill = p2.first_skill_name
                damage, heal, affect = p2.attack1(p1)
        else:
            skill = p2.first_skill_name
            damage, heal, affect = p2.attack1(p1)

        if heal is None:
            #p1.hp -= damage
            self.questMessage = f"🗡{p2.name} inflicted you *{abs(damage)}* damage with *{skill}*"

        else:
            if damage is None:
                #p2.hp += heal
                #if p2.hp > p2.totalHp:
                #    p2.hp = p1.totalHp

                self.questMessage = f"❤️ {p2.name} just healed of *{abs(heal)}HP* with *{skill}*"
            else:
                #p1.hp -= damage
                #p2.hp += heal
                self.questMessage = f"""❤️🗡 {p2.name} just healed of *{abs(heal)}HP* and inflicted you *{damage}*HP with *{skill}*"""


        p1 = self.companion()
        if p1 is None:
            self.won("p2")
        else:
            msg = self.getMsg()
            mkp = module.Mkd()
            mkp.add(module.Btn(f"{p1.first_skill_name}️", calldata=f"questA1|{self.player_id}"), module.Btn(f"{p1.second_skill_name}", calldata=f"questA2|{self.player_id}"))
            mkp.add(module.Btn(f"Forfeit", calldata=f"questL|{self.player_id}"))
            bot.edit_message_text(msg, chat_id=self.quest_chat.id, message_id=self.questMsg.id, reply_markup=mkp)


    def won(self, who):
        self.state = 0

        for companion_id, damage in self.total_damage.items():
            damage = abs(damage)
            # cur.execute(f"UPDATE companion SET exp = exp + {damage // 2} WHERE companion_id = {companion_id}")
            module.addExp(companion_id, damage // 5)

        self.total_damage = {}

        mkp = module.Mkd()
        if who == "p1":

            gold = int(self.character.level * 1.5)
            prize = f"{gold}💰"
            book = "rip"

            if random.randint(0,1000) in range(1*self.character.level):
                book = abilities.abilities[random.randint(0,len(abilities.abilities)-1)]
                prize += f" and a {book.emote}{book.name} book !!"

                book = book.number

            mkp.add(module.Btn("Claim your prize", calldata=f"questC-g{gold}-b{book}|{self.player_id}"))
            msg = f"You defeated {self.character.name}!\nYou won {prize}\nDon't forget to claim or it will be lose!"
            bot.edit_message_text(msg, chat_id=self.quest_chat.id, message_id=self.questMsg.id, reply_markup=mkp)
        else:
            msg = f"You lose. {self.character.name} was more strong than you..\nUpgrade your companions and come later"
            mkp.add(module.Btn("Leave", calldata=f"questL|{self.player_id}"))
            bot.edit_message_text(msg, chat_id=self.quest_chat.id, message_id=self.questMsg.id, reply_markup=mkp)

    def getMsg(self):
        ch = self.getCompanion()
        msg = f"""{self.questMessage}\n\n\n{module.createMention(self.player)} - *{ch.name_ne}*\n*Lv.* {ch.level}, *HP:* _{ch.hp}/{ch.totalHp}_\n{module.getBarPersentase(ch.hp, ch.totalHp)}\n\nOpponent - *{self.character.name}*\n*HP:* _{int(self.character.hp)}/{self.character.totalHp}_\n{module.getBarPersentase(self.character.hp,self.character.totalHp)}\n"""
        return msg

    def getCompanion(self):
        return self.companion(getLast=True)

    def position(self):
        player_companions = CompanionData.query.filter_by(owner=self.player_id).all()
        player_position = PositionData.query.filter_by(id=self.player_id).first()

        if not player_position:
            companionList = player_companions[:3]
            position1 = companionList[0].name
            position2 = companionList[1].name if len(companionList) >= 2 else None
            position3 = companionList[2].name if len(companionList) >= 3 else None

            addData = PositionData(self.player_id, position1, position2, position3)
            db.session.add(addData)
            db.session.commit()
            player_position = PositionData.query.filter_by(id=self.player_id).first()

        player_position = (player_position.position1, player_position.position2, player_position.position3)

        for x in player_position:
            for y in player_companions:
                if x == y.name:
                    self.player_companions.append(characters.characters[x](y.level, companion_id=y.companion_id))

    def companion(self, getLast=False):
        for i, x in enumerate(self.player_companions.copy()):
            if not x.isDead():
                return x

            if not getLast:
                bot.edit_message_text(f"{x.name} died!", chat_id = self.quest_chat.id, message_id = self.questMsg.id)
                del self.player_companions[i]
                time.sleep(2)

    def leave(self):
        bot.edit_message_text("You started another quest / forceleaved, and this one was terminated.", chat_id=self.quest_chat.id, message_id=self.questMsg.id)
        del QUEST_RING[self.player_id]
