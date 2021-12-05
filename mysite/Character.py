""" character.py """

from elements import *
import random

class Orc(EarthElement):
    name = "🐷 Orc"
    name_ne = "Orc"
    id = 1
    element = "EarthElement"
    elem = EarthElement
    first_skill_name = "Power Stomp"
    second_skill_name = "Ultimate Punch"
    first_skill_info = r"Damage 50% or 150%"
    second_skill_info = r"Damage 50%-100% (chance of critical 1.7× damage)"
    imagePath = "mysite/images/Orc.jpg"
    attack = 134
    speed = 38
    totalHp = 637
    hp = 637
    gpm = 1.5
    maxGold = 1500
    attackIncrement = 9.3
    speedIncrement = 0.8
    hpIncrement = 41

    disadvtges = 0
    advtges = 0

    def attack1(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.choice([50, 150])) // 100
        affect = False

        #Elements interaction
        #Orc is earth, so have 30% more on water
        if characterObject.element == "WaterElement":
            damage += int((damage*30)/100)
            affect = True


        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


    def attack2(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(50, 100)) // 100
        affect = False

        if random.randint(0, 1):
            damage *= 1.7
        damage = round(damage)

        #Elements interaction
        #Orc is earth, so have 30% more on water
        if characterObject.element == "WaterElement":
            damage += int((damage*30)/100)
            affect = True


        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


class Dryad(EarthElement):
    name = "🌳Dryad"
    name_ne = "Dryad"
    id = 2
    element = "EarthElement"
    elem = EarthElement
    first_skill_name = "Nature Call"
    second_skill_name = "Full Blossom"
    first_skill_info = r"Damage 70%-135%"
    second_skill_info = r"Damage 150% or miss (40% chance of miss)"
    imagePath = "mysite/images/Dyrad.jpg"
    attack = 81
    speed = 40
    totalHp = 782
    hp = 782
    gpm = 0.2
    maxGold = 2000
    attackIncrement = 7.3
    speedIncrement = 0.9
    hpIncrement = 51

    def attack1(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(70, 135)) // 100
        affect = False

        #Elements interaction
        #Dryad is earth, so have 30% more on water
        if characterObject.element == "WaterElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


    def attack2(self, characterObject, disadvtges=0, arena=False):
        damage = self.attack * 150 // 100
        affect = False

        if random.randint(1, 10) in [1, 2, 3, 4]:
            damage = 0

        #Elements interaction
        #Dryad is earth, so have 30% more on water
        if characterObject.element == "WaterElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


class Garuda(LightElement):
    name = "🦅 Garuda"
    name_ne = "Garuda"
    id = 3
    element = "LightElement"
    elem = LightElement
    first_skill_name = "God's Wing"
    second_skill_name = "Life drop"
    first_skill_info = r"Damage 80%-120%"
    second_skill_info = r"Damage 30%-60% (heal the amount = damage dealt)"
    imagePath = "mysite/images/Garuda.jpg"
    attack = 123
    speed = 50
    totalHp = 600
    hp = 600
    gpm = 0.5
    maxGold = 800
    attackIncrement = 8.8
    speedIncrement = 1.1
    hpIncrement = 41

    disadvtges = 0
    advtges = 0

    def attack1(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(80, 120)) // 100
        affect = False

        #Elements interaction
        #Garuda is holy, so have 30% more on dark
        if characterObject.element == "DarkElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


    def attack2(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(30, 60)) // 100
        affect = False

        #Elements interaction
        #Garuda is holy, so have 30% more on dark
        if characterObject.element == "DarkElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        self.hp += damage
        if self.hp > self.totalHp:
            self.hp = self.totalHp
            hp = self.totalHp

        heal = damage
        return damage, heal, affect


class Angel(LightElement):
    name = "😇 Angel"
    name_ne = "Angel"
    id = 4
    element = "LightElement"
    elem = LightElement
    first_skill_name = "Beam Aura"
    second_skill_name = "Supreme Light"
    first_skill_info = r"Damage 100%"
    second_skill_info = r"Damage 80%-120% (50% chance of critical 1.3×, 25% chance of critical 1.6×)"
    imagePath = "mysite/images/Angel.jpg"
    attack = 100
    speed = 60
    totalHp = 590
    hp = 590
    gpm = 2
    maxGold = 1000
    attackIncrement = 8.5
    speedIncrement = 1.4
    hpIncrement = 40

    disadvtges = 0
    advtges = 0

    def attack1(self, characterObject, disadvtges=0, arena=False):
        damage = self.attack
        affect = False

        #Elements interaction
        #Angel is holy, so have 30% more on dark
        if characterObject.element == "DarkElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


    def attack2(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(70, 120)) // 100
        affect = False

        rand = random.randint(1, 100)
        if rand in range(1, 26):
            damage *= 1.6
        elif rand in range(26, 76):
            damage *= 1.3

        damage = round(damage)

        #Elements interaction
        #Angel is holy, so have 30% more on dark
        if characterObject.element == "DarkElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


class Kraken(WaterElement):
    name = "🐙 Kraken"
    name_ne = "Kraken"
    id = 5
    element = "WaterElement"
    elem = WaterElement
    first_skill_name = "Slash"
    second_skill_name = "GiGa Waves"
    first_skill_info = r"Damage 95%-105%"
    second_skill_info = r"Damage 200% or miss (50% chance of miss)"
    imagePath = "mysite/images/Kraken.jpg"
    attack = 95
    speed = 39
    totalHp = 695
    hp = 695
    gpm = 1.2
    maxGold = 1000
    attackIncrement = 9
    speedIncrement = 1
    hpIncrement = 42

    disadvtges = 0
    advtges = 0

    def attack1(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(95, 105)) // 100
        affect = False

        #Elements interaction
        #Kraken is water, so have 30% more on fire
        if characterObject.element == "FireElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


    def attack2(self, characterObject, disadvtges=0, arena=False):
        damage = self.attack * 200 // 100
        affect = False

        if random.randint(0,1):
            damage = 0

        #Elements interaction
        #Kraken is water, so have 30% more on fire
        if characterObject.element == "FireElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


class Serpent(WaterElement):
    name = "🐍 Serpent"
    name_ne = "Serpent"
    id = 6
    element = "WaterElement"
    elem = WaterElement
    first_skill_name = "Water Spurt"
    second_skill_name = "Tsunami"
    first_skill_info = r"Damage 80%-120%"
    second_skill_info = r"Damage 65%-90% (heal self HP 5%)"
    imagePath = "mysite/images/Serpent.jpg"
    attack = 112
    speed = 58
    totalHp = 612
    hp = 612
    gpm = 0.6
    maxGold = 600
    attackIncrement = 8.7
    speedIncrement = 1.7
    hpIncrement = 41

    disadvtges = 0
    advtges = 0
    def attack1(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(80, 120)) // 100
        affect = False

        #Elements interaction
        #Serpent is waterholy, so have 30% more on fire
        if characterObject.element == "FireElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


    def attack2(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(65, 90)) // 100
        affect = False

        #Elements interaction
        #Serpent is waterholy, so have 30% more on fire
        if characterObject.element == "FireElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        self.hp += self.totalHp * 5 // 100
        if self.hp > self.totalHp:
            self.hp = self.totalHp
            hp = self.totalHp
        heal = self.totalHp * 5 // 100
        return damage, heal, affect


class Ghoul(DarkElement):
    name = "😈 Ghoul"
    name_ne = "Ghoul"
    id = 7
    element = "DarkElement"
    elem = DarkElement
    first_skill_name = "Ghoul Claws"
    second_skill_name = "Rampage"
    first_skill_info = r"Damage 80%-100%"
    second_skill_info = r"Damage 130%-200% (self current HP reduce 20%)"
    imagePath = "mysite/images/Ghoul.jpg"
    attack = 108
    speed = 44
    totalHp = 610
    hp = 610
    gpm = 0.8
    maxGold = 800
    attackIncrement = 8.6
    speedIncrement = 1
    hpIncrement = 40.8

    disadvtges = 0
    advtges = 0

    def attack1(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(80, 100)) // 100
        affect = False

        #Elements interaction
        #Ghoul is dark, so have 30% more on holy
        if characterObject.element == "LightElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


    def attack2(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(130, 200)) // 100
        affect = False

        #Elements interaction
        #Ghoul is dark, so have 30% more on holy
        if characterObject.element == "LightElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        self.hp -= self.hp * 20 // 100

        heal = -(self.hp * 20 // 100)
        return damage, heal, affect


class Cerberus(DarkElement):
    name = "🦁 Cerberus"
    name_ne = "Cerberus"
    id = 8
    element = "DarkElement"
    elem = DarkElement
    first_skill_name = "Dark Hound"
    second_skill_name = "Gate of Hell"
    first_skill_info = r"Damage 90%-115%"
    second_skill_info = r"Damage 50%-160%"
    imagePath = "mysite/images/Cerberus.jpg"
    attack = 132
    speed = 45
    totalHp = 435
    hp = 435
    gpm = 0.1
    maxGold = 500
    attackIncrement = 10
    speedIncrement = 1.1
    hpIncrement = 35

    disadvtges = 0
    advtges = 0

    def attack1(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(90, 115)) // 100
        affect = False

        #Elements interaction
        #Cerberus is dark, so have 30% more on holy
        if characterObject.element == "LightElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


    def attack2(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(50, 160)) // 100
        affect = False

        #Elements interaction
        #Cerberus is dark, so have 30% more on holy
        if characterObject.element == "LightElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


class Phoenix(FireElement):
    name = "🦜 Phoenix"
    name_ne = "Phoenix"
    id = 9
    element = "FireElement"
    elem = FireElement
    first_skill_name = "Fire Dance"
    second_skill_name = "Life Fire"
    first_skill_info = r"Damage 85%-115%"
    second_skill_info = r"Damage 40%-160%"
    imagePath = "mysite/images/Phoenix.jpg"
    attack = 118
    speed = 68
    totalHp = 598
    hp = 598
    gpm = 0.4
    maxGold = 2000
    attackIncrement = 9
    speedIncrement = 1.1
    hpIncrement = 40.5

    disadvtges = 0
    advtges = 0

    def attack1(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(85, 115)) // 100
        affect = False

        #Elements interaction
        #Phoenix is fire, so have 30% more on earth
        if characterObject.element == "EarthElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


    def attack2(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(40, 160)) // 100
        affect = False

        #Elements interaction
        #Phoenix is fire, so have 30% more on earth
        if characterObject.element == "EarthElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


class Dragon(FireElement):
    name = "🐲 Dragon"
    name_ne = "Dragon"
    id = 10
    element = "FireElement"
    elem = FireElement
    first_skill_name = "Fire Blast"
    second_skill_name = "Eternal Flame"
    first_skill_info = r"Damage 80%-120%"
    second_skill_info = r"Damage 70-90% (50% chance to critical hit which cause 1.5× damage)"
    imagePath = "mysite/images/Dragon.jpg"
    attack = 120
    speed = 43
    totalHp = 645
    hp = 645
    gpm = 1
    maxGold = 500
    attackIncrement = 9
    speedIncrement = 1
    hpIncrement = 42

    disadvtges = 0
    advtges = 0

    def attack1(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(80, 120)) // 100
        affect = False

        #Elements interaction
        #Dragon is fire, so have 30% more on earth
        if characterObject.element == "EarthElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect


    def attack2(self, characterObject, disadvtges=0, arena=False):
        damage = (self.attack * random.randint(70, 90)) // 100
        affect = False

        if random.randint(0, 1):
            damage *= 1.5
        damage = round(damage)

        #Elements interaction
        #Dragon is fire, so have 30% more on earth
        if characterObject.element == "EarthElement":
            damage += int((damage*30)/100)
            affect = True

        if arena is True:
            damage -= (damage *disadvtges) / 100

        characterObject.hp -= damage
        heal = None
        return damage, heal, affect

characters = [
    Orc,
    Dryad,
    Garuda,
    Angel,
    Kraken,
    Serpent,
    Ghoul,
    Cerberus,
    Phoenix,
    Dragon,
]
