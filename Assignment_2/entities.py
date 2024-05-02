from __future__ import annotations

from dataclasses import dataclass, field
from math import isqrt
from typing import List, Protocol


class DiscountStrategy(Protocol):
    def applyDiscount(self, price: float) -> float:
        pass


@dataclass
class NoDiscount(DiscountStrategy):
    def applyDiscount(self, price: float) -> float:
        return price


@dataclass
class PercentageDiscountStrategy(DiscountStrategy):
    percentage: float = 0.0

    def applyDiscount(self, price: float) -> float:
        return price * (1 - self.percentage)


@dataclass
class ReceiptDiscountStrategy(DiscountStrategy):
    customer_id: int
    percentage: float = 0.1

    def isPrime(self, n: int) -> bool:
        if n <= 1:
            return False
        for i in range(2, isqrt(n) + 1):
            if n % i == 0:
                return False
        return True

    def applyDiscount(self, price: float) -> float:
        if self.isPrime(self.customer_id):
            return price * (1 - self.percentage)
        else:
            return price


class Sellable(Protocol):
    def getId(self) -> int:
        ...

    def getName(self) -> str:
        ...

    def getPrice(self) -> float:
        ...

    def setDiscountStrategy(self, discount_strategy: DiscountStrategy) -> None:
        ...

    def getDiscountStrategy(self) -> DiscountStrategy:
        ...


@dataclass
class NoSellable:
    def getId(self) -> int:
        return -1

    def getName(self) -> str:
        return "no name"

    def getPrice(self) -> float:
        return 0

    def setDiscountStrategy(self, discount_strategy: DiscountStrategy) -> None:
        pass

    def getDiscountStrategy(self) -> DiscountStrategy:
        return NoDiscount()


@dataclass
class Item(Sellable):
    id: int
    name: str
    price: float
    discount_strategy: DiscountStrategy = field(default_factory=NoDiscount)

    def getId(self) -> int:
        return self.id

    def getName(self) -> str:
        return self.name

    def getPrice(self) -> float:
        return self.discount_strategy.applyDiscount(self.price)

    def setDiscountStrategy(self, discount_strategy: "DiscountStrategy") -> None:
        self.discount_strategy = discount_strategy

    def getDiscountStrategy(self) -> "DiscountStrategy":
        return self.discount_strategy


@dataclass
class ItemPack(Sellable):
    id: int
    sellables: List[Sellable] = field(default_factory=list)
    discount_strategy: DiscountStrategy = field(default_factory=NoDiscount)

    def getId(self) -> int:
        return self.id

    def getName(self) -> str:
        return self.sellables[0].getName() + " " + str(len(self.sellables)) + " pack"

    def getPrice(self) -> float:
        for sellable in self.sellables:
            sellable.setDiscountStrategy(NoDiscount())
        return sum(
            self.discount_strategy.applyDiscount(sellable.getPrice())
            for sellable in self.sellables
        )

    def setDiscountStrategy(self, discount_strategy: DiscountStrategy) -> None:
        self.discount_strategy = discount_strategy

    def getDiscountStrategy(self) -> DiscountStrategy:
        return self.discount_strategy


@dataclass
class Batch(Sellable):
    id: int
    amount: int
    item_type: Item
    discount_strategy: DiscountStrategy = field(default_factory=NoDiscount)

    def getId(self) -> int:
        return self.id

    def getName(self) -> str:
        return self.item_type.getName() + " " + str(self.amount) + " pack"

    def getPrice(self) -> float:
        self.item_type.setDiscountStrategy(self.discount_strategy)
        return self.amount * self.item_type.getPrice()

    def setDiscountStrategy(self, discount_strategy: DiscountStrategy) -> None:
        self.discount_strategy = discount_strategy

    def getDiscountStrategy(self) -> DiscountStrategy:
        return self.discount_strategy

    def getAmount(self) -> int:
        return self.amount

    def getItem(self) -> Item:
        return self.item_type

# implementing composite pattern


@dataclass
class Receipt(Sellable):
    id: int
    payment_method: str = ""
    # customer_number: int
    sellables: List[Sellable] = field(default_factory=list)
    discount_strategy: DiscountStrategy = field(default_factory=NoDiscount)

    def getId(self) -> int:
        return self.id

    def getName(self) -> str:
        return "Receipt " + str(self.id)

    def getPrice(self) -> float:
        price = sum(sellable.getPrice() for sellable in self.sellables)
        return self.discount_strategy.applyDiscount(price)

    def setDiscountStrategy(self, discount_strategy: DiscountStrategy) -> None:
        self.discount_strategy = discount_strategy

    def getDiscountStrategy(self) -> DiscountStrategy:
        return self.discount_strategy

    def addSellable(self, sellable: Sellable) -> None:
        self.sellables.append(sellable)

    def removeSellable(self, sellable: Sellable) -> None:
        if sellable in self.sellables:
            self.sellables.remove(sellable)

    def get_payment_method(self) -> str:
        return self.payment_method


@dataclass
class NoReceipt(Receipt):
    id: int = -1
    payment_method = ""
    sellables: List[Sellable] = field(default_factory=list)

    def getId(self) -> int:
        return self.id

    def getName(self) -> str:
        return "No Receipt Name"

    def getPrice(self) -> float:
        return 0

    def setDiscountStrategy(self, discount_strategy: DiscountStrategy) -> None:
        pass

    def getDiscountStrategy(self) -> DiscountStrategy:
        return NoDiscount()

    def addSellable(self, sellable: Sellable) -> None:
        pass

    def removeSellable(self, sellable: Sellable) -> None:
        pass

    def get_payment_method(self) -> str:
        return ""


@dataclass
class ReceiptBuilder:
    id: int = 0
    payment_method: str = ""
    sellables: List[Sellable] = field(default_factory=list)
    discount_strategy: DiscountStrategy = field(default_factory=NoDiscount)

    def with_id(self, id: int) -> ReceiptBuilder:
        self.id = id
        return self

    def with_sellable(self, sellable: Sellable) -> ReceiptBuilder:
        self.sellables.append(sellable)
        return self

    def with_payment_method(self, payment_method: str) -> ReceiptBuilder:
        self.payment_method = payment_method
        return self

    def with_discount_strategy(
        self, discount_strategy: DiscountStrategy
    ) -> ReceiptBuilder:
        self.discount_strategy = discount_strategy
        return self

    def build(self) -> Receipt:
        return Receipt(
            self.id,
            self.payment_method,
            sellables=self.sellables,
            discount_strategy=self.discount_strategy,
        )


class Discount(Protocol):
    def getId(self) -> int:
        pass

    def getItemId(self) -> int:
        pass

    def getValue(self) -> float:
        pass


@dataclass
class PercentageDiscount(Discount):
    id: int
    item_id: int
    percentage: float

    def getId(self) -> int:
        return self.id

    def getItemId(self) -> int:
        return self.item_id

    def getValue(self) -> float:
        return self.percentage
