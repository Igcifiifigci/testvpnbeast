""" abilities.py """

import elements as e


class FrozeArtifact():
    name = "Frost Artifact"
    emote = "❄️"
    number = 0
    price = 30000
    useBy = [e.FireElement.emote, e.WaterElement.emote, e.EarthElement.emote, e.LightElement.emote, e.DarkElement.emote]

    s = ["Freeze other for one round", "Self-damage increase by 20%"]
    skills = "Freeze opponent for one round and increase self-damage by 20%"

    def use(self):

        if self.player1_turn:
            p = "p1"
            notp = "p2"
            player = self.p1Companion(get=True)

            if self.isImmune[notp]["state"] is True:
                msg = "You tried to froze your opponent, but he was immunized.."
                self.leftUse[p] -= 1
                self.inUse[p].append(FrozeArtifact().emote)
                self.used[p].append(FrozeArtifact().emote)
                return msg

            self.isFreeze["p1"] = True
            if self.p1damage_sentA1["until"] != 0:
                self.p1damage_sentA2["damage"] = 20
                self.p1damage_sentA2["until"] = -1
            else:
                self.p1damage_sentA1["damage"] = 20
                self.p1damage_sentA1["until"] = -1


        else:
            p = "p2"
            notp = "p1"
            player = self.p2Companion(get=True)

            if self.isImmune[notp]["state"] is True:
                msg = "You tried to froze your opponent, but he was immunized.."
                self.leftUse[p] -= 1
                self.inUse[p].append(FrozeArtifact().emote)
                self.used[p].append(FrozeArtifact().emote)
                return msg

            self.isFreeze["p2"] = True
            if self.p2damage_sentA1["until"] != 0:
                self.p2damage_sentA2["damage"] = 20
                self.p2damage_sentA2["until"] = -1
            else:
                self.p2damage_sentA1["damage"] = 20
                self.p2damage_sentA1["until"] = -1

        msg = "You just frost your opponent! You also increased your next attack by 20%"

        self.leftUse[p] -= 1
        self.inUse[p].append(FrozeArtifact().emote)
        self.used[p].append(FrozeArtifact().emote)
        self.FrozeArtifact[p] = 1
        self.inUse[notp].append(FrozeArtifact().emote)
        self.FrozeArtifact[notp] = 1
        return msg

class HealingRing():
    name = "Healing Ring"
    emote = "💛"
    number = 1
    price = 30000
    useBy = [e.FireElement.emote, e.WaterElement.emote, e.EarthElement.emote, e.LightElement.emote, e.DarkElement.emote]

    s = ["Heal 15% HP"]
    skills = "Heal you by 15% HP"

    def use(self):
        if self.player1_turn:
            p = "p1"
            player = self.p1Companion(get=True)
        else:
            p = "p2"
            player = self.p2Companion(get=True)

        HP = int(((player.totalHp)*15)/100)

        if HP+player.hp > player.totalHp:
            player.hp = player.totalHp
        else:
            player.hp += HP



        msg = f"You just healed of {((player.hp)*15)/100}HP"
        self.leftUse[p] -= 1
        self.inUse[p].append(HealingRing().emote)
        self.used[p].append(HealingRing().emote)
        self.HealingRing[p] = 1
        return msg

class HealingRingII():
    name = "Healing Ring II"
    emote = "💛"
    number = 2
    price = 30000
    useBy = [e.FireElement.emote, e.WaterElement.emote, e.EarthElement.emote, e.LightElement.emote, e.DarkElement.emote]

    s = ["Heal 25% HP"]
    skills = "Heal you by 25% HP"

    def use(self):
        if self.player1_turn:
            p = "p1"
            player = self.p1Companion(get=True)
        else:
            p = "p2"
            player = self.p2Companion(get=True)

        HP = int(((player.totalHp)*25)/100)

        if HP+player.hp > player.totalHp:
            player.hp = player.totalHp
        else:
            player.hp += HP

        msg = f"You just healed of {((player.hp)*25)/100}HP"
        self.leftUse[p] -= 1
        self.inUse[p].append(HealingRingII().emote)
        self.used[p].append(HealingRingII().emote)
        self.HealingRingII[p] = 1
        return msg

class ShardedBone():
    name = "Sharded Bone"
    emote = "💀"
    number = 3
    price = 30000
    useBy = [e.FireElement.emote, e.WaterElement.emote, e.EarthElement.emote, e.LightElement.emote, e.DarkElement.emote]

    s = ["Opponent next attack decreased by 25%", "Self-attack for this round increased by 25%"]
    skills = "Your opponent next attack will be decreased by 25% and your next attack increased by 25%"

    def use(self):
        if self.player1_turn:
            p = "p1"
            player = self.p1Companion(get=True)

            if self.p1damage_sentA1["until"] != 0:
                self.p1damage_sentA2["damage"] = 25
                self.p1damage_sentA2["until"] = 1
                #
                self.p1damage_receivedA2["until"] = 1
                self.p1damage_receivedA2["damage"] = 25
            else:
                self.p1damage_sentA1["damage"] = 25
                self.p1damage_sentA1["until"] = 1
                #
                self.p1damage_receivedA1["until"] = 1
                self.p1damage_receivedA1["damage"] = 25
        else:
            p = "p2"
            player = self.p2Companion(get=True)

            if self.p2damage_sentA1["until"] != 0:
                self.p2damage_sentA2["damage"] = 25
                self.p2damage_sentA2["until"] = 1
                #
                self.p2damage_receivedA2["until"] = 1
                self.p2damage_receivedA2["damage"] = 25
            else:
                self.p2damage_sentA1["damage"] = 25
                self.p2damage_sentA1["until"] = 1
                #
                self.p2damage_receivedA1["until"] = 1
                self.p2damage_receivedA1["damage"] = 25

        msg = "You decreased your opponent next attack by 25% and increased your by 25%"
        self.leftUse[p] -= 1
        self.inUse[p].append(ShardedBone().emote)
        self.used[p].append(ShardedBone().emote)
        self.ShardedBone[p] = 1
        return msg

class BlueFragment():
    name = "Blue Fragment"
    emote = "📘"
    number = 4
    price = 30000
    useBy = [e.WaterElement.emote]

    s = ["Immune from all negative effects for 2 rounds"]
    skills = "You will be immunized against negative effects for 2 rounds"

    def use(self):
        if self.player1_turn:
            p = "p1"
            player = self.p1Companion(get=True)

        else:
            p = "p2"
            player = self.p2Companion(get=True)

        self.isImmune[p]["state"] = True
        self.isImmune[p]["until"] += 2

        msg = "For the next 2 rounds, you will be immunized against negative effects."
        self.leftUse[p] -= 1
        self.inUse[p].append(BlueFragment().emote)
        self.used[p].append(BlueFragment().emote)
        self.BlueFragment[p] = 1
        return msg

class RedFragment():
    name = "Red Fragment"
    emote = "📕"
    number = 5
    price = 30000
    useBy = [e.FireElement.emote]

    s = ["Burn opponent for 2 rounds, 20% of the attacker damage"]
    skills = "Your opponent will burn for 2 round dealing 20% damage each time"

    def use(self):
        if self.player1_turn:
            p = "p1"
            notp = "p2"
            player = self.p1Companion(get=True)

            if self.isImmune[notp]["state"] is True:
                msg = "You tried to burn your opponent, but he was immunized.."
                self.leftUse[p] -= 1
                self.inUse[p].append(RedFragment().emote)
                self.used[p].append(RedFragment().emote)
                return msg
        else:
            p = "p2"
            notp = "p1"
            player = self.p2Companion(get=True)

            if self.isImmune[notp]["state"] is True:
                msg = "You tried to burn your opponent, but he was immunized.."
                self.leftUse[p] -= 1
                self.inUse[p].append(RedFragment().emote)
                self.used[p].append(RedFragment().emote)
                return msg

        self.isBurning[notp]["state"] = True
        self.isBurning[notp]["until"] = 2
        self.isBurning[notp]["damage"] = int(((player.attack)*20)/100)

        msg = f"Your opponent is now burning for the 2 next rounds, which will cause a loss of {(player.attack*20)/100}HP each round"
        self.leftUse[p] -= 1
        self.inUse[notp].append(RedFragment().emote)
        self.used[p].append(RedFragment().emote)
        self.RedFragment[notp] = 1
        return msg

class GreenFragment():
    name = "Green Fragment"
    emote = "📗"
    number = 6
    price = 30000
    useBy = [e.EarthElement.emote]

    s = ["Reduce all damage received by 20% for 2 rounds"]
    skills = "All received damage will be reduced by 20% for 2 rounds"

    def use(self):
        if self.player1_turn:
            p = "p1"
            notp = "p2"
            player = self.p1Companion(get=True)

            if self.p1damage_receivedA1["until"] > 0:
                self.p1damage_receivedA2["until"] = 2
                self.p1damage_receivedA2["damage"] = 20
            else:
                self.p1damage_receivedA1["until"] = 2
                self.p1damage_receivedA1["damage"] = 20

        else:
            p = "p2"
            notp = "p1"
            player = self.p2Companion(get=True)

            if self.p2damage_receivedA1["until"] > 0:
                self.p2damage_receivedA2["until"] = 2
                self.p2damage_receivedA2["damage"] = 20
            else:
                self.p2damage_receivedA1["until"] = 2
                self.p2damage_receivedA1["damage"] = 20

        msg = f"For the next 3 rounds, received damage will be reduced by 20%"
        self.leftUse[p] -= 1
        self.inUse[p].append(GreenFragment().emote)
        self.used[p].append(GreenFragment().emote)
        self.GreenFragment[p] = 1
        return msg

class BlueFragmentII():
    name = "Blue Fragment II"
    emote = "📘"
    number = 7
    price = 30000
    useBy = [e.WaterElement.emote]

    s = ["Immune from all negative effects for 3 rounds"]
    skills = "You will be immunized against negative effects for 3 rounds"

    def use(self):
        if self.player1_turn:
            p = "p1"
            player = self.p1Companion(get=True)
        else:
            p = "p2"
            player = self.p2Companion(get=True)

        self.isImmune[p]["state"] = True
        self.isImmune[p]["until"] += 3

        msg = "For the next 3 rounds, you will be immunized against negative effects."
        self.leftUse[p] -= 1
        self.inUse[p].append(BlueFragmentII().emote)
        self.used[p].append(BlueFragmentII().emote)
        self.BlueFragmentII[p] = 1
        return msg

class RedFragmentII():
    name = "Red Fragment II"
    emote = "📕"
    number = 8
    price = 30000
    useBy = [e.FireElement.emote]

    s = ["Burn opponent for 3 rounds"]
    skills = "Your opponent will burn for 3 round dealing 30% damage each time"

    def use(self):
        if self.player1_turn:
            p = "p1"
            notp = "p2"
            player = self.p1Companion(get=True)

            if self.isImmune[notp]["state"] is True:
                msg = "You tried to burn your opponent, but he was immunized.."
                self.leftUse[p] -= 1
                self.inUse[p].append(RedFragmentII().emote)
                self.used[p].append(RedFragmentII().emote)
                return msg
        else:
            p = "p2"
            notp = "p1"
            player = self.p2Companion(get=True)

            if self.isImmune[notp]["state"] is True:
                msg = "You tried to burn your opponent, but he was immunized.."
                self.leftUse[p] -= 1
                self.inUse[p].append(RedFragmentII().emote)
                self.used[p].append(RedFragmentII().emote)
                return msg

        self.isBurning[notp]["state"] = True
        self.isBurning[notp]["until"] = 3
        self.isBurning[notp]["damage"] = int(((player.attack)*30)/100)

        msg = f"Your opponent is now burning for the 3 next rounds, which will cause a loss of {(player.attack*30)/100}HP each round"
        self.leftUse[p] -= 1
        self.inUse[notp].append(RedFragmentII().emote)
        self.RedFragmentII[notp] = 1
        return msg

class GreenFragmentII():
    name = "Green Fragment II"
    emote = "📗"
    number = 9
    price = 30000
    useBy = [e.EarthElement.emote]

    s = ["Reduce all damage received by 20% for 3 rounds"]
    skills = "All received damage will be reduced by 20% for 3 rounds"
    def use(self):
        if self.player1_turn:
            p = "p1"
            notp = "p2"
            player = self.p1Companion(get=True)

            if self.p1damage_receivedA1["until"] > 0:
                self.p1damage_receivedA2["until"] = 3
                self.p1damage_receivedA2["damage"] = 20
            else:
                self.p1damage_receivedA1["until"] = 3
                self.p1damage_receivedA1["damage"] = 20

        else:
            p = "p2"
            notp = "p1"
            player = self.p2Companion(get=True)

            if self.p2damage_receivedA1["until"] > 0:
                self.p2damage_receivedA2["until"] = 3
                self.p2damage_receivedA2["damage"] = 20
            else:
                self.p2damage_receivedA1["until"] = 3
                self.p2damage_receivedA1["damage"] = 20

        msg = f"For the next 3 rounds, received damage will be reduced by 20%"
        self.leftUse[p] -= 1
        self.inUse[p].append(GreenFragmentII().emote)
        self.used[p].append(GreenFragmentII().emote)
        self.GreenFragmentII[p] = 1
        return msg

class BlackRelics():
    name = "Black Relics"
    emote = "🔐"
    number = 10
    price = 30000
    useBy = [e.FireElement.emote, e.WaterElement.emote, e.EarthElement.emote, e.DarkElement.emote]

    s = ["Lock the opponent's ability for 3 rounds"]
    skills = "Your opponent's ability will be locked for 3 rounds"

    def use(self):
        if self.player1_turn:
            p = "p1"
            notp = "p2"
        else:
            p = "p2"
            notp = "p1"

        if self.isLocked[notp]["until"] == -1:
            msg = "Your opponent was immunized against ability's lock. Your ability power was wasted"

        elif self.isImmune[notp]["state"] is True:
                msg = "You opponent is immunized against negative thing.."
                self.leftUse[p] -= 1
                self.inUse[p].append(BlackRelics().emote)
                self.used[p].append(BlackRelics().emote)
                return msg
        else:
            self.isLocked[notp]["state"] = True
            self.isLocked[notp]["until"] = 5#3
            msg = "You locked for 3 rounds your opponent ability."
            self.inUse[notp].append(BlackRelics().emote)
            self.BlackRelics[notp] = 1

        self.leftUse[p] -= 1
        self.used[p].append(BlackRelics().emote)
        return msg

class LightRelics():
    name = "Light Relics"
    emote = "🔑"
    number = 11
    price = 30000
    useBy = [e.FireElement.emote, e.WaterElement.emote, e.EarthElement.emote, e.LightElement.emote]
    s = ["Unlock all locked ability, immune to ability lock"]
    skills = "Unlock all your locked abilities and immune you against ability's lock"

    def use(self):
        if self.player1_turn:
            p = "p1"
            notp = "p2"
            player = self.p1Companion(get=True)
        else:
            p = "p2"
            notp = "p1"
            player = self.p2Companion(get=True)

        self.isLocked[p]["state"] = False
        self.isLocked[p]["until"] = -1

        msg = "You unlocked your abilities and are now immune against ability lock."
        self.leftUse[p] -= 1
        self.inUse[p].append(LightRelics().emote)
        self.used[p].append(LightRelics().emote)
        self.LightRelics[p] = 1
        return msg

class GodsEye():
    name = "God's eye"
    emote = "👁"
    number = 12
    price = 30000
    useBy = [e.FireElement.emote, e.WaterElement.emote, e.EarthElement.emote, e.LightElement.emote, e.DarkElement.emote]

    s = ["Damage received for the next round are decreased by 50% and the opponent will take this amount of damage too"]
    skills = "Next round your opponent attack you, you will receive only 50% of the damage and reflect 50% of that damage back to opponent."

    def use(self):
        if self.player1_turn:
            p = "p1"
            notp = "p2"
            player = self.p1Companion(get=True)

            if self.p1damage_receivedA2["until"] > 0:
                self.p1damage_receivedA1["until"] = 1
                self.p1damage_receivedA1["damage"] = 50
            else:
                self.p1damage_receivedA2["until"] = 1
                self.p1damage_receivedA2["damage"] = 50

            self.p2damage = 50
        else:
            p = "p2"
            notp = "p1"
            player = self.p2Companion(get=True)

            if self.p2damage_receivedA2["until"] > 0:
                self.p2damage_receivedA1["until"] = 1
                self.p2damage_receivedA1["damage"] = 50
            else:
                self.p2damage_receivedA2["until"] = 1
                self.p2damage_receivedA2["damage"] = 50

            self.p1damage = 50

        msg = f"Next attack against you will be reduced by 50% and attacker will take 50% of damage too"
        self.leftUse[p] -= 1
        self.inUse[p].append(GodsEye().emote)
        self.used[p].append(GodsEye().emote)
        self.GodsEye[p] = 1
        #self.inUse[notp].append(GodsEye().emote)
        #self.GodsEye[notp] = 1
        return msg

class EmeraldShards():
    name = "Emerald shards"
    emote = "✳️"
    number = 13
    price = 30000
    useBy = [e.FireElement.emote, e.WaterElement.emote, e.EarthElement.emote, e.LightElement.emote, e.DarkElement.emote]

    s = ["If HP is lower than 30% next damage increase by 100%, if not by 50%"]
    skills = "If your HP is lower than 30%, your next attack damage will be increased by 100% else by 50%"

    def use(self):
        if self.player1_turn:
            p = "p1"
            notp = "p2"
            player = self.p1Companion(get=True)

            if player.hp < (player.totalHp*30)/100:
                dmg = 100
            else:
                dmg = 50

            if self.p1damage_sentA1["until"] > 0:
                self.p1damage_sentA2["damage"] = dmg
                self.p1damage_sentA2["until"] = 1
            else:
                self.p1damage_sentA1["damage"] = dmg
                self.p1damage_sentA1["until"] = 1

        else:
            p = "p2"
            notp = "p1"
            player = self.p2Companion(get=True)

            if player.hp < (player.totalHp*30)/100:
                dmg = 100
            else:
                dmg = 50

            if self.p2damage_sentA1["until"] > 0:
                self.p2damage_sentA2["damage"] = dmg
                self.p2damage_sentA2["until"] = 1
            else:
                self.p2damage_sentA1["damage"] = dmg
                self.p2damage_sentA1["until"] = 1

        msg = f"You just increased your next attack by {dmg}%"
        self.leftUse[p] -= 1
        self.inUse[p].append(EmeraldShards().emote)
        self.used[p].append(EmeraldShards().emote)
        self.EmeraldShards[p] = 1
        return msg


abilities = [
    FrozeArtifact,
    HealingRing,
    HealingRingII,
    ShardedBone,
    BlueFragment,
    RedFragment,
    GreenFragment,
    BlueFragmentII,
    RedFragmentII,
    GreenFragmentII,
    BlackRelics,
    LightRelics,
    GodsEye,
    EmeraldShards
]
