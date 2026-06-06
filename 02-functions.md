# Модуль 02. Функції

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 02**

Туторіал: [§4.8–4.10](https://docs.python.org/uk/3/tutorial/controlflow.html#defining-functions).

**Поглиблені сторінки модуля:**
- [Декоратори](02-functions/decorators.md) — обгортки, `@wraps`, параметризовані, `ParamSpec`, `singledispatch`.

## 1. Базове оголошення

### Swift
```swift
func add(_ a: Int, _ b: Int) -> Int {
    return a + b
}
```

### Python
```python
def add(a: int, b: int) -> int:
    return a + b
```

- `def` замість `func`.
- Анотації типів через `:` для параметрів і `->` для результату.
- Анотації **опціональні для інтерпретатора**, але обов'язкові за нашими best
  practices (їх перевіряє `pyright`).

> **⚠️ Пастка.** Без анотацій Python не скаржиться: `def add(a, b): return a + b`
> прийме будь-що. Типобезпеку дає лише статичний аналізатор. Тому: **анотуй
> завжди**.

## 2. Аргументи: positional, keyword, defaults

Це найбільша концептуальна різниця зі Swift у роботі з функціями.

### Значення за замовчуванням

```python
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}"

greet("Vasyl")                 # 'Hello, Vasyl'
greet("Vasyl", "Hi")           # 'Hi, Vasyl'
```

### Keyword arguments

Будь-який параметр можна передати **за іменем**, у будь-якому порядку:

```python
greet(greeting="Hi", name="Vasyl")
```

Це нагадує argument labels у Swift, але є фундаментальна різниця:

| | Swift | Python |
|--|-------|--------|
| Імена аргументів | частина сигнатури (label), обов'язкові за замовч. | будь-який параметр можна передати позиційно АБО за іменем |
| Контроль | `_` прибирає label | `/` і `*` явно розділяють (див. нижче) |

### Positional-only та keyword-only параметри

Python дає тонкий контроль через роздільники `/` і `*`:

```python
def f(pos_only, /, normal, *, kw_only):
    ...
#       ^до /        ^між    ^після *
# pos_only — ТІЛЬКИ позиційно
# normal   — і так, і так
# kw_only  — ТІЛЬКИ за іменем
```

```python
def connect(host: str, /, *, port: int = 5432, timeout: float = 30.0) -> None:
    ...

connect("localhost", port=5432)        # OK
connect("localhost", 5432)             # ПОМИЛКА: port — keyword-only
connect(host="localhost")              # ПОМИЛКА: host — positional-only
```

> **Best practice.** Робіть «опційні» налаштування `*`-keyword-only — це робить
> виклики самодокументованими (`port=5432` замість загадкового `5432`), як
> argument labels у Swift.

## 3. ⚠️ Mutable default arguments — головна пастка Python

Це класична помилка, на якій спотикаються всі. Запам'ятай раз і назавжди.

```python
# НЕПРАВИЛЬНО — НІКОЛИ так не роби
def append_item(item: int, target: list[int] = []) -> list[int]:
    target.append(item)
    return target

append_item(1)    # [1]
append_item(2)    # [1, 2]  — СЮРПРИЗ! той самий список
```

Default-значення обчислюється **один раз при оголошенні функції**, а не при
кожному виклику. Тому `[]` — це один спільний об'єкт на всі виклики.

```python
# ПРАВИЛЬНО — sentinel-патерн
def append_item(item: int, target: list[int] | None = None) -> list[int]:
    if target is None:
        target = []
    target.append(item)
    return target
```

У Swift цієї проблеми немає, бо default-вирази обчислюються при виклику, а масиви
мають value semantics.

> `ruff` із правилом `B006` ловить цю помилку автоматично — ще одна причина
> тримати лінтер увімкненим.

## 4. *args і **kwargs (variadic)

### Swift
```swift
func sum(_ numbers: Int...) -> Int {
    numbers.reduce(0, +)
}
```

### Python
```python
def total(*numbers: int) -> int:        # *args — кортеж позиційних
    return sum(numbers)

total(1, 2, 3)        # 6
```

`**kwargs` збирає іменовані аргументи у словник — аналога в Swift немає:

```python
def configure(**options: str) -> None:
    for key, value in options.items():
        print(f"{key} = {value}")

configure(host="localhost", mode="fast")
```

Розпакування (spread) при виклику:

```python
args = [1, 2, 3]
total(*args)                          # розпакувати список у позиційні

opts = {"host": "localhost"}
configure(**opts)                     # розпакувати словник у keyword
```

## 5. Кілька значень — кортежі замість tuple-типу

```python
def min_max(nums: list[int]) -> tuple[int, int]:
    return min(nums), max(nums)

low, high = min_max([3, 1, 4, 1, 5])   # розпакування
```

```swift
func minMax(_ nums: [Int]) -> (min: Int, max: Int) { ... }
let (low, high) = minMax([3, 1, 4])
```

> **Примітка.** У Swift кортежі можуть мати іменовані поля. У Python звичайний
> `tuple` — лише позиційний. Якщо потрібні імена — `NamedTuple` (Модуль 06).

## 6. Closures та lambda

### Звичайні функції — first-class

```python
def apply(f: Callable[[int], int], x: int) -> int:
    return f(x)

def double(n: int) -> int:
    return n * 2

apply(double, 5)        # 10
```

### lambda — анонімні функції (обмежені)

```python
square = lambda x: x * x       # один ВИРАЗ, без statements
square(4)                      # 16
```

```swift
let square = { (x: Int) -> Int in x * x }   // Swift closure
```

> **⚠️ Пастка.** `lambda` у Python — лише **один вираз**, без багаторядкового тіла,
> без `if/for`-statements. Це навмисно: для складного тіла використовуй звичайну
> `def`. На відміну від Swift closures, lambda не призначені для великих блоків.

> **Best practice.** Не присвоюй `lambda` змінній (`f = lambda x: ...`) — `ruff`
> (E731) попередить. Якщо потрібна названа функція — пиши `def`. `lambda` доречна
> лише як короткий аргумент: `sorted(items, key=lambda p: p.age)`.

### Замикання захоплюють за посиланням

```python
def make_counter() -> Callable[[], int]:
    count = 0
    def increment() -> int:
        nonlocal count          # без nonlocal — count буде локальним
        count += 1
        return count
    return increment

c = make_counter()
c(); c()        # 1, 2
```

> **⚠️ Пастка.** Щоб **змінювати** змінну зовнішньої функції зсередини замикання,
> потрібне ключове слово `nonlocal` (для глобальних — `global`). Без нього
> присвоєння створить нову *локальну* змінну. У Swift замикання захоплюють
> змінні напряму.

### ⚠️ Late binding — замикання в циклі

Класична пастка, що кусає всіх. Замикання захоплює **змінну**, а не її значення
на момент створення:

```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]        # [2, 2, 2]  — НЕ [0, 1, 2]!
```

Усі три лямбди дивляться на ту саму `i`, яка після циклу дорівнює `2`. Це прямий
наслідок «імена-наклейки на об'єктах» ([Модуль 00](00-tooling-and-mental-model.md)).
Фікс — «заморозити» значення через default-аргумент (він обчислюється одразу):

```python
funcs = [lambda i=i: i for i in range(3)]
[f() for f in funcs]        # [0, 1, 2]  ✓
```

> У Swift цієї пастки немає: capture list і value-семантика захоплюють значення.
> У Python пам'ятай: замикання тримає **посилання на змінну**.

## 7. Docstrings — документація (PEP 257)

```python
def fetch(url: str, timeout: float = 30.0) -> bytes:
    """Завантажує вміст за URL.

    Args:
        url: Адреса ресурсу.
        timeout: Таймаут у секундах.

    Returns:
        Тіло відповіді у байтах.

    Raises:
        TimeoutError: Якщо перевищено timeout.
    """
    ...
```

Docstring — це рядок-літерал першим у тілі. Доступний у рантаймі через
`fetch.__doc__` і використовується інструментами документації. Це аналог
коментарів-документації `///` у Swift, але вбудований у мову як об'єкт.

Популярні стилі: **Google** (як вище), **NumPy**, **reStructuredText**.
Інструмент документації — [Sphinx](https://www.sphinx-doc.org/) або
[MkDocs](https://www.mkdocs.org/) з `mkdocstrings`.

## 8. Анотації типів для функцій (поглиблення)

```python
from collections.abc import Callable, Iterable

def transform(
    items: Iterable[int],
    fn: Callable[[int], str],
) -> list[str]:
    return [fn(x) for x in items]
```

- `Callable[[int], str]` — функція, що приймає `int`, повертає `str`
  (аналог Swift `(Int) -> String`).
- `Iterable[int]` — будь-що, по чому можна ітерувати (про протоколи — Модуль 08).

Деталі системи типів — у [Модулі 04](04-types-and-typing.md).

## 9. Декоратори (огляд)

Декоратор `@deco` обгортає функцію, додаючи поведінку. Це окрема велика тема —
повний розбір (власні, з параметрами, `@wraps`, типізація через `ParamSpec`,
декоратори-класи, `singledispatch`, порядок застосування) на сторінці
**[Декоратори](02-functions/decorators.md)**. Швидкий приклад:

```python
import functools

def logged(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"call {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper

@logged
def add(a: int, b: int) -> int:
    return a + b
```

## 10. Інструменти та бібліотеки

### `functools` — інструментарій вищого порядку

```python
from functools import partial, reduce, cache

# partial — часткове застосування (аналог curry / каррінга)
def connect(host: str, port: int, timeout: float = 30) -> str:
    return f"{host}:{port} (t={timeout})"

local = partial(connect, "localhost")    # зафіксували host
local(5432)                              # 'localhost:5432 (t=30)'
local(5432, timeout=5)                   # перевизначаємо timeout

# reduce — згортка (Swift: reduce)
reduce(lambda acc, x: acc + x, [1, 2, 3, 4], 0)    # 10
# але для суми/добутку бери вбудовані: sum(...), math.prod(...)

# cache — мемоізація (детальніше — сторінка про декоратори)
@cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

### `operator` — функції замість лямбд

Готові функції-аналоги операторів. Часто чистіші за `lambda` як `key=`:

```python
from operator import itemgetter, attrgetter, add

itemgetter(1)(("a", "b"))         # 'b'      — як lambda t: t[1]
itemgetter("age")({"age": 30})    # 30
attrgetter("year")(some_date)     # some_date.year

sorted(people, key=attrgetter("age"))           # сортування за полем
sorted(rows, key=itemgetter(2, 0))              # за кількома стовпцями
reduce(add, [1, 2, 3])                          # 6  — без lambda
```

Деталі сортування з `key=` — [Модуль 03 · Сортування](03-data-structures/sorting.md).

### `inspect` — інтроспекція сигнатур

```python
import inspect

def f(host: str, *, port: int = 5432) -> None: ...
inspect.signature(f)                 # (host: str, *, port: int = 5432) -> None
inspect.signature(f).parameters      # OrderedDict із описом параметрів
```

Корисно для фреймворків, DI-контейнерів і валідації — Python дозволяє читати
сигнатуру функції в рантаймі (чого у Swift немає без рефлексії Mirror).

## Best practices модуля

- Анотуй усі параметри й результати; тримай `pyright` strict.
- Опційні налаштування роби `*`-keyword-only.
- **Ніколи** не використовуй mutable-об'єкти (`[]`, `{}`) як default; патерн
  `= None` + перевірка.
- `lambda` — лише для коротких inline-виразів, не присвоюй у змінні.
- Пам'ятай про `nonlocal`/`global` при зміні зовнішніх змінних, і про
  late-binding (заморожуй через `i=i`).
- Пиши docstrings у стилі Google для публічного API.
- `operator.itemgetter`/`attrgetter` замість `lambda` для `key=`.
- На декораторах — завжди `@functools.wraps`.

## Див. також

- [Декоратори](02-functions/decorators.md) — повний розбір.
- [Модуль 03 · Сортування](03-data-structures/sorting.md) — `key=`, `itemgetter`/`attrgetter`.
- [Модуль 04 — Типи](04-types-and-typing.md) — `Callable`, `ParamSpec`, типізація.
- [Модуль 05 — Класи](05-classes-and-oop.md) — `@property`, `__call__`, методи.
- [Модуль 09 — Ітератори](09-iterators-and-generators.md) — генератор-функції з `yield`.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 03 — Структури даних](03-data-structures.md)
