# Модуль 04. Складні типи та система типів

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 04**

Цей модуль — про те, як повернути собі типобезпеку, до якої ти звик у Swift.
Python динамічно типізований, але має повноцінну систему **анотацій типів**
([PEP 484](https://peps.python.org/pep-0484/) і наступники), яку перевіряють
статичні аналізатори (`pyright`, `mypy`). Анотації не впливають на рантайм — це
суто «компайл-тайм» контракт, як у Swift.

## 1. Базові анотації

```python
name: str = "Vasyl"
age: int = 40
height: float = 1.80
active: bool = True
data: bytes = b"raw"
```

Колекції (сучасний синтаксис, 3.9+ — нижній регістр, без `typing.List`):

```python
ids: list[int]
mapping: dict[str, int]
coords: tuple[float, float]
unique: set[str]
```

## 2. Optional — `X | None`

### Swift
```swift
var middleName: String?           // Optional<String>
let name = middleName ?? "N/A"    // nil-coalescing
if let mn = middleName { ... }     // unwrap
```

### Python
```python
middle_name: str | None = None        # сучасний синтаксис (3.10+)
# еквівалент: Optional[str] зі старого typing

name = middle_name or "N/A"           # ~ nil-coalescing (обережно з truthiness!)
name = middle_name if middle_name is not None else "N/A"   # точніше

if middle_name is not None:           # "unwrap"
    print(middle_name.upper())        # pyright знає: тут str, не None
```

> **⚠️ Пастка №1.** У Python **немає примусу розгортати Optional**, як у Swift.
> `middle_name.upper()` без перевірки скомпілюється і впаде в рантаймі з
> `AttributeError`, якщо там `None`. Захист дає лише `pyright`: він позначить
> такий доступ помилкою. Тому strict-режим критичний.

> **⚠️ Пастка №2.** `x or default` спрацює не лише для `None`, а й для будь-якого
> falsy-значення (`0`, `""`, `[]`). Якщо `0` — валідне значення, використовуй
> явне `x if x is not None else default`.

### Narrowing (звуження типу)

`pyright` робить type narrowing аналогічно до Swift `if let`:

```python
def process(value: int | str | None) -> str:
    if value is None:
        return "empty"
    if isinstance(value, int):
        return str(value * 2)      # тут value звужено до int
    return value.upper()           # тут value звужено до str
```

## 3. Union — кілька можливих типів

```python
def parse(raw: str) -> int | float:
    return float(raw) if "." in raw else int(raw)
```

`int | str` ≈ Swift enum із двома case, але без обгортки. Для розбору —
`isinstance` або `match` (Модуль 01).

## 4. Type alias

### Swift
```swift
typealias UserID = Int
typealias JSON = [String: Any]
```

### Python (3.12+, PEP 695)
```python
type UserID = int
type Json = dict[str, "Json"] | list["Json"] | str | int | float | bool | None
```

До 3.12:
```python
from typing import TypeAlias
UserID: TypeAlias = int
```

## 5. Literal — конкретні значення як тип

Аналог обмеженого набору, схожий на Swift enum, але на рівні літералів:

```python
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    ...

set_mode("read")        # OK
set_mode("delete")      # pyright: ПОМИЛКА — не входить у Literal
```

Для справжніх перелічень частіше беруть `enum.Enum` (Модуль 06), але `Literal`
зручний для рядкових прапорців API.

## 6. TypedDict — типізований словник

Коли працюєш із JSON-подібними структурами і не хочеш повноцінний клас:

```python
from typing import TypedDict

class User(TypedDict):
    id: int
    name: str
    email: str | None

u: User = {"id": 1, "name": "Vasyl", "email": None}
u["name"]        # pyright знає, що це str
```

Це найближче до анонімних структур JSON. Але для валідації даних із зовнішнього
світу краще `pydantic` (див. нижче й Модуль 06).

## 7. NewType — номінальні обгортки

Як у Swift, де `typealias UserID = Int` *не* створює окремий тип, а тобі хочеться
розрізняти `UserID` і `ProductID`:

```python
from typing import NewType

UserID = NewType("UserID", int)
ProductID = NewType("ProductID", int)

def get_user(uid: UserID) -> None: ...

uid = UserID(42)
get_user(uid)        # OK
get_user(42)         # pyright: ПОМИЛКА — звичайний int ≠ UserID
```

Це дає номінальну типобезпеку понад структурною, чого у Swift досягають
окремими типами.

## 8. Callable, Iterable та інші протоколи типів

З `collections.abc` (не зі старого `typing`):

```python
from collections.abc import Callable, Iterable, Iterator, Sequence, Mapping

handler: Callable[[int, str], bool]      # (Int, String) -> Bool
items: Sequence[int]                     # будь-що індексоване й раховане
config: Mapping[str, int]                # read-only dict-подібне
```

> **Best practice.** Приймай *найзагальніший* тип на вході (`Iterable`,
> `Sequence`, `Mapping`), повертай *конкретний* (`list`, `dict`). Це принцип
> «liberal in, conservative out» — аналог приймання `some Sequence` у Swift.

## 9. Any vs object — два «будь-що»

```python
from typing import Any

x: Any = get_data()       # ВИМИКАЄ перевірку типів — використовуй рідко
y: object = get_data()    # базовий тип, але перевірка ЛИШАЄТЬСЯ
```

> **⚠️ Пастка.** `Any` — це «вимкнути типізацію тут». Зловживання `Any` зводить
> нанівець `pyright`. Уникай; якщо треба «щось», бери `object` і звужуй через
> `isinstance`. У Swift найближчий «втеча» — `Any`, але там його теж не люблять.

## 10. Звуження типів: `assert_never`, `cast`, `TypeGuard`

`pyright` звужує типи через `isinstance`, `is None`, `==` з `Literal` тощо
(розділ 2). Коли цього мало — є явні інструменти.

### `assert_never` — статична вичерпність (як у Swift switch)

Це твій спосіб отримати «компілятор змусить покрити всі case». Якщо додаси новий
варіант в `Union`/`enum` і забудеш гілку — `pyright` помилиться **до запуску**:

```python
from typing import assert_never, Literal

def handle(cmd: Literal["start", "stop"]) -> str:
    match cmd:
        case "start": return "▶"
        case "stop":  return "⏹"
        case _:
            assert_never(cmd)   # pyright: error, якщо з'явиться новий Literal
```

У рантаймі `assert_never` кидає `AssertionError` — подвійний захист. Деталі
застосування з ADT — [Модуль 06](06-structs-and-value-types.md).

### `cast` — «повір мені» для типів

`cast(T, x)` каже аналізатору «вважай це `T`», **нічого не роблячи в рантаймі**:

```python
from typing import cast

raw: object = load_json()
config = cast(dict[str, int], raw)    # у рантаймі raw НЕ перевіряється і НЕ змінюється
```

> **⚠️ Пастка.** `cast` — обіцянка, яку компілятор не перевіряє (як `as!` у Swift,
> але навіть без рантайм-перевірки). Якщо збрехав — отримаєш помилку пізніше.
> Уникай; справжню перевірку дає `isinstance` або `pydantic`.

### `TypeGuard` / `TypeIs` — власні функції-звужувачі

Коли логіка перевірки складна, винеси її у функцію, що **звужує тип** для
аналізатора ([PEP 742](https://peps.python.org/pep-0742/), `TypeIs` — 3.13+):

```python
from typing import TypeIs

def is_str_list(val: list[object]) -> TypeIs[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(items: list[object]) -> None:
    if is_str_list(items):
        # тут pyright знає: items — це list[str]
        print(" ".join(items))
```

## 11. `@overload` — перевантаження сигнатур

Python не має перевантаження функцій (друге `def` перекриває перше). Але для
типів можна оголосити кілька сигнатур через `@overload` — корисно, коли тип
результату залежить від типу аргументу:

```python
from typing import overload

@overload
def parse(x: int) -> str: ...
@overload
def parse(x: str) -> int: ...
def parse(x: int | str) -> str | int:      # ← єдина РЕАЛІЗАЦІЯ
    return str(x) if isinstance(x, int) else int(x)

reveal = parse(5)      # pyright: тип str
reveal2 = parse("7")   # pyright: тип int
```

> Стуби `@overload` існують лише для аналізатора; у рантаймі викликається тільки
> остання (нестаба) реалізація. Для диспетчеризації за типом у рантаймі —
> `functools.singledispatch` ([декоратори](02-functions/decorators.md)).

## 12. `Final`, `ClassVar`, `Annotated`

```python
from typing import Final, ClassVar, Annotated

MAX_RETRIES: Final = 3            # pyright заборонить переприсвоєння (≈ Swift let)
MAX_RETRIES = 5                   # pyright: error

class Config:
    instances: ClassVar[int] = 0  # атрибут КЛАСУ, не екземпляра (Модуль 05)
    name: str                     # атрибут екземпляра

# Annotated — додати метадані до типу (їх читають pydantic, FastAPI тощо)
UserId = Annotated[int, "primary key"]
from pydantic import Field
Age = Annotated[int, Field(ge=0, le=150)]
```

`Final` — найближче до `let`/`static let` у Swift (на рівні аналізатора, не
рантайму — згадай, що справжніх констант немає, [Модуль 01](01-syntax-and-control-flow.md)).

## 13. `@override` — безпечне перевизначення

[PEP 698](https://peps.python.org/pep-0698/) (3.12+) повертає Swift-овий
`override`: позначай перевизначені методи, і `pyright` помилиться, якщо в
батьку такого методу немає (захист від одруків):

```python
from typing import override

class Base:
    def handle(self) -> None: ...

class Child(Base):
    @override
    def handle(self) -> None: ...     # OK
    @override
    def hanlde(self) -> None: ...     # pyright: error — у Base немає 'hanlde'
```

Детальніше про класи — [Модуль 05](05-classes-and-oop.md).

## 14. Runtime-інтроспекція анотацій

Анотації доступні в рантаймі (на відміну від Swift, де типи стерті). На цьому
стоять `pydantic`, `dataclasses`, FastAPI:

```python
from typing import get_type_hints

def f(a: int, b: "str") -> bool: ...

f.__annotations__       # {'a': int, 'b': 'str', 'return': bool}  — сирі, як написано
get_type_hints(f)       # {'a': int, 'b': <class 'str'>, ...}     — резолвить рядки/forward-refs
```

> **⚠️ Пастка.** `__annotations__` зберігає анотації **як написано** (forward-ref
> `"str"` лишається рядком). Щоб отримати справжні об'єкти-типи — `get_type_hints`.

## 15. Generics та Protocol — короткий анонс

Дженеріки (`class Stack[T]`, `TypeVar`, `ParamSpec`, варіантність) — окремий
[Модуль 07](07-generics.md). Протоколи (structural typing, аналог Swift
protocols) — [Модуль 08](08-protocols-and-interfaces.md). `Self`-тип теж там.

## Інструменти та бібліотеки

- **`pyright`** — рекомендований type checker (швидкий, точний, рушій Pylance у
  VS Code). Альтернатива — **`mypy`** (еталонна реалізація).
  ```bash
  uv run pyright
  ```
- **`pydantic`** — валідація даних у рантаймі на основі анотацій типів. Те, чого
  немає в чистих анотаціях: реальна перевірка вхідних даних (JSON, форми, конфіги).
  ```python
  from pydantic import BaseModel

  class User(BaseModel):
      id: int
      name: str
      email: str | None = None

  # Валідує і конвертує в рантаймі — кине помилку, якщо дані не підходять
  user = User.model_validate({"id": "1", "name": "Vasyl"})  # "1" -> 1
  ```
  Це аналог `Codable` зі Swift, але з валідацією та зрозумілими помилками.
- **`typing_extensions`** — нові можливості системи типів до того, як вони
  потраплять у стабільний `typing`.

## Best practices модуля

- Анотуй усе; тримай `pyright` у `strict`. Це твоя заміна компілятору Swift.
- `X | None` замість старого `Optional[X]`; `list[int]` замість `List[int]`.
- Перевіряй `None` через `is`/`is not`, дай `pyright` зробити narrowing.
- `Literal` для рядкових прапорців, `enum` для справжніх перелічень.
- `NewType` для номінального розрізнення «однакових» примітивів.
- `pydantic` для будь-яких даних із зовнішнього світу.
- Уникай `Any`; бери `object` + `isinstance`, коли тип невідомий.
- `assert_never` для вичерпності; `@override` проти одруків; `Final` для констант.
- `cast` — крайній засіб; надавай перевагу `isinstance`/`TypeIs`/`pydantic`.

## Див. також

- [Модуль 01 · match](01-syntax-and-control-flow/match.md) — `assert_never`, патерни.
- [Модуль 05 — Класи](05-classes-and-oop.md) — `@override`, `ClassVar`, `@property`.
- [Модуль 06 — Value-типи](06-structs-and-value-types.md) — `pydantic`, ADT, `TypedDict` vs dataclass.
- [Модуль 07 — Дженеріки](07-generics.md) — `TypeVar`, `ParamSpec`, `Self`, варіантність.
- [Модуль 08 — Протоколи](08-protocols-and-interfaces.md) — structural typing.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 05 — Класи та ООП](05-classes-and-oop.md)
