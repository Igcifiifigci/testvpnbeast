""" boss.py """

import random
from database import BossArena
from elements import *


#hp is the ingame hp, nowHp is the fix boss HP
#Skill damage percentage are % of the damage value
class LevelOne(EarthElement):
    lvl = 1
    name = "Basilisk"
    img = "images/Basilisk.jpg"
    element = "Earth"
    cost = 500

    reward_gold = 100000
    reward_badge = "Basilisk slaughterer"

    hp = 3000
    nowHp = 3000
    damage = 300

    skill_one = {"name": "Earthquake", "damage": "50% or 180%", "trigger": 80}
    skill_two = {"name": "Silent Scream", "damage": "50% Increase next round for Boss, 50% decreased next round for player", "trigger": 20}

    def attack(self, characterObject):
        x = random.randint(1, 100)
        if x > self.currentBoss.skill_two['trigger']:
            attack = (self.currentBoss.damage * random.choice([50, 180])) // 100
            heal = None

            advtages = 0
            disadvtges = 0

            skill_name = self.currentBoss.skill_one['name']

        elif x < self.currentBoss.skill_two['trigger']+1:

            attack = None
            heal = None

            advtages = 50
            disadvtges = 50

            skill_name = self.currentBoss.skill_two['name']
        print(attack, heal, skill_name, advtages, disadvtges)

        return attack, heal, skill_name, advtages, disadvtges


class LevelTwo(FireElement):
    lvl = 2
    name = "Chimera"
    element = "Fire"
    img = "images/Chiera.jpg"
    cost = 2500

    reward_gold = 250000
    reward_badge = "Chimera killer"

    hp = 5350
    nowHp = 5350
    damage = 600

    skill_one = {"name": "Deadly Claws", "damage": "90% or 110%", "trigger": 75}
    skill_two = {"name": "Supreme Roar", "damage": "Heal the Boss from 800HP" , "trigger": 25}


    def attack(self, characterObject):
        x = random.randint(1, 100)
        if x > self.currentBoss.skill_two['trigger']:
            attack = (self.currentBoss.damage * random.choice([90, 110])) // 100
            heal = None

            advtages = 0
            disadvtges = 0

            skill_name = self.currentBoss.skill_one['name']

        elif x < self.currentBoss.skill_two['trigger']+1:
            attack = None
            heal = 600

            advtages = 0
            disadvtges = 0

            skill_name = self.currentBoss.skill_two['name']

        return attack, heal, skill_name, advtages, disadvtges


class LevelThree(DarkElement):
    lvl = 3
    name = "Ravana"
    element = "Dark"
    img = "images/Ravana.jpg"
    cost = 5000

    reward_gold = 100000 #One time only
    reward_badge = "Divine arrow"

    hp = 14000
    nowHp = 14000
    damage = 380

    skill_one = {"name": "Shadow Chain", "damage": "80% or 140%", "trigger": 80}
    skill_two = {"name": "Mystic Fist", "damage": "200% damage" , "trigger": 20}


    def attack(self, characterObject):
        x = random.randint(1, 100)
        if x > self.currentBoss.skill_two['trigger']:
            attack = (self.currentBoss.damage * random.choice([80, 140])) // 100
            heal = None

            advtages = 0
            disadvtges = 0

            skill_name = self.currentBoss.skill_one['name']

        elif x < self.currentBoss.skill_two['trigger']+1:
            attack = (self.currentBoss.damage * 200) // 100
            heal = None

            advtages = 0
            disadvtges = 0

            skill_name = self.currentBoss.skill_two['name']

        return attack, heal, skill_name, advtages, disadvtges


class LevelFour(LightElement):
    lvl = 4
    name = "Anubis"
    element = "Light"
    img = "images/Anubis.jpg"
    cost = 10000

    reward_gold = 1000000 #One time only
    reward_badge = "Anubis Assassinator"

    hp = 10800
    nowHp = 10800
    damage = 950

    skill_one = {"name": "Judgement", "damage": "75% or 175%", "trigger": 60}
    skill_two = {"name": "Devine Punishment", "damage": "300% damage or 0% (50/50)" , "trigger": 30}
    skill_three = {"name": "All Hail", "damage": "Between 50% and 100% and heal the Boss of that amount" , "trigger": 10}


    def attack(self, characterObject):
        x = random.randint(1, 100)
        if x <= self.currentBoss.skill_two['trigger']:
            attack = (self.currentBoss.damage * random.choice([50, 100])) // 100
            heal = attack

            advtages = 0
            disadvtges = 0

            skill_name = self.currentBoss.skill_three['name']

        elif x <= self.currentBoss.skill_two['trigger'] + self.currentBoss.skill_three['trigger']:
            attack = (self.currentBoss.damage * random.choice([0, 300])) // 100
            heal = None

            advtages = 0
            disadvtges = 0

            skill_name = self.currentBoss.skill_two['name']
        else:
            attack = (self.currentBoss.damage * random.choice([75, 175])) // 100
            heal = None

            advtages = 0
            disadvtges = 0

            skill_name = self.currentBoss.skill_one['name']

        return attack, heal, skill_name, advtages, disadvtges


class LevelFive(FireElement):
    lvl = 5
    name = "Demon King"
    element = "Fire"
    img = "images/Demon_King.jpg"
    cost = 0

    reward_gold = 2000000 #One time only
    reward_badge = "Demon King executer"

    hp = 16700
    nowHp = 16700
    damage = 1200

    skill_one = {"name": "Oblivion", "damage": "75% or 200%", "trigger": 70}
    skill_two = {"name": "Death's call", "damage": "300% damage" , "trigger": 20}
    skill_three = {"name": "Blackout", "damage": "+75% damage for Boss next round, -50% damage for player" , "trigger": 10}


    def attack(self, characterObject):
        x = random.randint(1, 100)
        if x <= self.currentBoss.skill_three['trigger']:
            attack = None
            heal = None

            advtages = 75
            disadvtges = 50

            skill_name = self.currentBoss.skill_one['name']

        elif x < self.currentBoss.skill_two['trigger'] + self.currentBoss.skill_three['trigger']:
            attack = (self.currentBoss.damage * 300) // 100
            heal = None

            advtages = 0
            disadvtges = 0

            skill_name = self.currentBoss.skill_two['name']

        else:
            attack = (self.currentBoss.damage * random.choice([75, 200])) // 100
            heal = None

            advtages = 0
            disadvtges = 0

            skill_name = self.currentBoss.skill_three['name']

        return attack, heal, skill_name, advtages, disadvtges


bossList = [
    LevelOne,
    LevelTwo,
    LevelThree,
    LevelFour,
    LevelFive
]
