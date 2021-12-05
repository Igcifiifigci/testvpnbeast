""" Arena room """

from tbot import bot
from telebot import types
from database import db, UserData, CompanionData, PositionData, BossArena
import characters, boss, abilities
import module
import random, time, threading


BOSS = boss.bossList
BOSS_ARENA = {}
IN_ARENA = {}


def noInArena(tele_id):
    return not tele_id in IN_ARENA.keys()


class TimerArena:
    PENDING = {}

    def __init__(self):
        self.id = random.randint(0, 1_000_000_000)

    def execute(self, when, call=None):
        def timeout(self, when):
            if when == self.state:
                ArenaBoss.timeout(self)
            else:
                pass

        try:
            threading.Timer(520, timeout, [self, when]).start()
        except:
            try:
                bot.answer_callback_query(callback_query_id=call, text="Sorry, I crashed. You can still play but without any timer")
            except:
                pass #Cuz when starting their is not call to reply..
        return #RuntimeError: can't start new thread


class ArenaBoss:
    def __init__(self, player_info, channel_info, message):
        self.state = 0
        self.crt_trn = 0

        self.channel_info = channel_info
        self.player_info = player_info
        self.arena_message = None
        self.command_arena = message
        self.first = False

        self.currentBoss = None

        self.infight_msg = "Battle begins!"
        self.player_companions = []
        self._player_companions = []

        self.advtges = 0
        self.disadvtges = 0

        IN_ARENA[player_info.id] = int(time.time()) + 169

        self.update()

        names = []
        for bosS in range(5):
            names.append(BOSS[bosS].name)

        self.position()

        self.home_msg = f"""🔱 Welcome to ⚔️ Boss Arena ⚔️\n\n⚠️ Battle with deadly bosses and gain awsome rewards\n\n1st Floor - {names[0]} {self.won[0]}\n2nd Floor - {names[1]} {self.won[1]}\n3rd Floor - {names[2]} {self.won[2]}\n4th Floor - {names[3]} {self.won[3]}\n5th Floor - {names[4]} {self.won[4]}"""
        msg = self.home_msg

        self.markup = module.Mkd()
        self.markup.add(
        	module.Btn(
	        	text=names[0],
	        	  calldata=f"boss0|{self.player_info.id}"),

        	module.Btn(
        		text=names[1],
        		  calldata=f"boss1|{self.player_info.id}"),

       	  	module.Btn(
	        	text=names[2],
    	    	  calldata=f"boss2|{self.player_info.id}")
       	)

        self.markup.add(
    		module.Btn(
    			text=names[3],
    	  		  calldata=f"boss3|{self.player_info.id}"),
        	module.Btn(
        		text=names[4],
        		  calldata=f"boss4|{self.player_info.id}")
        )

        self.markup.add(
        	module.Btn(
 				text="Cancel",
        		  calldata=f"cancelboss|{self.player_info.id}")
        )

        markup = self.markup
        self.arena_message = bot.reply_to(message, msg, reply_markup=markup)


    def update(self):
        self.userstats = BossArena.query.filter_by(id=self.player_info.id).first()
        if not self.userstats:
            createStats = BossArena(self.player_info.id, 0, 0, 0, 0, 0, 0, 0, 0)
            db.session.add(createStats)
            db.session.commit()

            self.userstats = BossArena.query.filter_by(id=self.player_info.id).first()

        self.level = self.userstats.level

        self.won = ["🔐", "🔐", "🔐", "🔐", "🔐"]
        i=0
        for boss_defeated in range(self.level):
            self.won[i] = "🗡"
            i+=1

        names = []
        for bosS in range(5):
            names.append(BOSS[bosS].name)

        self.home_msg = f"""🔱 Welcome to ⚔️ Boss Arena ⚔️\n\n⚠️ Battle with deadly bosses and gain awsome rewards\n\n1st Floor - {names[0]} {self.won[0]}\n2nd Floor - {names[1]} {self.won[1]}\n3rd Floor - {names[2]} {self.won[2]}\n4th Floor - {names[3]} {self.won[3]}\n5th Floor - {names[4]} {self.won[4]}"""


    def getMsg(self, characterObject1):
        msg = f"{self.infight_msg}\n\n\n{module.createMention(self.player_info)} - *{characterObject1[0].name}*\n*Lv.* {characterObject1[0].level}, *HP:* _{characterObject1[0].hp}/{characterObject1[0].totalHp}_\n{module.getBarPersentase(characterObject1[0].hp, characterObject1[0].totalHp)}\n\nLevel {self.currentBoss.lvl} - *{self.currentBoss.name}*\n*HP:* _{int(self.currentBoss.hp)}/{self.currentBoss.nowHp}_\n{module.getBarPersentase(self.currentBoss.hp,self.currentBoss.nowHp)}"
        return msg

    def position(self):
        player_companions = CompanionData.query.filter_by(owner = self.player_info.id).all()
        player_position = PositionData.query.filter_by(id = self.player_info.id).first()

        if not player_position:
            companionList = player_companions[:3]
            position1 = companionList[0].name
            position2 = companionList[1].name if len(companionList) >= 2 else None
            position3 = companionList[2].name if len(companionList) >= 3 else None

            addData = PositionData(self.player_info.id, position1, position2, position3)
            db.session.add(addData)
            db.session.commit()
            player_position = PositionData.query.filter_by(id = self.player_info.id).first()

        player_position = (player_position.position1, player_position.position2, player_position.position3)

        for x in player_position:


            for y in player_companions:
                if x == y.name:
                    self.player_companions.append(characters.characters[x](y.level, companion_id = y.companion_id))
                #break

    def companion(self):
        for i, x in enumerate(self.player_companions.copy()):
            #self._player_companions.append(x)
            if not x.isDead():
                return x

            bot.edit_message_text(f"{x.name} died!",
            	chat_id=self.channel_info.id,
            	  message_id=self.arena_message.id)

            del self.player_companions[i]
            #del self._player_companions[i]
            time.sleep(2)


    def attack1(self, trn, call=None):
        if trn != self.crt_trn:
            return

        player = self.companion()

        damage, heal, affect = player.attack1(self.currentBoss, self.disadvtges, arena=True)

        alive = self.companion()
        if not alive:
            msg = f"You died. Try to upgrade your companions!"

            markup = module.Mkd()
            markup.add(
                module.Btn(
                	text="Back to Home",
                	  calldata=f"gohome|{self.player_info.id}")
            )
            bot.edit_message_text(msg,
            	chat_id=self.channel_info.id,
            	  message_id=self.arena_message.id,
            	    reply_markup=markup)

            self.doneArena(False)
            return


        if heal == None:
            self.infight_msg = f"You inflicted *{int(damage)}* damage to *{self.currentBoss.name}* with *{player.first_skill_name}*"
        else:
            if heal < 0:
                self.infight_msg = f"You lose *{abs(heal)}HP* and inflicted *{int(damage)}* damage to *{self.currentBoss.name}* with *{player.first_skill_name}*"
            else:
                self.infight_msg = f"You just healed of *{int(heal)}HP* and inflicted *{int(damage)}* damage to *{self.currentBoss.name}* with *{player.first_skill_name}*"

        if affect:
            self.infight_msg += f"\n*{player.first_skill_name}* was 30% more effective on {self.currentBoss.name}. Thanks to elements"

        self.reload(False, call=call)

    def attack2(self, trn, call=None):
        if trn != self.crt_trn:
            return

        player = self.companion()

        damage, heal, affect = player.attack2(self.currentBoss, self.disadvtges, arena=True)

        alive = self.companion()
        if not alive:
            msg = f"You died. Try to upgrade your companions!"

            markup = module.Mkd()
            markup.add(
                module.Btn(
                	text="Back to Home",
                	  calldata=f"gohome|{self.crt_trn}|{self.player_info.id}")
            )
            bot.edit_message_text(msg,
            	chat_id=self.channel_info.id,
            	  message_id=self.arena_message.id,
            	  	reply_markup=markup)

            self.doneArena(False)
            return


        if heal == None:
            self.infight_msg = f"You inflicted *{int(damage)}* to {self.currentBoss.name} with *{player.second_skill_name}*"
        else:
            if heal < 0:
                self.infight_msg = f"You lose *{abs(heal)}HP* and inflicted *{int(damage)}* damage to {self.currentBoss.name} with *{player.second_skill_name}*"
            else:
                self.infight_msg = f"You just healed of *{heal}HP* and inflicted *{int(damage)}* damage to {self.currentBoss.name} with *{player.second_skill_name}*"

        if affect:
            self.infight_msg += f"\n*{player.second_skill_name}* was 30% more effective on {self.currentBoss.name}. Thanks to elements"

        self.reload(False, call=call)

    def reload(self, bossTurn=True, first=False, call=None):
        if bossTurn is False:
            if self.currentBoss.hp <= 0:
                stats = BossArena.query.filter_by(id = self.player_info.id).first()
                if not stats:
                    return #big problem

                #BossReward = [badgeCount for badgeCount in stats]
                #lvl = self.currentBoss.lvl
                #if BossReward[lvl] > 0:
                #	msg = f"You defeated {self.currentBoss.name}!!🎉 You won {self.currentBoss.reward_badge} badge and {self.currentBoss.reward_gold}💰 gold"
	            #else:
                #	msg = f"You defeated {self.currentBoss.name}!!🎉 You won another {self.currentBoss.reward_badge} badge"



                # Don't judge this shit, it was 3am -- but it's working lol (it's not, it doesn't check good. Look up. to implement)
                lvl = self.currentBoss.lvl
                if lvl == 1:
                    if stats.b1_reward < lvl:
                        msg = f"""*{self.currentBoss.name}* is dead. *Congratulations!!*🎉 \n\nYou won the *{self.currentBoss.reward_badge}* badge and {self.currentBoss.reward_gold}💰gold"""
                    else:
                        msg = f"""*{self.currentBoss.name}* is dead. *Congratulations!!*🎉 \n\nYou won another *{self.currentBoss.reward_badge}* badge"""


                elif lvl == 2:
                    if stats.b2_reward < lvl:
                        msg = f"""*{self.currentBoss.name}* is dead. *Congratulations!!*🎉 \n\nYou won the *{self.currentBoss.reward_badge}* badge and {self.currentBoss.reward_gold}💰gold"""

                    else:
                        msg = f"""*{self.currentBoss.name}* is dead. *Congratulations!!*🎉 \n\nYou won another *{self.currentBoss.reward_badge}* badge"""



                elif lvl == 3:
                    if stats.b3_reward < lvl:
                        msg = f"""*{self.currentBoss.name}* is dead. *Congratulations!!*🎉 \n\nYou won the *{self.currentBoss.reward_badge}* badge and {self.currentBoss.reward_gold}💰gold"""
                    else:
                        msg = f"""*{self.currentBoss.name}* is dead. *Congratulations!!*🎉 \n\nYou won another *{self.currentBoss.reward_badge}* badge"""


                elif lvl == 4:
                    if stats.b4_reward < lvl:
                        msg = f"""*{self.currentBoss.name}* is dead. *Congratulations!!*🎉 \n\nYou won the *{self.currentBoss.reward_badge}* badge and {self.currentBoss.reward_gold}💰gold"""
                    else:
                        msg = f"""*{self.currentBoss.name}* is dead. *Congratulations!!*🎉 \n\nYou won another *{self.currentBoss.reward_badge}* badge"""


                elif lvl == 5:
                    if stats.b5_reward < lvl:
                        msg = f"""*{self.currentBoss.name}* is dead. *Congratulations!!*🎉 \n\nYou won the *{self.currentBoss.reward_badge}* badge and {self.currentBoss.reward_gold}💰gold"""
                    else:
                        msg = f"""*{self.currentBoss.name}* is dead. *Congratulations!!*🎉 \n\nYou won another *{self.currentBoss.reward_badge}* badge"""

                msg += "\n\nLook your stats with /arenastats command!"
                markup = module.Mkd()
                markup.add(
                    module.Btn(
                    	text="Back to Home",
                    	  calldata=f"gohome|{self.crt_trn}|{self.player_info.id}")
                )
                bot.edit_message_text(msg,
                	chat_id=self.channel_info.id,
                	  message_id=self.arena_message.id,
                	    reply_markup=markup)

                self.doneArena(True, self.currentBoss.lvl)
                return

            player = self.companion()

            if not player:
                msg = f"""You died. Try to upgrade your companions!"""

                markup = module.Mkd()
                markup.add(
                    module.Btn(
                    	text="Back to Home",
                    	  calldata=f"gohome|{self.crt_trn}|{self.player_info.id}")
                )
                bot.edit_message_text(msg,
                	chat_id=self.channel_info.id,
                	  message_id=self.arena_message.id,
                	    reply_markup=markup)
                self.doneArena(False)
                return


            msg = self.getMsg(self.player_companions)

            markup = module.Mkd()
            markup.add(
                module.Btn(
                	text=player.first_skill_name,
                	  calldata=f"arenattack1|{self.crt_trn}|{self.player_info.id}"),
                module.Btn(
                	text=player.second_skill_name,
                	  calldata=f"arenattack2|{self.crt_trn}|{self.player_info.id}"),
                module.Btn(
                	text="Cancel",
                	  calldata=f"cancelboss|{self.crt_trn}|{self.player_info.id}")
            )

            bot.edit_message_text(msg,
            	chat_id=self.channel_info.id,
            	  message_id=self.arena_message.id,
            	    reply_markup=markup)

            #Timer
            self.state += 1
            TimerArena.execute(self, self.state, call=call)

            #Comment next line to make the boss never attack
            self.reload(first=not self.first)

        else:

            if first is True:

                self.first = True
                return

            time.sleep(2) #Too lazy to make some threading shit

            try:
                damage, heal, skill_name, adv, disadv = self.currentBoss.attack(self, self.companion())
            except Exception as e:
                print(e)

            self.advtges = adv
            self.disadvtges = disadv

            player = self.companion()

            if heal is None:
                if self.advtges != 0:
                    self.infight_msg = f"""⚖️ Your attack has been reduced by *{self.disadvtges}%* this round\nBoss attack has been increased by *{self.advtges}%* next round due to {self.currentBoss.name}' *{skill_name}*"""

                damage = damage + ((damage * self.advtges) // 100)
                player.hp -= damage

                self.infight_msg = f"""🗡{self.currentBoss.name} inflicted you *{abs(damage)}* damage with *{skill_name}*"""
                self.advtges = 0

            else:
                if damage is None:
                    self.currentBoss.hp += heal
                    if self.currentBoss.hp > self.currentBoss.nowHp:
                        self.currentBoss.hp = self.currentBoss.nowHp

                    self.infight_msg = f"""❤️{self.currentBoss.name} just healed of *{abs(heal)}HP* with *{skill_name}*"""
                else:
                    player.hp -= damage + (damage * self.advtges) // 100
                    self.currentBoss.hp += heal
                    self.infight_msg = f"""❤️🗡{self.currentBoss.name} just healed of *{abs(heal)}HP* and damaged you of *{damage}*HP with *{skill_name}*"""

                    self.advtges = 0

            player = self.companion()

            if not player:
                msg = f"""You died. Try to upgrade your companions!"""

                markup = module.Mkd()
                markup.add(
                    module.Btn(
                    	text="Back to Home",
                    	  calldata=f"gohome|{self.crt_trn}|{self.player_info.id}")
                )
                bot.edit_message_text(msg, chat_id=self.channel_info.id, message_id=self.arena_message.id, reply_markup=markup)
                self.doneArena(False)
                return

            msg = self.getMsg(self.player_companions)

            markup = module.Mkd()
            markup.add(
                module.Btn(
                	text=player.first_skill_name,
                	  calldata=f"arenattack1|{self.crt_trn}|{self.player_info.id}"),
                module.Btn(
                	text=player.second_skill_name,
                	  calldata=f"arenattack2|{self.crt_trn}|{self.player_info.id}"),
                module.Btn(
                	text="Cancel",
                	  calldata=f"cancelboss|{self.crt_trn}|{self.player_info.id}")
            )

            bot.edit_message_text(msg, chat_id=self.channel_info.id, message_id=self.arena_message.id, reply_markup=markup)


    def timeout(self):
        msg = """You were AFK for too long, the Arena Gate closed. ⛓\n\n🗝 No stats were affected"""

        #reset
        try:
            del BOSS_ARENA[self.player_info.id]
        except:
            pass
        try:
            del IN_ARENA[self.player_info.id]
        except:
            pass

        self.currentBoss.hp = self.currentBoss.nowHp

        self.player_companions = []
        self._player_companions = []
        self.first = False
        try:
            bot.edit_message_text(msg,
            	chat_id=self.channel_info.id,
            	  message_id=self.arena_message.id)
        except:
            bot.reply_to(self.command_arena, msg)

        #bot.delete_message(self.channel_info.id, self.msg_id)
        #bot.delete_message(self.channel_info.id, self.command_arena.id)



    def start(self, boss):
        #First, check if player has enough gold
        try:
            data = UserData.query.filter_by(id=self.player_info.id).first()
        except:
            msg = "Cannot fetch data to check that you have enough gold.. Cancelling"
            temp = bot.reply_to(self.command_arena, msg)
            bot.delete_message(self.channel_info.id, self.arena_message.id)

            self.arena_message = temp
            self.channel_info = temp.chat

            #reset
            del BOSS_ARENA[who]
            del IN_ARENA[who]

            return

        cost = self.currentBoss.cost
        if int(data.gold) >= int(cost): #Player has enough
            #So, we remove gold
            UserData.query.filter_by(id=self.player_info.id).update({UserData.gold: UserData.gold - int(cost)})
            db.session.commit()
        else:
            markup = module.Mkd()
            markup.add(
                module.Btn(
                	text="Return to Arena menu",
                	  calldata=f"gohome|{self.crt_trn}|{self.player_info.id}"),
            )
            msg = "You don't have enough gold to fight this boss.."
            temp = bot.reply_to(self.command_arena, msg, reply_markup=markup)
            bot.delete_message(self.channel_info.id, self.arena_message.id)

            self.arena_message = temp
            self.channel_info = temp.chat

            #bot.edit_message_text(msg, chat_id=self.channel_info.id, message_id=self.arena_message.id, reply_markup=markup)
            return


        msg = f"""About to fight **{self.currentBoss.name}** who have a power of {self.currentBoss.damage} and like {self.currentBoss.hp}HP"""
        temp = bot.reply_to(self.command_arena, msg)
        bot.delete_message(self.channel_info.id, self.arena_message.id)

        self.arena_message = temp
        self.channel_info = temp.chat

        self.reload(call=None, bossTurn=False)

    def sure(self, boss):
        self.currentBoss = BOSS[int(boss)]

        if int(self.level)+1 < int(self.currentBoss.lvl):
            msg = f"""You can't fight **{self.currentBoss.name}**, you first need to beat previous boss"""
            markup = module.Mkd()
            markup.add(
                module.Btn(
                	text="Go back",
                	  calldata=f"gohome|{self.crt_trn}|{self.player_info.id}"),
            )
        else:
            msg = f"🗝 You are about to enter floor {self.currentBoss.lvl} to fight {self.currentBoss.name}\n\n⚠️ Are you sure?"
            markup = module.Mkd()
            markup.add(
                module.Btn(
                	text=f"""Enter (Cost is {self.currentBoss.cost}💰)""",
                	  calldata=f"enter{boss}|{self.crt_trn}|{self.player_info.id}"),
                module.Btn(
                	text="Cancel",
                	  calldata=f"gohome|{self.crt_trn}|{self.player_info.id}"),
            )

        #bot.edit_message_text(msg, chat_id=self.channel_info.id, message_id=self.arena_message.id, reply_markup=markup)
        #No method to edit a message by adding a media
        temp = bot.send_photo(self.channel_info.id, open("mysite/"+self.currentBoss.img, "rb"), caption=msg, reply_to_message_id=self.command_arena.id, reply_markup=markup)
        bot.delete_message(self.channel_info.id, self.arena_message.id)
        self.channel_info = temp.chat
        self.arena_message = temp

    def cancel(self, who):
        msg = "You left the Arena, and the Arena Gate was closed. ⛓\n\n🗝 Come back next time"

        #reset
        del BOSS_ARENA[who]
        del IN_ARENA[who]

        try:
            self.currentBoss.hp = self.currentBoss.nowHp
        except:
            pass

        self.player_companions = []
        self._player_companions = []
        self.first = False

        bot.edit_message_text(msg,
        	chat_id=self.channel_info.id,
        	  message_id=self.arena_message.id)

        #bot.delete_message(self.channel_info.id, self.msg_id)
        #bot.delete_message(self.channel_info.id, self.command_arena.id)

    def doneArena(self, won, boss=0):
        if won is True:
            #add stats
            stats = BossArena.query.filter_by(id=self.player_info.id).first()

            if not stats:
                return #We have a serious problem, cuz you can't fight launch arena without stats

            if stats.level < boss:
                if boss == 1:
                    BossArena.query.filter_by(id = self.player_info.id).update({BossArena.b1_reward: BossArena.b1_reward + 1, BossArena.win: BossArena.win + 1, BossArena.level: BossArena.level + 1})
                    db.session.commit()
                    UserData.query.filter_by(id = self.player_info.id).update({UserData.gold: UserData.gold + self.currentBoss.reward_gold})
                    db.session.commit()

                elif boss == 2:
                    BossArena.query.filter_by(id = self.player_info.id).update({BossArena.b2_reward: BossArena.b2_reward + 1, BossArena.win: BossArena.win + 1, BossArena.level: BossArena.level + 1})
                    db.session.commit()
                    UserData.query.filter_by(id = self.player_info.id).update({UserData.gold: UserData.gold + self.currentBoss.reward_gold})
                    db.session.commit()
                elif boss == 3:
                    BossArena.query.filter_by(id = self.player_info.id).update({BossArena.b3_reward: BossArena.b3_reward + 1, BossArena.win: BossArena.win + 1, BossArena.level: BossArena.level + 1})
                    db.session.commit()
                    UserData.query.filter_by(id = self.player_info.id).update({UserData.gold: UserData.gold + self.currentBoss.reward_gold})
                    db.session.commit()
                elif boss == 4:
                    BossArena.query.filter_by(id = self.player_info.id).update({BossArena.b4_reward: BossArena.b4_reward + 1, BossArena.win: BossArena.win + 1, BossArena.level: BossArena.level + 1})
                    db.session.commit()
                    UserData.query.filter_by(id = self.player_info.id).update({UserData.gold: UserData.gold + self.currentBoss.reward_gold})
                    db.session.commit()
                elif boss == 5:
                    BossArena.query.filter_by(id = self.player_info.id).update({BossArena.b5_reward: BossArena.b5_reward + 1, BossArena.win: BossArena.win + 1, BossArena.level: BossArena.level + 1})
                    db.session.commit()
                    UserData.query.filter_by(id = self.player_info.id).update({UserData.gold: UserData.gold + self.currentBoss.reward_gold})
                    db.session.commit()

            else:
                if boss == 1:
                    BossArena.query.filter_by(id = self.player_info.id).update({BossArena.b1_reward: BossArena.b1_reward + 1, BossArena.win: BossArena.win + 1})
                    db.session.commit()
                elif boss == 2:
                    BossArena.query.filter_by(id = self.player_info.id).update({BossArena.b2_reward: BossArena.b2_reward + 1, BossArena.win: BossArena.win + 1})
                    db.session.commit()
                elif boss == 3:
                    BossArena.query.filter_by(id = self.player_info.id).update({BossArena.b3_reward: BossArena.b3_reward + 1, BossArena.win: BossArena.win + 1})
                    db.session.commit()
                elif boss == 4:
                    BossArena.query.filter_by(id = self.player_info.id).update({BossArena.b4_reward: BossArena.b4_reward + 1, BossArena.win: BossArena.win + 1})
                    db.session.commit()
                elif boss == 5:
                    BossArena.query.filter_by(id = self.player_info.id).update({BossArena.b5_reward: BossArena.b5_reward + 1, BossArena.win: BossArena.win + 1})
                    db.session.commit()
        else:
            BossArena.query.filter_by(id = self.player_info.id).update({BossArena.defeat: BossArena.defeat + 1})
            db.session.commit()

        #reset
        self.currentBoss.hp = self.currentBoss.nowHp

        self.player_companions = []
        self._player_companions = []
        self.infight_msg = "Battle begins!"

        self.update()
        self.position()
        self.first = False


    def home(self):
        self.update()
        self.player_companions = []
        self._player_companions = []
        self.position()

        msg = self.home_msg
        markup = self.markup

        temp = bot.reply_to(self.command_arena, msg, reply_markup=markup)
        bot.delete_message(self.channel_info.id, self.arena_message.id)
        self.arena_message = temp
        self.channel_info = temp.chat
        #bot.edit_message_text(msg, chat_id=self.channel_info.id, message_id=self.arena_message.id, reply_markup=markup)

