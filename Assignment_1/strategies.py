from dataclasses import dataclass
from typing import Protocol


@dataclass
class MovingStrategyParameters:
    stamina: int
    leg_cnt: int
    wing_cnt: int


@dataclass
class MovingStrategyResponse:
    stamina_change: int
    location_change: int


class MovingStrategy(Protocol):
    def move(self, params: MovingStrategyParameters) -> MovingStrategyResponse:
        pass

    MIN_WINGS_FOR_FLIGHT: int = 2
    MIN_LEGS_FOR_RUN: int = 2
    MIN_LEGS_FOR_WALK: int = 2
    MIN_LEGS_FOR_HOP: int = 1
    MIN_LEGS_FOR_CRAWL: int = 0

    MIN_STAMINA_FOR_FLIGHT: int = 81
    MIN_STAMINA_FOR_RUN: int = 61
    MIN_STAMINA_FOR_WALK: int = 41
    MIN_STAMINA_FOR_HOP: int = 21
    MIN_STAMINA_FOR_CRAWL: int = 1

    MOVEMENT_DISTANCE_FOR_FLIGHT: int = 8
    MOVEMENT_DISTANCE_FOR_RUN: int = 6
    MOVEMENT_DISTANCE_FOR_WALK: int = 4
    MOVEMENT_DISTANCE_FOR_HOP: int = 3
    MOVEMENT_DISTANCE_FOR_CRAWL: int = 1

    STAMINA_CONSUMPTION_FOR_FLIGHT: int = -4
    STAMINA_CONSUMPTION_FOR_RUN: int = -4
    STAMINA_CONSUMPTION_FOR_WALK: int = -2
    STAMINA_CONSUMPTION_FOR_HOP: int = -2
    STAMINA_CONSUMPTION_FOR_CRAWL: int = -1


class NoMovingStrategy(MovingStrategy):
    def move(self, params: MovingStrategyParameters) -> MovingStrategyResponse:
        return MovingStrategyResponse(0, 0)


class DefaultMovingStrategy(MovingStrategy):
    def move(self, params: MovingStrategyParameters) -> MovingStrategyResponse:
        if (
            params.wing_cnt >= MovingStrategy.MIN_WINGS_FOR_FLIGHT
            and params.stamina >= MovingStrategy.MIN_STAMINA_FOR_FLIGHT
        ):
            return MovingStrategyResponse(
                MovingStrategy.STAMINA_CONSUMPTION_FOR_FLIGHT,
                MovingStrategy.MOVEMENT_DISTANCE_FOR_FLIGHT,
            )

        elif (
            params.leg_cnt >= MovingStrategy.MIN_LEGS_FOR_RUN
            and params.stamina >= MovingStrategy.MIN_STAMINA_FOR_RUN
        ):
            return MovingStrategyResponse(
                MovingStrategy.STAMINA_CONSUMPTION_FOR_RUN,
                MovingStrategy.MOVEMENT_DISTANCE_FOR_RUN,
            )

        elif (
            params.leg_cnt >= MovingStrategy.MIN_LEGS_FOR_WALK
            and params.stamina >= MovingStrategy.MIN_STAMINA_FOR_WALK
        ):
            return MovingStrategyResponse(
                MovingStrategy.STAMINA_CONSUMPTION_FOR_WALK,
                MovingStrategy.MOVEMENT_DISTANCE_FOR_WALK,
            )
        elif (
            params.leg_cnt >= MovingStrategy.MIN_LEGS_FOR_HOP
            and params.stamina >= MovingStrategy.MIN_STAMINA_FOR_HOP
        ):
            return MovingStrategyResponse(
                MovingStrategy.STAMINA_CONSUMPTION_FOR_HOP,
                MovingStrategy.MOVEMENT_DISTANCE_FOR_HOP,
            )

        elif (
            params.leg_cnt >= MovingStrategy.MIN_LEGS_FOR_CRAWL
            and params.stamina >= MovingStrategy.MIN_STAMINA_FOR_CRAWL
        ):
            return MovingStrategyResponse(
                MovingStrategy.STAMINA_CONSUMPTION_FOR_CRAWL,
                MovingStrategy.MOVEMENT_DISTANCE_FOR_CRAWL,
            )
        return MovingStrategyResponse(0, 0)


@dataclass
class AttackingStrategyParameters:
    power: int
    teeth_type: int
    claw_size: int


class AttackingStrategyResponse:
    damage: int


class AttackingStrategy(Protocol):
    def calculate_damage(self, params: AttackingStrategyParameters) -> int:
        pass


class NoAttackingStrategy(AttackingStrategy):
    def calculate_damage(self, params: AttackingStrategyParameters) -> int:
        return 1


class DefaultAttackingStrategy(AttackingStrategy):
    def calculate_damage(self, params: AttackingStrategyParameters) -> int:
        # i = params.power * (params.claw_size + 1) + params.teeth_type * 3
        i = (params.power + params.teeth_type * 3) * (params.claw_size + 1)

        return int(i)
