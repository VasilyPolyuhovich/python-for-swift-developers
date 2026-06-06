# Сортування

[← Курс](../README.md) · [Модуль 03](../03-data-structures.md) · **Сортування**

У Swift є `sorted()`, `sorted(by:)`, `sort()` і `Comparable`. Python дає той самий
набір ідей, але з кількома відмінностями, на яких легко спіткнутися:
`sorted()` vs `.sort()`, аргумент `key` (а не компаратор), і **гарантована
стабільність**.

---

## 1. `sorted()` vs `.sort()`

```python
nums = [3, 1, 4, 1, 5]

sorted(nums)            # [1, 1, 3, 4, 5]  — НОВИЙ список, оригінал цілий
sorted(nums, reverse=True)   # [5, 4, 3, 1, 1]
nums                    # [3, 1, 4, 1, 5]  — не змінився

nums.sort()             # сортує НА МІСЦІ, повертає None
nums                    # [1, 1, 3, 4, 5]
```

| | Повертає | Мутує? | Працює на |
|--|----------|--------|-----------|
| `sorted(x)` | новий `list` | ні | будь-який ітерабельний |
| `x.sort()` | `None` | так | лише `list` |

> **⚠️ Пастка №1.** `result = nums.sort()` дасть `result == None`! `.sort()` мутує
> на місці й повертає `None` (як багато мутуючих методів у Python). Якщо потрібен
> результат — `sorted()`. Якщо треба відсортувати наявний список без копії —
> `.sort()`, але окремим рядком.

> **⚠️ Пастка №2.** `sorted()` приймає будь-що ітерабельне (`set`, `dict`,
> генератор) і **завжди** повертає `list`: `sorted({3,1,2})` → `[1, 2, 3]`.

---

## 2. `key=` — не компаратор, а «функція ознаки»

У Swift ти пишеш замикання-компаратор (`sort { $0.age < $1.age }`). У Python
ти даєш **функцію одного аргумента**, що повертає ознаку для порівняння. Python
сам порівнює ці ознаки. Це і швидше (ознака рахується раз на елемент), і
зазвичай простіше.

```python
words = ["banana", "pie", "Washington", "book"]

sorted(words)                    # ['Washington', 'banana', 'book', 'pie']
                                 # ⚠️ великі літери йдуть перші (ASCII!)
sorted(words, key=str.lower)     # ['banana', 'book', 'pie', 'Washington']
sorted(words, key=len)           # ['pie', 'book', 'banana', 'Washington']
```

### `key` для об'єктів і кортежів — `operator`

Замість `lambda` ідіоматичні `itemgetter`/`attrgetter` з `operator`
([Модуль 02](../02-functions.md)):

```python
from operator import itemgetter, attrgetter
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int

people = [Person("Bob", 30), Person("Alice", 30), Person("Carol", 25)]

sorted(people, key=attrgetter("age"))      # за полем .age
sorted(rows, key=itemgetter(0))            # за rows[i][0] (кортежі/списки)
sorted(d.items(), key=itemgetter(1))       # за значенням словника
```

---

## 3. Стабільність і кілька ключів

Сортування Python **стабільне**: елементи з однаковим ключем зберігають
відносний порядок. Це дає простий рецепт для **багатоключового** сортування.

### Однаковий напрямок усіх ключів — кортеж у `key`

```python
# спочатку за age, потім (для рівних) за name — обидва за зростанням
sorted(people, key=attrgetter("age", "name"))
# [Carol(25), Alice(30), Bob(30)]
```

### Різні напрямки — сортуй послідовно, від менш до більш значущого

Коли напрямки різні (age за спаданням, name за зростанням), скористайся
стабільністю: сортуй спершу за **другорядним** ключем, потім за **головним**.

```python
s = sorted(people, key=attrgetter("name"))                 # 1) вторинний: name ↑
s = sorted(s, key=attrgetter("age"), reverse=True)         # 2) головний: age ↓
# [Alice(30), Bob(30), Carol(25)]
```

> **Чому це працює.** Другий sort переставляє лише за age; для рівних age порядок
> із першого sort (за name) лишається завдяки стабільності. Це канонічний
> Python-патерн для змішаних напрямків — у Swift ти б писав складніший компаратор.

Для числових полів змішаний напрям можна й одним ключем — інвертувати знак:

```python
sorted(people, key=lambda p: (-p.age, p.name))   # age ↓, name ↑
```

---

## 4. Сортування словників

Словник сам не «сортується» (він упорядкований за вставкою), але можна
відсортувати його `.items()` і зібрати назад:

```python
scores = {"math": 90, "art": 85, "cs": 95}

# за значенням, за спаданням → список пар
sorted(scores.items(), key=itemgetter(1), reverse=True)
# [('cs', 95), ('math', 90), ('art', 85)]

# назад у dict (порядок збережеться — dict упорядкований з 3.7)
dict(sorted(scores.items(), key=itemgetter(1)))
# {'art': 85, 'math': 90, 'cs': 95}

# просто ключ із макс/мін значенням — без повного сортування
max(scores, key=scores.get)        # 'cs'
min(scores, key=scores.get)        # 'art'
```

---

## 5. Власні типи: `Comparable` → `__lt__`

Щоб тип сортувався «з коробки» (без `key`), реалізуй `__lt__` (Python для
сортування достатньо «менше»). Аналог `Comparable` у Swift:

```python
from functools import total_ordering

@total_ordering                    # згенерує >, >=, <=, == з __lt__ і __eq__
class Version:
    def __init__(self, major: int, minor: int):
        self.major, self.minor = major, minor
    def __eq__(self, other):
        return (self.major, self.minor) == (other.major, other.minor)
    def __lt__(self, other):
        return (self.major, self.minor) < (other.major, other.minor)

sorted([Version(1, 2), Version(1, 0), Version(2, 0)])    # працює без key
```

Деталі dunder-методів порівняння — [Модуль 05](../05-classes-and-oop.md). Для
простих record-типів `@dataclass(order=True)` робить це автоматично
([Модуль 06](../06-structs-and-value-types.md)).

> **⚠️ Пастка.** Не можна сортувати різнотипне: `sorted([1, "a"])` → `TypeError`
> (на відміну від деяких мов, Python не порівнює `int` із `str`).

---

## 6. Реверс, частковий порядок: `reversed`, `heapq`, `bisect`

```python
list(reversed([1, 2, 3]))          # [3, 2, 1]  — лінива ітерація у зворотному
sorted(x, reverse=True)            # повне сортування за спаданням

import heapq
heapq.nlargest(3, nums)            # 3 найбільші — дешевше за повний sort
heapq.nsmallest(2, nums)           # 2 найменші
# heap як пріоритетна черга:
h = []
heapq.heappush(h, 5); heapq.heappush(h, 1)
heapq.heappop(h)                   # 1  (завжди мінімум)

import bisect
a = [1, 3, 5, 7]
bisect.insort(a, 4)                # [1, 3, 4, 5, 7] — вставка зі збереженням порядку
bisect.bisect_left(a, 5)           # індекс для вставки (бінарний пошук)
```

> **Best practice.** Для «топ-N» із великої колекції бери `heapq.nlargest`/
> `nsmallest` (O(n log k)), а не `sorted(...)[:N]` (O(n log n)). Для частих
> вставок зі збереженням порядку — `bisect.insort`.

---

## Шпаргалка / рецепти

```python
sorted(data)                                   # за зростанням, нова копія
data.sort()                                    # на місці
sorted(data, reverse=True)                     # за спаданням
sorted(words, key=str.lower)                   # без урахування регістру
sorted(objs, key=attrgetter("field"))          # за атрибутом
sorted(objs, key=attrgetter("a", "b"))         # кілька ключів, той самий напрям
sorted(d.items(), key=itemgetter(1))           # словник за значенням
sorted(data, key=lambda x: (-x.score, x.name)) # score ↓, name ↑
max(d, key=d.get)                              # ключ з макс. значенням
heapq.nlargest(10, data)                       # топ-10 без повного сортування
```

## Див. також

- [Модуль 03 — Структури даних](../03-data-structures.md) — list/dict/set/tuple.
- [Модуль 02 — Функції](../02-functions.md) — `operator.itemgetter`/`attrgetter`, `key=`.
- [Модуль 05 — Класи](../05-classes-and-oop.md) — `__lt__`, `__eq__`, `total_ordering`.
- [Модуль 06 — Value-типи](../06-structs-and-value-types.md) — `@dataclass(order=True)`.
- [Тематичний індекс](../INDEX.md).
