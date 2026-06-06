# Декоратори

[← Курс](../README.md) · [Модуль 02](../02-functions.md) · **Декоратори**

Декоратор — це функція, що **обгортає** іншу функцію (чи клас), додаючи поведінку
без зміни її коду. Синтаксис `@deco` — лише цукор:

```python
@logged
def add(a, b): ...

# точно те саме, що:
def add(a, b): ...
add = logged(add)
```

У Swift найближче — property wrappers (`@Published`, `@State`) і result builders,
але декоратори універсальніші: працюють із будь-яким викликом. `@property`,
`@staticmethod`, `@dataclass`, `@cache` — усе це декоратори.

> **Передумова.** Декоратори стоять на тому, що функції — це
> [об'єкти першого класу](../00-tooling-and-mental-model.md): їх можна передавати,
> повертати, переприсвоювати.

---

## 1. Найпростіший декоратор

```python
import functools

def logged(fn):
    @functools.wraps(fn)              # ← обов'язково, пояснення нижче
    def wrapper(*args, **kwargs):
        print(f"call {fn.__name__}{args}")
        result = fn(*args, **kwargs)
        return result
    return wrapper

@logged
def add(a, b):
    "adds two numbers"
    return a + b

add(2, 3)
# call add(2, 3)
# → 5
```

`*args, **kwargs` у `wrapper` роблять його універсальним до будь-якої сигнатури.

### Навіщо `@functools.wraps`

Без нього обгортка «з'їдає» метадані оригіналу:

```python
add.__name__     # 'add'        (з @wraps)   vs   'wrapper' (без)
add.__doc__      # 'adds two...' (з @wraps)   vs   None      (без)
```

> **⚠️ Пастка.** **Завжди** клади `@functools.wraps(fn)` на внутрішню обгортку.
> Інакше зламаєш інтроспекцію, документацію, та інструменти, що дивляться на
> `__name__`/`__doc__`/сигнатуру. `@wraps` ще й проставляє `__wrapped__`, через
> який можна дістати оригінал.

---

## 2. Декоратор із параметрами

Потрібен **ще один** рівень вкладеності: зовнішня функція приймає параметри й
повертає сам декоратор.

```python
def repeat(n: int):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return [fn(*args, **kwargs) for _ in range(n)]
        return wrapper
    return decorator

@repeat(3)
def roll():
    return 7

roll()        # [7, 7, 7]
```

Читай зсередини назовні: `repeat(3)` повертає `decorator`, який обгортає `roll`.

> **Ментальна модель трьох рівнів:**
> - `repeat(n)` — фабрика декораторів (бере **аргументи декоратора**).
> - `decorator(fn)` — власне декоратор (бере **функцію**).
> - `wrapper(*args)` — заміна (бере **аргументи виклику**).

---

## 3. Типізація декораторів (`ParamSpec`)

Наївний декоратор «втрачає» типи: `pyright` бачить `wrapper(*args, **kwargs)` і
не знає сигнатури. `ParamSpec` ([PEP 612](https://peps.python.org/pep-0612/))
зберігає її — обгорнута функція лишається типобезпечною:

```python
from collections.abc import Callable
from functools import wraps

def logged[**P, R](fn: Callable[P, R]) -> Callable[P, R]:   # PEP 695 + ParamSpec
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"call {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper

@logged
def add(a: int, b: int) -> int:
    return a + b

add(2, 3)        # pyright знає: int, int → int.  add(2, "x") → помилка типу
```

`[**P, R]` — це PEP 695-синтаксис для `ParamSpec P` і `TypeVar R`. До 3.12
писали явно `P = ParamSpec("P")`. Детальніше — [Модуль 07](../07-generics.md).

---

## 4. Декоратори-класи та stateful

Якщо декоратору потрібен стан, зручніше клас із `__call__`:

```python
class CountCalls:
    def __init__(self, fn):
        functools.update_wrapper(self, fn)
        self.fn = fn
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.fn(*args, **kwargs)

@CountCalls
def ping():
    return "pong"

ping(); ping()
ping.count        # 2
```

---

## 5. Готові декоратори зі stdlib

Більшість того, що тобі треба, вже є:

```python
from functools import cache, lru_cache, cached_property, wraps, singledispatch

@cache                       # мемоізація без обмеження (3.9+)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

@lru_cache(maxsize=128)      # мемоізація з LRU-витісненням
def query(key: str) -> bytes: ...
```

| Декоратор | Що робить |
|-----------|-----------|
| `functools.cache` / `lru_cache` | Мемоізація результатів |
| `functools.cached_property` | Властивість, що рахується раз і кешується ([Модуль 05](../05-classes-and-oop.md)) |
| `functools.singledispatch` | Перевантаження за типом 1-го аргумента (§6) |
| `functools.wraps` | Збереження метаданих в обгортці |
| `property`, `staticmethod`, `classmethod` | Методи-аксесори ([Модуль 05](../05-classes-and-oop.md)) |
| `dataclasses.dataclass` | Генерація `__init__`/`__eq__`/... ([Модуль 06](../06-structs-and-value-types.md)) |
| `contextlib.contextmanager` | Функція → менеджер контексту ([Модуль 10](../10-errors-and-exceptions.md)) |
| `abc.abstractmethod` | Абстрактний метод ([Модуль 08](../08-protocols-and-interfaces.md)) |

---

## 6. `singledispatch` — перевантаження за типом

У Swift перевантаження за типом — це окремі `func` із різними сигнатурами. У
Python функції не перевантажуються (друге визначення просто перекриває перше).
`singledispatch` дає таку поведінку за типом **першого** аргумента:

```python
from functools import singledispatch

@singledispatch
def describe(x) -> str:
    return f"object {x!r}"           # дефолтна реалізація

@describe.register
def _(x: int) -> str:
    return f"int {x}"

@describe.register
def _(x: list) -> str:
    return f"list of {len(x)}"

describe(5)        # 'int 5'
describe([1, 2])   # 'list of 2'
describe("hi")     # "object 'hi'"  — дефолт
```

(Для диспетчеризації за `self` у класах — `singledispatchmethod`.)

---

## 7. Кілька декораторів і порядок

```python
@a
@b
def f(): ...
# еквівалент: f = a(b(f))  — застосовуються ЗНИЗУ ВГОРУ
```

> **⚠️ Пастка.** Порядок важливий. `@app.route(...)` над `@logged` ≠ навпаки.
> Найближчий до `def` декоратор обгортає першим.

---

## Шпаргалка / рецепти

```python
# Заміряти час виконання
def timed[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*a: P.args, **k: P.kwargs) -> R:
        import time
        t = time.perf_counter()
        try:
            return fn(*a, **k)
        finally:
            print(f"{fn.__name__}: {time.perf_counter() - t:.4f}s")
    return wrapper

# Кешувати дорогий чистий обчислювальний результат
@cache
def expensive(n): ...

# Повторювати при помилці — бери tenacity, не пиши свій (Модуль 10)
from tenacity import retry, stop_after_attempt
@retry(stop=stop_after_attempt(3))
def flaky(): ...
```

## Див. також

- [Модуль 02 — Функції](../02-functions.md) — closures, `nonlocal`, first-class функції.
- [Модуль 05 — Класи](../05-classes-and-oop.md) — `@property`, `@cached_property`, `__call__`.
- [Модуль 07 — Дженеріки](../07-generics.md) — `ParamSpec`, `TypeVar`, PEP 695.
- [Модуль 10 — Помилки](../10-errors-and-exceptions.md) — `@contextmanager`, `tenacity`.
- [Тематичний індекс](../INDEX.md).
