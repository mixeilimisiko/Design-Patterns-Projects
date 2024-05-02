from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from strategies import (  # AttackingStrategyResponse,; MovingStrategyResponse,
    AttackingStrategy,
    AttackingStrategyParameters,
    MovingStrategy,
    MovingStrategyParameters,
    NoAttackingStrategy,
    NoMovingStrategy,
)


class EvolvableTrait(Protocol):
    def evolve(self) -> None:
        pass

    def evolution_stage(self) -> int:
        pass


#    at this point defining different EvolvableTrait implementations
#    for Legs, Wings and Claws was probably unnecessary,
#    because they all behave the same way so that one
#    DefaultEvolvableTrait class would have been enough,
#    but in general legs wings and claws might develop
#    different evolution logic which is why I left it as it is now.


@dataclass
class Legs(EvolvableTrait):
    leg_cnt: int = 0

    def evolve(self) -> None:
        self.leg_cnt = self.leg_cnt + 1

    def evolution_stage(self) -> int:
        return self.leg_cnt


@dataclass
class Wings(EvolvableTrait):
    wing_cnt: int = 0

    def evolve(self) -> None:
        self.wing_cnt = self.wing_cnt + 1

    def evolution_stage(self) -> int:
        return self.wing_cnt


@dataclass
class Claws(EvolvableTrait):
    claw_size: int = 0

    CLAW_SIZES = {
        0: "No claws",
        1: "Small claws",
        2: "Medium claws",
        3: "Big claws",
    }

    def evolve(self) -> None:
        if self.claw_size < 3:
            self.claw_size = self.claw_size + 1

    def evolution_stage(self) -> int:
        return self.claw_size


@dataclass
class Teeth(EvolvableTrait):
    teeth_type: int = 0

    TEETH_TYPES = {
        0: "Blunt teeth",
        1: "Moderate teeth",
        2: "Sharp teeth",
        3: "Ultra-sharp teeth",
    }

    def evolve(self) -> None:
        if self.teeth_type < 3:
            self.teeth_type = self.teeth_type + 1

    def evolution_stage(self) -> int:
        return self.teeth_type


class IMovingAgent(Protocol):
    def spawn(self, init_location: int) -> None:
        pass

    def evolve_legs(self) -> None:
        pass

    def evolve_wings(self) -> None:
        pass

    @property
    def location(self) -> int:
        return 0

    @property
    def stamina(self) -> int:
        return 0

    @property
    def leg_cnt(self) -> int:
        return 0

    @property
    def wing_cnt(self) -> int:
        return 0

    def set_moving_strategy(self, moving_strategy: MovingStrategy) -> None:
        pass

    def move(self) -> None:
        pass


class IFightingAgent(Protocol):
    def evolve_claws(self) -> None:
        pass

    def evolve_teeth(self) -> None:
        pass

    @property
    def health(self) -> int:
        return 0

    @property
    def claw_size(self) -> int:
        return 0

    @property
    def teeth_type(self) -> int:
        return 0

    def set_attacking_strategy(self, atck_strg: AttackingStrategy) -> None:
        pass

    def take_damage(self, damage: int) -> None:
        pass

    def attack(self, other: IFightingAgent) -> int:
        return 0


@dataclass
class MovingAgent(IMovingAgent):
    moving_strategy: MovingStrategy = field(default_factory=NoMovingStrategy)
    legs: EvolvableTrait = field(default_factory=Legs)
    wings: EvolvableTrait = field(default_factory=Wings)
    loc: int = 0
    stamina_val: int = 100

    def spawn(self, init_location: int) -> None:
        self.loc = init_location

    def evolve_legs(self) -> None:
        self.legs.evolve()

    def evolve_wings(self) -> None:
        self.wings.evolve()

    @property
    def location(self) -> int:
        return self.loc

    @property
    def leg_cnt(self) -> int:
        return self.legs.evolution_stage()

    @property
    def wing_cnt(self) -> int:
        return self.wings.evolution_stage()

    @property
    def stamina(self) -> int:
        return self.stamina_val

    def set_moving_strategy(self, moving_strategy: MovingStrategy) -> None:
        self.moving_strategy = moving_strategy

    def move(self) -> None:
        params = MovingStrategyParameters(
            self.stamina_val, self.leg_cnt, self.wing_cnt
        )  # boooo flake8
        response = self.moving_strategy.move(params)
        self.stamina_val += response.stamina_change
        self.loc += response.location_change


@dataclass
class FightingAgent(IFightingAgent):
    atck_strg: AttackingStrategy = field(default_factory=NoAttackingStrategy)
    claws: EvolvableTrait = field(default_factory=Claws)
    teeth: EvolvableTrait = field(default_factory=Teeth)
    health_value: int = 100
    power: int = 1

    @property
    def health(self) -> int:
        return self.health_value

    def evolve_claws(self) -> None:
        self.claws.evolve()

    def evolve_teeth(self) -> None:
        self.teeth.evolve()

    @property
    def claw_size(self) -> int:
        return self.claws.evolution_stage()

    @property
    def teeth_type(self) -> int:
        return self.teeth.evolution_stage()

    def set_attacking_strategy(self, atck_strg: AttackingStrategy) -> None:
        self.atck_strg = atck_strg

    def take_damage(self, damage: int) -> None:
        self.health_value -= damage

    def attack(self, other: IFightingAgent) -> int:
        params = AttackingStrategyParameters(
            self.power, self.teeth_type, self.claw_size
        )
        dealt_damage = self.atck_strg.calculate_damage(params)
        other.take_damage(dealt_damage)
        return dealt_damage
