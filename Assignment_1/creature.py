from __future__ import annotations

from dataclasses import dataclass, field

from agents import FightingAgent, IFightingAgent, IMovingAgent, MovingAgent
from strategies import AttackingStrategy, MovingStrategy


class ICreature(IMovingAgent, IFightingAgent):
    pass


@dataclass
class Creature(ICreature):
    moving_agent: IMovingAgent = field(default_factory=MovingAgent)
    fighting_agent: IFightingAgent = field(default_factory=FightingAgent)

    def spawn(self, init_location: int) -> None:
        self.moving_agent.spawn(init_location)

    def evolve_legs(self) -> None:
        self.moving_agent.evolve_legs()

    def evolve_wings(self) -> None:
        self.moving_agent.evolve_wings()

    def evolve_claws(self) -> None:
        self.fighting_agent.evolve_claws()

    def evolve_teeth(self) -> None:
        self.fighting_agent.evolve_teeth()

    @property
    def location(self) -> int:
        return self.moving_agent.location

    @property
    def stamina(self) -> int:
        return self.moving_agent.stamina

    @property
    def health(self) -> int:
        return self.fighting_agent.health

    @property
    def leg_cnt(self) -> int:
        return self.moving_agent.leg_cnt

    @property
    def wing_cnt(self) -> int:
        return self.moving_agent.wing_cnt

    @property
    def claw_size(self) -> int:
        return self.fighting_agent.claw_size

    @property
    def teeth_type(self) -> int:
        return self.fighting_agent.teeth_type

    def set_moving_strategy(self, moving_strategy: MovingStrategy) -> None:
        self.moving_agent.set_moving_strategy(moving_strategy)

    def move(self) -> None:
        self.moving_agent.move()

    def set_attacking_strategy(self, atck_strg: AttackingStrategy) -> None:
        self.fighting_agent.set_attacking_strategy(atck_strg)

    def take_damage(self, damage: int) -> None:
        self.fighting_agent.take_damage(damage)

    def attack(self, other: IFightingAgent) -> int:
        return self.fighting_agent.attack(other)


@dataclass
class MemorizedDamageCreature(ICreature):
    inner: ICreature = field(default_factory=Creature)
    default_damage: int = 1
    has_evolved: bool = False

    def spawn(self, init_location: int) -> None:
        self.inner.spawn(init_location)

    def evolve_legs(self) -> None:
        self.inner.evolve_legs()

    def evolve_wings(self) -> None:
        self.inner.evolve_wings()

    def evolve_claws(self) -> None:
        self.inner.evolve_claws()
        self.has_evolved = True

    def evolve_teeth(self) -> None:
        self.inner.evolve_teeth()
        self.has_evolved = True

    @property
    def location(self) -> int:
        return self.inner.location

    @property
    def stamina(self) -> int:
        return self.inner.stamina

    @property
    def health(self) -> int:
        return self.inner.health

    @property
    def leg_cnt(self) -> int:
        return self.inner.leg_cnt

    @property
    def wing_cnt(self) -> int:
        return self.inner.wing_cnt

    @property
    def claw_size(self) -> int:
        return self.inner.claw_size

    @property
    def teeth_type(self) -> int:
        return self.inner.teeth_type

    def set_moving_strategy(self, moving_strategy: MovingStrategy) -> None:
        self.inner.set_moving_strategy(moving_strategy)

    def move(self) -> None:
        self.inner.move()

    def set_attacking_strategy(self, atck_strg: AttackingStrategy) -> None:
        self.inner.set_attacking_strategy(atck_strg)

    def take_damage(self, damage: int) -> None:
        self.inner.take_damage(damage)

    def attack(self, other: IFightingAgent) -> int:
        if self.has_evolved:
            self.default_damage = self.inner.attack(other)
            self.has_evolved = False
            return self.default_damage
        else:
            other.take_damage(self.default_damage)
            return self.default_damage
