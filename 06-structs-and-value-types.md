# Модуль 06. «Структури» та value-типи

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 06**

У Python **немає `struct`** із value semantics, як у Swift. Це одна з
найважливіших відмінностей. Але є кілька конструкцій, що покривають різні ролі
Swift `struct` та `enum`. Цей модуль — про те, як обрати правильну.

## Карта відповідностей

| Роль зі Swift | Інструмент у Python | Семантика |
|---------------|---------------------|-----------|
| `struct` (дані + методи) | `@dataclass` | reference, але зручно |
| `struct` незмінна | `@dataclass(frozen=True)` | незмінна, hashable |
| легкий immutable record | `NamedTuple` | value-подібна, незмінна |
| `enum` (простий) | `enum.Enum` | перелічення |
| `enum` із associated values | `@dataclass` + `Union` (`X \| Y`) | див. нижче |
| валідована модель (Codable++) | `pydantic.BaseModel` | валідація в рантаймі |

> **⚠️ Головна пастка.** Жоден із цих типів (окрім `NamedTuple` та `frozen`)
> **не дає value-семантики копіювання** при присвоєнні. `b = a` — це спільне
> посилання. Якщо потрібна копія — `copy.replace()` (3.13+), `dataclasses.replace`
> або `copy.deepcopy`.

## 1. dataclass — основний робочий інструмент

### Swift
```swift
struct Point {
    var x: Double
    var y: Double
}
let p = Point(x: 1, y: 2)
```

### Python
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

p = Point(x=1.0, y=2.0)        # автоматичний __init__
print(p)                        # Point(x=1.0, y=2.0) — автоматичний __repr__
p == Point(1.0, 2.0)            # True — автоматичний __eq__
```

`@dataclass` генерує `__init__`, `__repr__`, `__eq__` із оголошених полів. Це
найближче до Swift `struct` за зручністю (але reference за семантикою).

### Значення за замовчуванням і методи

```python
from dataclasses import dataclass, field

@dataclass
class Server:
    host: str
    port: int = 5432                          # default
    tags: list[str] = field(default_factory=list)   # ⚠️ для mutable — factory!

    @property
    def address(self) -> str:                 # методи й property — як завжди
        return f"{self.host}:{self.port}"
```

> **⚠️ Пастка.** Mutable default (`tags: list[str] = []`) заборонено в dataclass —
> отримаєш помилку. Використовуй `field(default_factory=list)`. Це та сама пастка
> mutable defaults, але dataclass захищає тебе явною помилкою.

### `field()` — тонке налаштування полів

`field()` керує тим, як поле бере участь у згенерованих методах:

```python
@dataclass
class User:
    name: str
    id: int = field(compare=False)        # НЕ враховується в __eq__
    token: str = field(repr=False, default="")   # НЕ показується в __repr__
    cache: dict = field(default_factory=dict, compare=False)
    computed: float = field(init=False, default=0.0)   # НЕ в __init__

User("Vasyl", 1) == User("Vasyl", 2)      # True — id виключено з рівності
```

| Параметр `field()` | Призначення |
|--------------------|-------------|
| `default` / `default_factory` | значення/фабрика за замовчуванням |
| `init=False` | поле не входить у `__init__` (заповнюється в `__post_init__`) |
| `repr=False` | приховати з `__repr__` (паролі, токени) |
| `compare=False` | виключити з `__eq__`/порядку (службові id, кеш) |
| `hash=...` | контроль участі в `__hash__` |
| `kw_only=True` | зробити це поле keyword-only |

### `__post_init__` та `InitVar`

`__post_init__` виконується одразу після згенерованого `__init__` — для валідації
чи похідних полів. `InitVar` — параметр, що передається в `__post_init__`, але
**не зберігається** як поле:

```python
from dataclasses import dataclass, field, InitVar

@dataclass
class Account:
    balance: float
    discount: InitVar[float] = 0.0            # лише для ініціалізації
    net: float = field(init=False, default=0.0)

    def __post_init__(self, discount: float) -> None:
        if self.balance < 0:
            raise ValueError("balance must be non-negative")   # валідація
        self.net = self.balance * (1 - discount)              # похідне поле

a = Account(100.0, discount=0.1)
a.net            # 90.0
```

> **⚠️ Пастка.** `dataclasses.replace(a, balance=200)` НЕ передасть `InitVar`
> (його значення вже «втрачене»), тож `discount` візьме дефолт `0.0`, і `net`
> перерахується як `200.0`, а не з урахуванням знижки. `InitVar` + `replace` —
> тонке місце; для незмінних обчислюваних полів продумай це заздалегідь.

### Frozen dataclass — незмінна «структура»

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
# p.x = 5            # ПОМИЛКА: frozen — як let-поля у Swift struct
hash(p)             # frozen => hashable => можна як ключ dict/set

# "Зміна" = створення нового (як у Swift зі struct + var copy)
from dataclasses import replace
p2 = replace(p, x=10.0)        # новий Point(10.0, 2.0)
```

> **Best practice.** Для типів-значень (координати, гроші, конфіги) використовуй
> `frozen=True`. Це повертає тобі звичну зі Swift незмінність і безпечність, плюс
> hashability. Для «передати й не мутувати» — найкращий вибір.

Корисні опції:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class Config:
    host: str
    port: int
```

- `slots=True` — економія пам'яті + заборона випадкових атрибутів (швидше).
- `kw_only=True` — усі поля лише як keyword (самодокументовані виклики).

### Копіювання: `replace` vs `copy` vs `deepcopy`

Оскільки dataclass — reference-тип, «зміна незмінного» = створення нового. Маєш
три інструменти з різною семантикою:

```python
import copy
from dataclasses import replace

p = Point(1.0, 2.0)

replace(p, x=10.0)        # новий Point(10.0, 2.0) — змінити поля (як var-копія Swift)
copy.replace(p, x=10.0)   # те саме, але універсальний протокол __replace__ (3.13+)
copy.copy(p)              # ПОВЕРХНЕВА копія — вкладені list/dict СПІЛЬНІ!
copy.deepcopy(p)          # ГЛИБОКА копія — усе незалежне
```

> **⚠️ Пастка.** `copy.copy` копіює лише верхній рівень: якщо поле — це `list`,
> копія й оригінал ділять той самий список. Для повної незалежності вкладених
> структур потрібен `deepcopy` (повільніше). Для «змінити кілька полів незмінного
> об'єкта» — `replace`/`copy.replace`, а не ручне копіювання. Деталі семантики —
> [Модуль 03 · list](03-data-structures/list.md).

## 2. NamedTuple — легкий незмінний record

```python
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float

p = Point(1.0, 2.0)
p.x                 # 1.0  (доступ за іменем)
p[0]                # 1.0  (і за індексом — це ж кортеж)
x, y = p            # розпакування
# p.x = 5           # ПОМИЛКА: незмінний
```

`NamedTuple` — це `tuple` з іменами полів. **Справді value-подібний**: незмінний,
hashable, порівнюється за значенням, розпаковується.

| | `NamedTuple` | `frozen dataclass` |
|--|-------------|---------------------|
| Незмінність | завжди | через `frozen=True` |
| Доступ за індексом | так | ні |
| Методи/property | обмежено | повноцінно |
| Defaults | так | так |
| Найкраще для | прості record, повернення кількох значень | повноцінні моделі |

> **Best practice.** `NamedTuple` — для дрібних незмінних record-ів (повернути
> `(min, max)` з іменами). `frozen dataclass` — коли потрібні методи, валідація,
> складніша поведінка.

## 3. Enum — перелічення

### Swift
```swift
enum Direction {
    case north, south, east, west
}
```

### Python
```python
from enum import Enum

class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

d = Direction.NORTH
d.value             # "north"
d.name              # "NORTH"
Direction("north")  # Direction.NORTH (з value)
list(Direction)     # ітерація по всіх варіантах
```

Варіації:

```python
from enum import IntEnum, StrEnum, auto

class Priority(IntEnum):        # поводиться як int
    LOW = 1
    HIGH = 2

class Color(StrEnum):           # поводиться як str (3.11+)
    RED = "red"
    GREEN = "green"

class Suit(Enum):
    HEARTS = auto()             # auto() — автонумерація
    SPADES = auto()
```

### `Flag`/`IntFlag` — бітові набори (OptionSet зі Swift)

Коли потрібен **набір** прапорців (комбінувати через `|`) — аналог Swift
`OptionSet`:

```python
from enum import Flag, auto

class Perm(Flag):
    READ = auto()
    WRITE = auto()
    EXEC = auto()

p = Perm.READ | Perm.WRITE      # комбінація
Perm.READ in p                  # True   — перевірка членства
Perm.EXEC in p                  # False
list(p)                         # [Perm.READ, Perm.WRITE]
```

`IntEnum`/`IntFlag` додатково поводяться як `int` (для сумісності з C-API,
бітовими масками протоколів). `StrEnum` — як `str` (зручно для JSON/БД).

> **⚠️ Пастка.** `IntEnum`/`StrEnum` «розчиняються» у `int`/`str`: `Priority.LOW
> == 1` → `True`, і вони пройдуть туди, де очікують число/рядок. Це зручно для
> інтеропу, але втрачає сувору типобезпеку — для чистих перелічень бери звичайний
> `Enum`.

Матчинг (вичерпність перевіряє pyright):

```python
def describe(d: Direction) -> str:
    match d:
        case Direction.NORTH: return "up"
        case Direction.SOUTH: return "down"
        case Direction.EAST:  return "right"
        case Direction.WEST:  return "left"
```

## 4. Enum з associated values — найбільший контраст зі Swift

У Swift `enum` може нести різні дані в кожному case:

```swift
enum Shape {
    case circle(radius: Double)
    case rectangle(width: Double, height: Double)
}
```

У Python **enum так не вміє**. Ідіоматичний еквівалент — набір dataclass-ів,
об'єднаних `Union`, із розбором через `match`:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Circle:
    radius: float

@dataclass(frozen=True)
class Rectangle:
    width: float
    height: float

type Shape = Circle | Rectangle      # "sum type" через Union

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius=r):
            return 3.14159 * r * r
        case Rectangle(width=w, height=h):
            return w * h
        # pyright попередить, якщо забув варіант (exhaustiveness)
```

> **⚠️ Пастка.** Це найважливіший «переклад» зі Swift. Algebraic data types
> (enum з даними) у Python = `Union` із dataclass-ів + `match`. `pyright` уміє
> перевіряти вичерпність такого матчингу (через `assert_never`):
> ```python
> from typing import assert_never
> def area(shape: Shape) -> float:
>     match shape:
>         case Circle(radius=r): return 3.14159 * r * r
>         case Rectangle(width=w, height=h): return w * h
>         case _: assert_never(shape)   # pyright: помилка, якщо є непокритий варіант
> ```

## 5. pydantic — модель із валідацією (Codable++)

Коли дані приходять ззовні (JSON API, конфіги, форми), потрібна валідація в
рантаймі — те, чого dataclass не робить:

```python
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    id: int
    name: str = Field(min_length=1)
    email: EmailStr
    age: int = Field(ge=0, le=150)

# Парсинг + валідація + конвертація типів (схоже на Codable, але суворіше)
user = User.model_validate_json('{"id": 1, "name": "Vasyl", '
                                '"email": "v@example.com", "age": 40}')
user.model_dump_json()        # серіалізація назад
```

> **Best practice.** Межа застосувань:
> - `@dataclass` — внутрішні дані твоєї програми (довіряєш джерелу).
> - `pydantic.BaseModel` — будь-що з-за меж програми (API, файли, ввід користувача).
>
> `pydantic` — фактичний стандарт для API (його використовує FastAPI, Модуль 13).

## 6. Серіалізація та успадкування dataclass

### У dict/tuple і назад

```python
from dataclasses import dataclass, asdict, astuple
import json

@dataclass
class Point:
    x: int
    y: int

p = Point(1, 2)
asdict(p)                       # {'x': 1, 'y': 2}   (рекурсивно для вкладених)
astuple(p)                      # (1, 2)
json.dumps(asdict(p))           # '{"x": 1, "y": 2}'
Point(**json.loads('{"x": 1, "y": 2}'))    # Point(x=1, y=2)  — назад
```

> **⚠️ Пастка.** `asdict` рекурсивно перетворює вкладені dataclass-и, але не знає
> про власні типи (`datetime`, `Decimal`) — `json.dumps` на них спіткнеться.
> Для надійної (де)серіалізації складних моделей бери `pydantic` (нижче) — він
> має `model_dump`/`model_validate` з підтримкою таких типів.

Для бінарної серіалізації між Python-процесами — `pickle` (працює з dataclass
«з коробки»), але **ніколи** не розпаковуй `pickle` з ненадійного джерела
([Модуль 13](13-stdlib-and-ecosystem.md)).

### Успадкування і `order`

```python
from dataclasses import dataclass

@dataclass(order=True)              # генерує <, <=, >, >= (порівняння за полями)
class Version:
    major: int
    minor: int

sorted([Version(1, 2), Version(1, 0)])    # [Version(1,0), Version(1,2)]

@dataclass
class Base:
    a: int
@dataclass
class Child(Base):                  # успадкування полів
    b: int = 0

Child(1, 2)                         # Child(a=1, b=2)
```

> **⚠️ Пастка.** Поля без дефолту не можуть іти після полів із дефолтом (включно
> через успадкування) — інакше `TypeError`. Якщо база має поле з дефолтом, усі
> нові поля нащадка теж потребують дефолтів (або `kw_only=True`, що знімає це
> обмеження).

## Як обрати — дерево рішень

```
Дані приходять ззовні й треба валідація? ── так ──> pydantic.BaseModel
                  │ ні
Потрібна незмінність + методи?            ── так ──> @dataclass(frozen=True)
                  │ ні
Дрібний незмінний record / повернути кілька значень? ─ так ─> NamedTuple
                  │ ні
Фіксований набір варіантів без даних?     ── так ──> Enum
                  │ ні
Варіанти з різними даними (Swift enum)?   ── так ──> Union dataclass-ів + match
                  │ ні
Звичайні дані з поведінкою                ───────> @dataclass
```

## Best practices модуля

- За замовчуванням для класів-даних — `@dataclass`; для незмінних — `frozen=True`.
- Mutable-поля dataclass — лише через `field(default_factory=...)`.
- `NamedTuple` для дрібних незмінних record-ів.
- Swift enum із associated values → `Union` dataclass-ів + `match` + `assert_never`.
- Будь-які зовнішні дані → `pydantic`.
- Пам'ятай: усе це reference; копіюй через `replace`/`deepcopy` свідомо.
- `field(compare=False/repr=False/init=False)` для службових полів.
- `__post_init__` для валідації; `Flag`/`IntFlag` для наборів прапорців.

## Див. також

- [Модуль 01 · match](01-syntax-and-control-flow/match.md) — розбір ADT і `assert_never`.
- [Модуль 03 · list/conversions](03-data-structures/list.md) — copy/deepcopy, reference-семантика.
- [Модуль 04 — Типи](04-types-and-typing.md) — `assert_never`, `TypedDict`, `pydantic`.
- [Модуль 05 — Класи](05-classes-and-oop.md) — `__eq__`/`__hash__`/`__lt__`, `total_ordering`.
- [Модуль 13 — Stdlib](13-stdlib-and-ecosystem.md) — `json`, `pickle`, `decimal`.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 07 — Дженеріки](07-generics.md)
