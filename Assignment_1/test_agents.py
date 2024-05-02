import random

from agents import Claws, FightingAgent, Legs, MovingAgent, Teeth, Wings
from strategies import DefaultAttackingStrategy, DefaultMovingStrategy, MovingStrategy

""" Evolvable Trait Tests """


def test_leg_constructor() -> None:
    legs = Legs()

    assert legs.evolution_stage() == 0


def test_leg_evolution() -> None:
    legs = Legs()

    for i in range(5):
        legs.evolve()

        assert legs.evolution_stage() == i + 1


def test_wing_constructor() -> None:
    wings = Wings()

    assert wings.evolution_stage() == 0


def test_wing_evolution() -> None:
    wings = Wings()

    for i in range(5):
        wings.evolve()

        assert wings.evolution_stage() == i + 1


def test_claws_constructor() -> None:
    claws = Claws()

    assert claws.evolution_stage() == 0


def test_claws_evolution() -> None:
    claws = Claws()

    for i in range(3):
        claws.evolve()

        assert claws.evolution_stage() == i + 1


def test_teeth_constructor() -> None:
    teeth = Teeth()

    assert teeth.evolution_stage() == 0


def test_teeth_evolution() -> None:
    teeth = Teeth()

    for i in range(3):
        teeth.evolve()
        assert teeth.evolution_stage() == i + 1


def test_teeth_evolution_limit() -> None:
    teeth = Teeth()
    for i in range(4):
        teeth.evolve()

    assert teeth.evolution_stage() == 3


""" MovingAgent Tests """


def test_moving_agent_constructor() -> None:
    ma = MovingAgent()

    assert ma.location == 0
    assert ma.leg_cnt == 0
    assert ma.wing_cnt == 0
    assert ma.stamina == 100


def test_spawn() -> None:
    ma = MovingAgent()
    spawn_loc = 50

    ma.spawn(spawn_loc)

    assert ma.location == spawn_loc


def test_ma_leg_evolution() -> None:
    ma = MovingAgent()

    ma.evolve_legs()

    assert ma.leg_cnt == 1


def test_ma_wing_evolution() -> None:
    ma = MovingAgent()

    ma.evolve_wings()

    assert ma.wing_cnt == 1


def test_no_strategy_move() -> None:
    ma = MovingAgent()

    ma.move()

    assert ma.location == 0


def test_move_without_evolution() -> None:
    ma = MovingAgent()
    ma.set_moving_strategy(DefaultMovingStrategy())
    init_stamina = ma.stamina

    ma.move()

    assert ma.location == MovingStrategy.MOVEMENT_DISTANCE_FOR_CRAWL
    assert (
        ma.stamina == init_stamina + MovingStrategy.STAMINA_CONSUMPTION_FOR_CRAWL
    )  # frank zappa - flakes


def test_move_after_evolution() -> None:
    ma = MovingAgent()
    ma.evolve_legs()
    ma.evolve_legs()
    ma.set_moving_strategy(DefaultMovingStrategy())
    init_stamina = ma.stamina

    ma.move()

    assert ma.location == MovingStrategy.MOVEMENT_DISTANCE_FOR_RUN
    assert (
        ma.stamina == init_stamina + MovingStrategy.STAMINA_CONSUMPTION_FOR_RUN
    )  # aaaaaaaaaagh flake!!!


""" FightingAgent Tests """


def test_fighting_agent_constructor() -> None:
    fa = FightingAgent()

    assert fa.health == 100
    assert fa.claw_size == 0
    assert fa.teeth_type == 0
    assert fa.power == 1


def test_fa__claw_evolution() -> None:
    fa = FightingAgent()
    init_claw_size = fa.claw_size

    fa.evolve_claws()

    assert fa.claw_size == init_claw_size + 1


def test_fa__teeth_evolution() -> None:
    fa = FightingAgent()
    init_teeth_type = fa.teeth_type

    fa.evolve_teeth()

    assert fa.teeth_type == init_teeth_type + 1


def test_take_damage() -> None:
    fa = FightingAgent()
    assert fa.health == 100

    damage = random.randint(1, 100)
    fa.take_damage(damage)

    assert fa.health == 100 - damage


def test_no_strategy_attack() -> None:
    predator = FightingAgent()
    prey = FightingAgent()

    predator.attack(prey)

    assert prey.health == 99


def test_attack_without_evolution() -> None:
    predator = FightingAgent()
    prey = FightingAgent()
    predator.set_attacking_strategy(DefaultAttackingStrategy())

    predator.attack(prey)

    assert prey.health == 99


def test_attack_with_claw_evolution() -> None:
    predator = FightingAgent()
    prey = FightingAgent()
    predator.set_attacking_strategy(DefaultAttackingStrategy())

    predator.evolve_claws()

    predator.attack(prey)

    assert prey.health == 98


def test_attack_with_teeth_evolution() -> None:
    predator = FightingAgent()
    prey = FightingAgent()
    predator.set_attacking_strategy(DefaultAttackingStrategy())

    predator.evolve_teeth()

    predator.attack(prey)

    assert prey.health == 96
