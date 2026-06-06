# Structural pattern matching (`match`)

[← Курс](../README.md) · [Модуль 01](../01-syntax-and-control-flow.md) · **match**

`match` (Python 3.10+, [PEP 634](https://peps.python.org/pep-0634/)) — це не
розширений `switch`, а **деструктуризація за структурою**, найближчий аналог
Swift `switch` із `case let`, where-умовами й матчингом enum з associated values.
Ключова відмінність: Python `match` зіставляє за **формою** значення, а не лише
за рівністю.

```swift
// Swift
switch point {
case (0, 0): print("origin")
case (let x, 0): print("on x-axis at \(x)")
case let (x, y) where x == y: print("diagonal")
default: print("elsewhere")
}
```

```python
match point:
    case (0, 0):
        print("origin")
    case (x, 0):                 # x ЗВ'ЯЗУЄТЬСЯ, не порівнюється
        print(f"on x-axis at {x}")
    case (x, y) if x == y:       # guard — аналог where
        print("diagonal")
    case _:                      # default
        print("elsewhere")
```

> **⚠️ Головна пастка capture vs порівняння.** `case (x, 0)` — це **не** «x
> дорівнює змінній x». Голе ім'я в патерні **захоплює** значення (зв'язує нову
> змінну). Щоб зіставити зі значенням наявної константи — використай
> **крапку** (`case Color.RED`) або іменований атрибут, інакше Python просто
> перезапише твою змінну. Це найчастіша помилка новачків у `match`.

---

## Види патернів

### 1. Літерали та capture

```python
match command:
    case 0:           ...     # літерал
    case "quit":      ...     # рядок-літерал
    case x:           ...     # capture: зв'язує будь-що в x (як `default` + bind)
    case _:           ...     # wildcard: збіг із будь-чим, без зв'язування
```

### 2. OR-патерни (`|`) і `as`

```python
match status:
    case 400 | 401 | 403 | 404:        # кілька альтернатив
        return "client error"
    case 500 | 502 | 503 as code:      # as — захопити те, що збіглося
        return f"server error {code}"
```

### 3. Type patterns (зіставлення за класом)

```python
match value:
    case int() | float():     # ДУЖКИ обов'язкові: int() — патерн «екземпляр int»
        return "number"
    case str():
        return "string"
    case list():
        return "list"
```

> **⚠️ Пастка.** `case int:` (без дужок) — це capture в змінну на ім'я `int`, а
> **не** перевірка типу! Для перевірки типу завжди `case int():`.

### 4. Sequence patterns

```python
match data:
    case []:                  # порожній список
        ...
    case [x]:                 # рівно один елемент
        ...
    case [first, *rest]:      # голова + хвіст (rest — list)
        ...
    case [_, _, third]:       # рівно три, цікавить третій
        ...
    case (x, y):              # кортеж так само
        ...
```

Працює для будь-яких послідовностей (list, tuple), але **не** для рядків
(`str` як послідовність символів навмисно не матчиться як sequence).

### 5. Mapping patterns (словники)

```python
match payload:
    case {"type": "circle", "radius": r}:        # потрібні ключі + capture
        return 3.14159 * r * r
    case {"type": "rect", "w": w, "h": h}:
        return w * h
    case {"type": t, **rest}:                    # **rest — решта пар
        return f"unknown {t}, extra={rest}"
```

> Mapping-патерн вимагає лише **присутності** вказаних ключів — зайві ігноруються
> (тому й `**rest` для їх захоплення). Це ідеально для розбору JSON.

### 6. Class patterns (деструктуризація об'єктів)

Найпотужніше — матчинг по полях класу, аналог Swift enum з associated values:

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

match p:
    case Point(x=0, y=0):         # за іменами полів
        return "origin"
    case Point(x=0, y=y):         # частковий збіг + capture
        return f"y-axis at {y}"
    case Point(x=x, y=y) if x == y:
        return f"diagonal {x}"
    case Point():                 # будь-який Point
        return "somewhere"
```

Позиційний синтаксис (`Point(0, 0)`) теж працює — завдяки `__match_args__`, яке
`@dataclass` і `NamedTuple` ставлять автоматично ([Модуль 06](../06-structs-and-value-types.md)):

```python
match p:
    case Point(0, 0):  return "origin"
    case Point(x, y):  return f"({x}, {y})"
```

Для звичайних класів `__match_args__` задають вручну:

```python
class Vec:
    __match_args__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y
```

---

## Вичерпність: чого Python НЕ робить

```python
match shape:
    case Circle(): ...
    case Rect():   ...
    # немає case _  →  якщо прийде Triangle, match просто "провалиться"
    #                   (нічого не виконає, без помилки!)
```

> **⚠️ Пастка №6 (з хабу модуля).** На відміну від Swift, `match` **не вимагає
> вичерпності**. Якщо жоден `case` не збігся — блок мовчки нічого не виконує.
> Дві стратегії:
> 1. Майже завжди додавай `case _:` (явний default/помилка).
> 2. Для enum-подібної вичерпності покладайся на `pyright` + `assert_never`:

```python
from typing import assert_never

def area(shape: Circle | Rect) -> float:
    match shape:
        case Circle(radius=r): return 3.14159 * r * r
        case Rect(w=w, h=h):   return w * h
        case _:
            assert_never(shape)   # pyright помилиться, якщо додати новий варіант
                                  # і забути case — повертає статичну вичерпність!
```

Це і є спосіб отримати Swift-рівень безпеки enum-switch. Деталі —
[Модуль 06 · ADT](../06-structs-and-value-types.md) і [Модуль 04](../04-types-and-typing.md).

---

## Коли `match`, а коли ні

- **Бери `match`** для розбору структур: JSON/повідомлень, AST, команд, ADT,
  кортежів результатів.
- **Не бери `match`** для простого «дорівнює одному з» — звичайний `if/elif` або
  `in {…}` читабельніший:
  ```python
  if status in {400, 401, 403}:   # ясніше за match з одними літералами
      ...
  ```
- Для діапазонів `match` незручний (немає патерну «< 0») — використовуй guard
  (`case n if n < 0`) або `if/elif`.

## Шпаргалка / рецепти

```python
# Розбір команди CLI
match args:
    case ["add", item]:           add(item)
    case ["remove", *items]:      remove_all(items)
    case ["help"] | []:           show_help()
    case _:                       error("unknown command")

# Розбір HTTP-відповіді (dict із JSON)
match response:
    case {"status": "ok", "data": data}:    use(data)
    case {"status": "error", "message": m}: fail(m)
    case _:                                  fail("malformed")

# Вичерпний матч ADT із статичною перевіркою
match event:
    case Click(x, y):       ...
    case KeyPress(key):     ...
    case _:                 assert_never(event)
```

## Див. також

- [Модуль 01 — Синтаксис](../01-syntax-and-control-flow.md) — `if/elif`, тернарний, цикли.
- [Модуль 06 — Value-типи та ADT](../06-structs-and-value-types.md) — `match` + dataclass/enum.
- [Модуль 04 — Типи](../04-types-and-typing.md) — `assert_never`, статична вичерпність.
- [Тематичний індекс](../INDEX.md).
