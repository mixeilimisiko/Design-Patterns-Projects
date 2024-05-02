from creature import MemorizedDamageCreature
from strategies import DefaultAttackingStrategy


def test_constructor() -> None:
    creature = MemorizedDamageCreature()

    assert creature.default_damage == 1
    assert creature.has_evolved is False


def test_damage_memorization() -> None:
    creature = MemorizedDamageCreature()
    creature.set_attacking_strategy(DefaultAttackingStrategy())
    creature.evolve_teeth()

    assert creature.has_evolved is True
    assert creature.default_damage == 1

    creature.attack(creature)

    assert creature.has_evolved is False
    assert creature.default_damage == 4

    creature.evolve_claws()
    assert creature.has_evolved is True
    assert creature.default_damage == 4

    creature.attack(creature)
    assert creature.has_evolved is False
    assert creature.default_damage == 8
