from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Protocol

from agents import Claws, Teeth
from creature import ICreature, MemorizedDamageCreature
from strategies import DefaultAttackingStrategy, DefaultMovingStrategy


class EvolutionStrategy(Protocol):
    def evolve(self, creature: ICreature) -> None:
        pass


class RandomEvolutionStrategy(EvolutionStrategy):
    def evolve(self, creature: ICreature) -> None:
        cnt = random.randint(1, 3)

        for _ in range(cnt):
            creature.evolve_legs()

        cnt = random.randint(1, 3)
        for _ in range(cnt):
            creature.evolve_wings()

        cnt = random.randint(1, 3)
        for _ in range(cnt):
            creature.evolve_claws()

        cnt = random.randint(1, 3)
        for _ in range(cnt):
            creature.evolve_teeth()


class PhaseHandler(Protocol):
    def handle(self, predator: ICreature, pray: ICreature, state: bool) -> None:
        pass


class NoHandler(PhaseHandler):
    def handle(self, predator: ICreature, pray: ICreature, state: bool) -> None:
        # raise NoSuitableHandlerException(
        #     "No suitable handler found. Simulation terminated."
        # )
        print("No suitable handler found. Simulation terminated.")


class NoSuitableHandlerException(Exception):
    pass


@dataclass
class EvolutionHandler(PhaseHandler):
    following: PhaseHandler = field(default_factory=NoHandler)
    evolution_strategy: EvolutionStrategy = field(
        default_factory=RandomEvolutionStrategy
    )  # dumb flake :(((

    def handle(self, predator: ICreature, pray: ICreature, state: bool) -> None:
        print("Evolving...\n")

        # Handle evolution phase for creatures
        # Implement the logic to evolve creatures' traits
        if state:
            self._evolve_creature(predator)
            self._evolve_creature(pray)
            self._log_characteristics(predator, "Predator")
            self._log_characteristics(pray, "Pray")
        self.following.handle(predator, pray, state)

    def _evolve_creature(self, creature: ICreature) -> None:
        self.evolution_strategy.evolve(creature)
        ...

    def _log_characteristics(
        self, creature: ICreature, creature_type: str
    ) -> None:  # goddamn flake
        print(creature_type + " characteristics:")
        print("Amount of wings: " + str(creature.wing_cnt))
        print("Amount of legs: " + str(creature.leg_cnt))
        print(Claws.CLAW_SIZES[creature.claw_size])
        print(Teeth.TEETH_TYPES[creature.teeth_type])
        print()
        ...


@dataclass
class ChaseHandler(PhaseHandler):
    following: PhaseHandler = field(default_factory=NoHandler)

    def handle(self, predator: ICreature, pray: ICreature, state: bool) -> None:
        print("Chasing...\n")
        if state:
            # Handle chase phase for creatures
            while True:
                predator.move()
                if predator.location >= pray.location:
                    break
                if predator.stamina <= 0:  # predator out of stamina:
                    state = False
                    print("Pray ran into infinity")
                    break
                pray.move()
        self.following.handle(predator, pray, state)


@dataclass
class FightHandler(PhaseHandler):
    following: PhaseHandler = field(default_factory=NoHandler)

    def handle(self, predator: ICreature, pray: ICreature, state: bool) -> None:
        # Handle fight phase for creatures
        if state:
            print("Fighting...\n")
            while True:
                predator.attack(pray)
                if pray.health <= 0:
                    state = False
                    print("Pray ran into infinity")
                    break
                pray.attack(predator)
                if predator.health <= 0:
                    state = False
                    print("Some R-rated things have happened")
                    break
        self.following.handle(predator, pray, state)


@dataclass
class SporeSimulator:
    brain: PhaseHandler = field(default_factory=NoHandler)
    predator: ICreature = field(default_factory=MemorizedDamageCreature)
    pray: ICreature = field(default_factory=MemorizedDamageCreature)

    # default setup method that client can call
    # don't forget to set strategies
    def setup(self) -> None:
        self.predator = MemorizedDamageCreature()
        self.predator.set_moving_strategy(DefaultMovingStrategy())
        self.predator.set_attacking_strategy(DefaultAttackingStrategy())
        self.pray = MemorizedDamageCreature()
        self.pray.set_moving_strategy(DefaultMovingStrategy())
        self.pray.set_attacking_strategy(DefaultAttackingStrategy())
        self.predator.spawn(0)
        self.pray.spawn(random.randint(1, 100))
        self.brain = EvolutionHandler(ChaseHandler(FightHandler()))

    # methods which let client do custom setup
    def set_pray(self, creature: ICreature) -> None:
        self.pray = creature

    def set_predator(self, creature: ICreature) -> None:
        self.predator = creature

    def set_brain(self, brain: PhaseHandler) -> None:
        self.brain = brain

    def run(self) -> None:
        print("=====================starting simulation====================\n")
        state = True
        self.brain.handle(self.predator, self.pray, state)


if __name__ == "__main__":
    simulator = SporeSimulator()
    for _ in range(100):
        simulator.setup()
        simulator.run()
