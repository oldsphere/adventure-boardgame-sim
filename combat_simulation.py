from combat_rules import *

ork = Entity(
    name='Ork1', 
    life=2, 
    attack_dices=[
        attack,
        basic,
    ]
)

daemon = Entity(
    name='Daemon',
    life=25,
    attack_dices=[
        attack,
        attack,
        attack,
        defense,
        defense,
        defense,
        def1,
        off2,
        off2,
    ]
)

trasgo = Entity(
    name='Trasgo', 
    life=1, 
    attack_dices=[
        basic,
    ]
)

PJ_low = Entity(
    name='Warrior', 
    life=5+1, 
    attack_dices=[
        # Arma
        off1,
        def1,
    ]
)

PJ_high = Entity(
    name='Warrior', 
    life=5+5+3, 
    attack_dices=[
        # Arma
        attack,
        attack,
        off2,

        # Armadura
        defense,
        def1,
        def1,

        # Habilidad
        def1,
        off2,
        def1,
        def1,
    ]
)


enemy = ork
PJ = PJ_low

print(PJ.mean_attack())

stats = CombatStats()
Combat(PJ,enemy,stats,verbose=True)
stats.show()

MultiCombat(PJ, enemy)
