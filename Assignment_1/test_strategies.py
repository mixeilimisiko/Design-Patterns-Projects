from strategies import (
    AttackingStrategyParameters,
    DefaultAttackingStrategy,
    DefaultMovingStrategy,
    MovingStrategy,
    MovingStrategyParameters,
)


def test_nothing() -> None:
    pass


def test_enough_wings_to_fly() -> None:
    strategy = DefaultMovingStrategy()
    params = MovingStrategyParameters(
        MovingStrategy.MIN_STAMINA_FOR_FLIGHT,
        MovingStrategy.MIN_LEGS_FOR_RUN,
        MovingStrategy.MIN_WINGS_FOR_FLIGHT,
    )

    response = strategy.move(params)

    assert response.stamina_change == MovingStrategy.STAMINA_CONSUMPTION_FOR_FLIGHT
    assert response.location_change == MovingStrategy.MOVEMENT_DISTANCE_FOR_FLIGHT


def test_not_enough_wings_to_fly() -> None:
    strategy = DefaultMovingStrategy()
    params = MovingStrategyParameters(
        MovingStrategy.MIN_STAMINA_FOR_FLIGHT,
        MovingStrategy.MIN_LEGS_FOR_RUN,
        MovingStrategy.MIN_WINGS_FOR_FLIGHT - 1,
    )

    response = strategy.move(params)

    assert response.stamina_change == MovingStrategy.STAMINA_CONSUMPTION_FOR_RUN
    assert response.location_change == MovingStrategy.MOVEMENT_DISTANCE_FOR_RUN


def test_not_enough_legs_to_run_or_walk() -> None:
    strategy = DefaultMovingStrategy()
    params = MovingStrategyParameters(
        MovingStrategy.MIN_STAMINA_FOR_FLIGHT,
        MovingStrategy.MIN_LEGS_FOR_RUN - 1,
        MovingStrategy.MIN_WINGS_FOR_FLIGHT - 1,
    )

    response = strategy.move(params)

    assert response.stamina_change == MovingStrategy.STAMINA_CONSUMPTION_FOR_HOP
    assert response.location_change == MovingStrategy.MOVEMENT_DISTANCE_FOR_HOP


def test_not_enough_legs_to_hop() -> None:
    strategy = DefaultMovingStrategy()
    params = MovingStrategyParameters(
        MovingStrategy.MIN_STAMINA_FOR_FLIGHT,
        MovingStrategy.MIN_LEGS_FOR_HOP - 1,
        MovingStrategy.MIN_WINGS_FOR_FLIGHT - 1,
    )

    response = strategy.move(params)

    assert response.stamina_change == MovingStrategy.STAMINA_CONSUMPTION_FOR_CRAWL
    assert response.location_change == MovingStrategy.MOVEMENT_DISTANCE_FOR_CRAWL


def test_not_enough_stamina_to_flight() -> None:
    strategy = DefaultMovingStrategy()
    params = MovingStrategyParameters(
        MovingStrategy.MIN_STAMINA_FOR_FLIGHT - 1,
        MovingStrategy.MIN_LEGS_FOR_RUN,
        MovingStrategy.MIN_WINGS_FOR_FLIGHT,
    )

    response = strategy.move(params)

    assert response.stamina_change == MovingStrategy.STAMINA_CONSUMPTION_FOR_RUN
    assert response.location_change == MovingStrategy.MOVEMENT_DISTANCE_FOR_RUN


def test_not_enough_stamina_to_run() -> None:
    strategy = DefaultMovingStrategy()
    params = MovingStrategyParameters(
        MovingStrategy.MIN_STAMINA_FOR_RUN - 1,
        MovingStrategy.MIN_LEGS_FOR_RUN,
        MovingStrategy.MIN_WINGS_FOR_FLIGHT,
    )

    response = strategy.move(params)

    assert response.stamina_change == MovingStrategy.STAMINA_CONSUMPTION_FOR_WALK
    assert response.location_change == MovingStrategy.MOVEMENT_DISTANCE_FOR_WALK


def test_not_enough_stamina_to_walk() -> None:
    strategy = DefaultMovingStrategy()
    params = MovingStrategyParameters(
        MovingStrategy.MIN_STAMINA_FOR_WALK - 1,
        MovingStrategy.MIN_LEGS_FOR_RUN,
        MovingStrategy.MIN_WINGS_FOR_FLIGHT,
    )

    response = strategy.move(params)

    assert response.stamina_change == MovingStrategy.STAMINA_CONSUMPTION_FOR_HOP
    assert response.location_change == MovingStrategy.MOVEMENT_DISTANCE_FOR_HOP


def test_not_enough_stamina_to_hop() -> None:
    strategy = DefaultMovingStrategy()
    params = MovingStrategyParameters(
        MovingStrategy.MIN_STAMINA_FOR_HOP - 1,
        MovingStrategy.MIN_LEGS_FOR_RUN,
        MovingStrategy.MIN_WINGS_FOR_FLIGHT,
    )

    response = strategy.move(params)

    assert response.stamina_change == MovingStrategy.STAMINA_CONSUMPTION_FOR_CRAWL
    assert response.location_change == MovingStrategy.MOVEMENT_DISTANCE_FOR_CRAWL


def test_not_enough_stamina_to_crawl() -> None:
    strategy = DefaultMovingStrategy()
    params = MovingStrategyParameters(
        0, MovingStrategy.MIN_LEGS_FOR_RUN, MovingStrategy.MIN_WINGS_FOR_FLIGHT
    )

    response = strategy.move(params)

    assert response.stamina_change == 0
    assert response.location_change == 0


def test_default_damage() -> None:
    strategy = DefaultAttackingStrategy()
    params = AttackingStrategyParameters(1, 0, 0)

    damage = strategy.calculate_damage(params)

    assert damage == 1


def test_teeth_should_add_3n_damage() -> None:
    strategy = DefaultAttackingStrategy()
    for i in range(3):
        params = AttackingStrategyParameters(1, i, 0)

        damage = strategy.calculate_damage(params)

        assert damage == 1 + i * 3


def test_claws_should_multiply_damage() -> None:
    strategy = DefaultAttackingStrategy()
    for i in range(3):
        params = AttackingStrategyParameters(2, 0, i)

        damage = strategy.calculate_damage(params)

        assert damage == 2 * (1 + i)


def test_claws_and_teeth() -> None:
    strategy = DefaultAttackingStrategy()
    params = AttackingStrategyParameters(1, 1, 1)

    damage = strategy.calculate_damage(params)

    assert damage == (1 + 3 * 1) * 2
