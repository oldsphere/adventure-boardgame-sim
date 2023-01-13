import numpy as np
import random
from typing import List
from colors import Color as c
import copy

class Entity:
    def __init__(self, name, life, attack_dices):
        self.life = life
        self.max_life = life
        self.name = name
        self.attack_dices = attack_dices

    def heal(self):
        self.life = self.max_life

    def attack(self, target):
        return Attack(self.attack_dices)

    def addDamage(self, quantity):
        self.life = max(self.life-quantity, 0)

    def isAlive(self):
        return self.life > 0

    def mean_attack(self):
        nAttacks = 2000
        return np.array([
            self.attack(self) for i in range(nAttacks)
            ]).sum(axis=0)/nAttacks

class Horde:
    def __init__(self, entities):
        self.entities = entities

    def addEnemy(self, enemy):
        self.entities.append(enemy)

    def attack(self, target):
        return np.array([e.attack() for e in self.entities]).sum(axis=0)

    def heal(self):
        [e.heal() for e in self.entities]

    def addDamage(self, quantity):
        weakerEntity = sorted(self.entities, key=lambda x: x.life)[0] 
        weakerEntity.addDamage(quantity)
        if not weakerEntity.isAlive():
            self.entities.pop(weakerEntity)

    def isAlive(self):
        return any([e.isAlive() for e in self.entities])

class Dice:
    def __init__(self, name, faces):
        self.name = name
        self.faces = faces

        self._mean = None

    def throw(self):
        return random.choice(self.faces)

    def mean(self):
        if not self._mean: 
            outcome = np.array([self.throw() for _ in range(5000)])
            self._mean = outcome.mean(axis=0)
        return self._mean

class RoundStats:
    def __init__(self, nRound:int, attacker:Entity, defender:Entity):
        self.nRound = nRound

        self.attacker = attacker
        self.defender = defender

        self.attacker_initial_life = attacker.life
        self.defender_initial_life = defender.life

        self.attacker_results = []
        self.defender_results = []

        self.attacker_damage_received = 0
        self.defender_damage_received = 0
        self.attacker_damage_blocked = 0
        self.attacker_damage_done = 0

    def Update(self):
        self.attacker_total_attack = self.attacker_results[0]
        self.attacker_total_defense = self.attacker_results[1]
        self.defender_total_attack = self.defender_results[0]
        self.defender_total_defense = self.defender_results[1]
        self.attacker_damage_done = max(self.attacker_total_attack - self.defender_total_defense, 0)
        self.defender_damage_done = max(self.defender_total_attack - self.attacker_total_defense, 0)
        self.defender_damage_blocked = self.attacker_total_attack - self.attacker_damage_done
        self.attacker_damage_blocked = self.defender_total_attack - self.defender_damage_done

    def show(self):
        attacker_label = f'{self.attacker.name}({self.attacker_initial_life})'
        defender_label = f'{self.defender.name}({self.defender_initial_life})'
        print(
            f'Atacante {c.YELLOW}{attacker_label: <15}{c.END} obtiene:    '
            f'{c.RED}{self.attacker_total_attack} X{c.END}'
            f' y '
            f'{c.BLUE}{self.attacker_total_defense} O{c.END}'
            '\n'

            f'Defensor {c.YELLOW}{defender_label: <15}{c.END} obtiene:    '
            f'{c.BLUE}{self.defender_total_defense} O{c.END}'
            f' y '
            f'{c.RED}{self.defender_total_attack} X{c.END}'
            '\n'
            f'{"": <37}'
            f'{c.BOLD}{self.attacker_damage_done}{c.END}'
            '     '
            f'{c.BOLD}{self.defender_damage_done}{c.END}'
            '\n'
        )
        
class CombatStats:
    def __init__(self):
        self.rounds:List[RoundStats] = []
        self.nRounds = 0

        self.attaker_mean_damage = 0
        self.defender_mean_damage = 0
        self.attacker_mean_blockage = 0
        self.defender_mean_blockage = 0

        self.winner = None

    def round_sum(self,field):
        return sum([r.__dict__[field] for r in self.rounds])

    def Update(self):
        self.attacker_total_damage = self.round_sum('attacker_damage_done')
        self.attacker_mean_damage = self.attacker_total_damage/self.nRounds
        self.attacker_total_block = self.round_sum('attacker_damage_blocked')
        self.attacker_mean_block = self.attacker_total_block/self.nRounds
        self.attacker_mean_block = self.round_sum('attacker_damage_blocked')
        self.defender_total_damage = self.round_sum('defender_damage_done')
        self.defender_mean_damage = self.defender_total_damage/self.nRounds
        self.defender_total_block = self.round_sum('defender_damage_blocked')
        self.defender_mean_block = self.defender_total_block/self.nRounds

    def create_round(self, attacker:Entity, defender:Entity) -> RoundStats:
        self.nRounds += 1
        newRound = RoundStats(self.nRounds, attacker, defender)
        self.rounds.append(newRound)
        return newRound

    def show(self):
        self.Update()

        role = 'defender' if self.winner == self.rounds[-1].defender else 'Attacker'
        print(
            f'Winner: {c.YELLOW}{self.winner.name} ({role}) {c.END}\n'
            f'nRounds: {self.nRounds}\n'
            '\n'
            f'Attacker Statistics:\n'
            f'  Total Damage: {self.attacker_total_damage}\n'
            f'  Mean Damage: {self.attacker_mean_damage:0.3f} per combat\n'
            f'  Blocked Damage: {self.attacker_total_block}\n'
            f'  Mean Blocked Damage: {self.attacker_mean_block:0.3f} per combat\n'
            '\n'
            f'Defender Statistics:\n'
            f'  Total Damage: {self.defender_total_damage}\n'
            f'  Mean Damage: {self.defender_mean_damage:0.3f} per combat\n'
            f'  Blocked Damage: {self.defender_total_block}\n'
            f'  Mean Blocked Damage: {self.defender_mean_block:0.3f} per combat\n'
        )


def Combat(attacker, defender, cStats:CombatStats,verbose=True):
    rStats = cStats.create_round(attacker, defender)
    rStats.attacker_results = attacker.attack(defender)
    rStats.defender_results = defender.attack(attacker)
    rStats.Update()

    if verbose: rStats.show()

    attacker.addDamage(rStats.defender_damage_done)
    if not attacker.isAlive():
        cStats.winner=defender
        return

    defender.addDamage(rStats.attacker_damage_done)
    if not defender.isAlive():
        cStats.winner=attacker
        return

    Combat(attacker,defender,cStats,verbose)


def MultiCombat(attacker, defender):
    nCombats = 1000
    stats = []
    for _ in range(nCombats):
        s = CombatStats()
        Combat(attacker, defender, s, verbose=False)
        attacker.heal()
        defender.heal()
        s.Update()
        stats.append(copy.copy(s))
    
    mean_nTurns = sum([s.nRounds for s in stats])/nCombats
    max_nTurns = max([s.nRounds for s in stats])
    min_nTurns = min([s.nRounds for s in stats])
    num_attacker_wins = len([s for s in stats if s.winner == attacker])
    mean_damage_on_wins = sum([s.defender_total_damage for s in stats if s.winner == attacker])/nCombats
    attacker_winrate = num_attacker_wins/nCombats*100

    print(f'Win Rate: {attacker_winrate:0.2f}%')
    print(f'min/mean/max number of turns: {min_nTurns}/{mean_nTurns}/{max_nTurns}')
    print(f'Average damage suffered: {mean_damage_on_wins}')


def Attack(dices):
    return np.array([ d.throw() for d in dices]).sum(axis=0)

attack = Dice( 'attack', [(1,0)])
defense = Dice( 'defense', [(0,1)])

basic = Dice(
    'basic',
    [
        (0,0),
        (0,1),
        (1,0),
        (1,1),
        (1,0),
        (0,1)
    ]
)
def1 = Dice(
    'basic_deff',
    [
        (0,0),
        (0,2),
        (0,1),
        (0,1),
        (1,1),
        (0,2)
    ]
)
off1 = Dice(
    'basic_off',
    [
        (0,0),
        (2,0),
        (1,0),
        (1,0),
        (1,1),
        (2,0)
    ]
)
off2 = Dice(
    'advance_off',
    [
        (1,0),
        (2,0),
        (2,0),
        (3,0),
        (3,1),
        (5,0)
    ]
)


