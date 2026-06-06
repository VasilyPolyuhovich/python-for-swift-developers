# Модуль 05. Класи та ООП

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 05**

Туторіал: [§9 Класи](https://docs.python.org/uk/3/tutorial/classes.html).

Класи Python мапляться на Swift `class`, але є кілька принципових різниць:
явний `self`, інша модель приватності, dunder-методи замість протоколів-операторів,
і — головне — **усі екземпляри класів є reference-типами** (як і в Swift, тут
збіг).

**Поглиблені сторінки модуля:**
- [Dunder-методи: повний каталог](05-classes-and-oop/dunder-methods.md) — оператори, контейнери, доступ до атрибутів, конвертації, контекст.
- [Дескриптори, `__slots__`, метакласи, MRO](05-classes-and-oop/descriptors-and-metaclasses.md) — як працює `@property` зсередини, кооперативний `super()`, метапрограмування.

## 1. Базовий клас

### Swift
```swift
class Person {
    let name: String
    var age: Int

    init(name: String, age: Int) {
        self.name = name
        self.age = age
    }

    func greet() -> String {
        "Hi, I'm \(name)"
    }
}
```

### Python
```python
class Person:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"

p = Person("Vasyl", 40)        # без 'new'
print(p.greet())
```

Ключові відмінності:

- `__init__` — конструктор (dunder-метод). Викликається при `Person(...)`.
- **`self` — явний перший параметр кожного методу**. У Swift він неявний.
- Поля не оголошуються окремо — вони з'являються при присвоєнні в `__init__`.
- Немає `new`: екземпляр створюється викликом класу `Person(...)`.

> **⚠️ Пастка №1.** Забути `self.` — найчастіша помилка. `self.name` — поле
> екземпляра; `name` без `self` — локальна змінна методу.

## 2. Атрибути класу vs екземпляра

```python
class Counter:
    instances = 0              # АТРИБУТ КЛАСУ — спільний для всіх (як static у Swift)

    def __init__(self) -> None:
        self.value = 0          # атрибут ЕКЗЕМПЛЯРА — свій у кожного
        Counter.instances += 1
```

```swift
class Counter {
    static var instances = 0     // атрибут типу
    var value = 0                // атрибут екземпляра
}
```

> **⚠️ Пастка №2.** Mutable-атрибут класу (`items = []` на рівні класу) спільний
> для всіх екземплярів — та сама пастка, що з mutable defaults. Mutable-стан клади
> в `self.` всередині `__init__`.

## 3. Properties — обчислювані та контрольовані атрибути

### Swift
```swift
class Circle {
    var radius: Double
    var area: Double { radius * radius * .pi }   // computed
    init(radius: Double) { self.radius = radius }
}
```

### Python
```python
import math

class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius          # _ — конвенція "приватного"

    @property
    def area(self) -> float:            # обчислюваний (read-only)
        return math.pi * self._radius ** 2

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:   # контрольований setter
        if value < 0:
            raise ValueError("radius must be non-negative")
        self._radius = value

c = Circle(5)
c.area            # звертання БЕЗ дужок — як до поля
c.radius = 10     # викликає setter із валідацією
```

`@property` перетворює метод на «обчислюваний атрибут» — аналог computed property
зі Swift. Доступ без дужок: `c.area`, не `c.area()`.

> **Best practice.** Починай із простого публічного атрибута (`self.radius`). Не
> пиши getter/setter «на всяк випадок» — це не Java. Додавай `@property` лише
> коли реально потрібні обчислення чи валідація. Зовнішній код не помітить
> різниці — інтерфейс той самий.

### `@cached_property` — обчислити раз і запам'ятати

Якщо обчислення дороге, а результат не змінюється — `functools.cached_property`
рахує його при першому доступі й кешує в `__dict__` екземпляра (аналог `lazy var`
зі Swift):

```python
from functools import cached_property

class Dataset:
    def __init__(self, rows: list[int]) -> None:
        self.rows = rows

    @cached_property
    def total(self) -> int:
        print("computing...")        # надрукується лише ОДИН раз
        return sum(self.rows)

d = Dataset([1, 2, 3])
d.total      # computing... → 6
d.total      # 6  (без обчислення)
```

> **⚠️ Пастка.** `cached_property` зберігає результат назавжди (поки живий
> екземпляр) — не використовуй для значень, що залежать від мутабельного стану,
> який може змінитися. Як це працює зсередини — [дескриптори](05-classes-and-oop/descriptors-and-metaclasses.md).

## 4. Приватність — конвенції, а не примус

У Python **немає `private`/`public`** як ключових слів. Натомість конвенції:

```python
class Account:
    def __init__(self) -> None:
        self.balance = 0          # публічний
        self._pin = "0000"        # "захищений" — конвенція: не чіпай ззовні
        self.__secret = "x"       # name mangling -> _Account__secret
```

- `name` — публічний.
- `_name` — «внутрішній» за конвенцією. Інструменти й колеги це поважають, але
  технічно доступ є.
- `__name` (два підкреслення) — **name mangling**: перейменовується на
  `_ClassName__name`, щоб уникнути конфліктів у спадкуванні. Це не «справжній
  private», а механізм запобігання колізіям.

> **⚠️ Пастка №3.** Не очікуй захисту рівня Swift `private`. Філософія Python —
> «ми всі тут дорослі» (`_` сигналізує «не варто», а не «не можна»). Якщо тобі
> потрібен жорсткий публічний контракт — покладайся на `_`-конвенцію + `pyright`
> (він попередить про доступ до `_`-членів ззовні в strict-режимі деяких
> конфігурацій) і на дизайн API.

## 5. Dunder-методи — «магічні» методи

Замість протоколів `Equatable`, `Comparable`, `CustomStringConvertible` зі Swift,
Python використовує спеціальні методи з подвійним підкресленням (dunder = double
underscore).

```python
class Money:
    def __init__(self, cents: int) -> None:
        self.cents = cents

    def __repr__(self) -> str:               # для дебагу (як debugDescription)
        return f"Money(cents={self.cents})"

    def __str__(self) -> str:                # для користувача (як description)
        return f"${self.cents / 100:.2f}"

    def __eq__(self, other: object) -> bool: # ~ Equatable
        if not isinstance(other, Money):
            return NotImplemented
        return self.cents == other.cents

    def __lt__(self, other: "Money") -> bool: # ~ Comparable (<)
        return self.cents < other.cents

    def __hash__(self) -> int:               # потрібен для set/dict-ключів
        return hash(self.cents)

    def __add__(self, other: "Money") -> "Money":   # оператор +
        return Money(self.cents + other.cents)
```

| Swift | Python dunder |
|-------|---------------|
| `Equatable` (`==`) | `__eq__` |
| `Comparable` (`<`) | `__lt__` (+ `functools.total_ordering`) |
| `Hashable` | `__hash__` |
| `CustomStringConvertible` | `__str__` |
| `CustomDebugStringConvertible` | `__repr__` |
| `+`, `-`, `*` | `__add__`, `__sub__`, `__mul__` |
| `subscript` | `__getitem__`/`__setitem__` |
| `callable` (`()`) | `__call__` |
| `for-in` (Sequence) | `__iter__` (Модуль 09) |
| context (немає) | `__enter__`/`__exit__` (Модуль 10) |

> **Best practice.** Завжди визначай `__repr__` для своїх класів — це безцінно
> при дебагу й логуванні. `functools.total_ordering` згенерує всі оператори
> порівняння з `__eq__` + `__lt__`. Але для більшості «даних»-класів усе це
> згенерує `@dataclass` автоматично — див. [Модуль 06](06-structs-and-value-types.md).

## 6. Спадкування

### Swift
```swift
class Animal {
    func sound() -> String { "..." }
}
class Dog: Animal {
    override func sound() -> String { "Woof" }
}
```

### Python
```python
class Animal:
    def sound(self) -> str:
        return "..."

class Dog(Animal):                    # успадкування — у дужках
    def sound(self) -> str:           # перевизначення (немає 'override')
        return "Woof"
```

Виклик батьківського методу — через `super()`:

```python
class Puppy(Dog):
    def __init__(self, name: str) -> None:
        super().__init__()            # як super.init() у Swift
        self.name = name

    def sound(self) -> str:
        return super().sound() + "!"
```

> **⚠️ Пастка №4.** Немає ключового слова `override`. Перевизначення відбувається
> неявно простим співпадінням імені. Це означає, що *випадковий* збіг імен мовчки
> перевизначить метод. `pyright` має часткові перевірки; декоратор
> `@typing.override` (3.12+) повертає явність — використовуй його:
> ```python
> from typing import override
>
> class Dog(Animal):
>     @override
>     def sound(self) -> str:
>         return "Woof"
> ```

### Множинне успадкування та MRO

На відміну від Swift (одиночне спадкування + протоколи), Python дозволяє
**множинне спадкування**. Порядок розв'язання методів — MRO (Method Resolution
Order, алгоритм C3):

```python
class A:
    def hi(self) -> str: return "A"
class B(A):
    def hi(self) -> str: return "B"
class C(A):
    def hi(self) -> str: return "C"
class D(B, C):
    pass

D().hi()              # "B"  — за MRO: D, B, C, A
D.__mro__             # подивитись порядок
```

> **⚠️ Пастка №5.** Множинне спадкування потужне, але легко заплутатись. У
> більшості випадків віддавай перевагу композиції та протоколам (Модуль 08), як і
> звик у protocol-oriented Swift. Множинне спадкування доречне переважно для
> mixin-ів.

## 7. Статичні методи та методи класу

```python
class Date:
    def __init__(self, year: int, month: int, day: int) -> None:
        self.year, self.month, self.day = year, month, day

    @classmethod
    def from_string(cls, s: str) -> "Date":      # ~ Swift static factory init
        y, m, d = map(int, s.split("-"))
        return cls(y, m, d)                       # cls — сам клас (підтримує спадкування)

    @staticmethod
    def is_valid_year(year: int) -> bool:         # ~ static func без доступу до типу
        return 1 <= year <= 9999

Date.from_string("2025-01-15")
Date.is_valid_year(2025)
```

- `@classmethod` отримує `cls` (сам клас) — для альтернативних конструкторів.
- `@staticmethod` — звичайна функція в неймспейсі класу, без `self`/`cls`.

## Інструменти та бібліотеки

- **`dataclasses`** (stdlib) — для класів-«даних» генерує `__init__`, `__repr__`,
  `__eq__`. **Майже завжди починай із `@dataclass`**, а не голого класу — Модуль 06.
- **`functools.total_ordering`** — автогенерація операторів порівняння.
- **`abc`** (stdlib) — абстрактні базові класи (Модуль 08).
- **`attrs`** — потужніша альтернатива `dataclasses` (валідатори, конвертери).

## Best practices модуля

- Не забувай `self.`; завжди визначай `__repr__`.
- Публічні атрибути за замовчуванням; `@property` лише за потреби обчислень/валідації.
- Приватність — конвенція (`_name`), не примус. Поважай її, не покладайся на захист.
- `@override` (3.12+) для явності перевизначення.
- Уникай множинного спадкування; обирай композицію + протоколи.
- Для класів-даних — `@dataclass`, не ручні методи.
- `@cached_property` для дорогих незмінних обчислень.

## Див. також

- [Dunder-методи: повний каталог](05-classes-and-oop/dunder-methods.md).
- [Дескриптори, slots, метакласи, MRO](05-classes-and-oop/descriptors-and-metaclasses.md).
- [Модуль 06 — Value-типи](06-structs-and-value-types.md) — `@dataclass`, `NamedTuple`, immutability.
- [Модуль 08 — Протоколи](08-protocols-and-interfaces.md) — ABC, structural typing, mixins.
- [Модуль 09 — Ітератори](09-iterators-and-generators.md) — `__iter__`/`__next__`.
- [Модуль 04 — Типи](04-types-and-typing.md) — `@override`, `ClassVar`, `Final`.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 06 — «Структури» та value-типи](06-structs-and-value-types.md)
