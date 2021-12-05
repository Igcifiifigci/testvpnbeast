""" elements.py """

class Character:
    name = "Unnamed"
    first_skill_name = "Unnamed"
    second_skill_name = "Unnamed"
    level = 1
    attack = 1
    hp = 1
    speed = 1
    gpm = 1
    maxGold = 1
    hpIncrement = 1
    attackIncrement = 1
    speedIncrement = 1

    def __init__(self, level, companion_id = None):
        if companion_id:
            self.companion_id = companion_id

        self.name2 = self.name.encode("ascii", "ignore").decode().strip()
        self.level = level
        self.hp += round(self.hpIncrement * (level - 1))
        self.totalHp = self.hp
        self.attack += round(self.attackIncrement * (level - 1))
        self.speed += round(self.speedIncrement * (level - 1))

        for _ in range(1, self.level, 10):
            self.gpm += self.gpm / 3
            self.maxGold += self.maxGold // 3

        if round(self.gpm) != 0:
            self.gpm = round(self.gpm)
        else:
            self.gpm = float("%.1f" % self.gpm)


    def stun(self, characterObject):
        characterObject.stunned()


    def stunned(self):
        pass


    def isDead(self):
        if self.hp <= 0:
            return True

        return False


class EarthElement(Character):
    element = "Earth ⛰"
    emote = "⛰"

class WaterElement(Character):
    element = "Water 🌊"
    emote = "🌊"

class DarkElement(Character):
    element = "Dark ⚫️"
    emote = "⚫️"

class FireElement(Character):
    element = "Fire 🔥"
    emote = "🔥"

class LightElement(Character):
    element = "Light ⚪"
    emote = "⚪"

elements = [
    EarthElement,
    WaterElement,
    DarkElement,
    FireElement,
    LightElement
]
