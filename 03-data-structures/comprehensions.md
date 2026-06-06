# Comprehensions — трансформація та фільтрація

[← Курс](../README.md) · [Модуль 03](../03-data-structures.md) · **Comprehensions**

Comprehension — найвиразніша риса Python і головний спосіб **трансформувати** й
**фільтрувати** колекції. Це заміна ланцюжкам `map`/`filter` зі Swift, але
вбудована в синтаксис.

```swift
// Swift
let squares = (1...5).map { $0 * $0 }
let evens   = numbers.filter { $0 % 2 == 0 }
let result  = numbers.filter { $0 % 2 == 0 }.map { $0 * $0 }
```

```python
# Python
squares = [x * x for x in range(1, 6)]                   # map
evens   = [x for x in numbers if x % 2 == 0]             # filter
result  = [x * x for x in numbers if x % 2 == 0]         # filter + map
```

Загальна форма: `[ВИРАЗ for ЗМІННА in ДЖЕРЕЛО if УМОВА]`.

---

## 1. Чотири різновиди

```python
[x * x for x in nums]            # list comprehension      → list
{x * x for x in nums}            # set comprehension        → set (унікальні)
{k: v for k, v in pairs}         # dict comprehension       → dict
(x * x for x in nums)            # generator expression     → лінивий ітератор!
```

> **⚠️ Пастка.** Дужки `()` дають **не кортеж**, а **генератор** (лінивий, на один
> прохід — [Модуль 09](../09-iterators-and-generators.md)). Кортеж-comprehension
> не існує; для кортежу: `tuple(x for x in ...)`.

```python
{c: ord(c) for c in "abc"}       # {'a': 97, 'b': 98, 'c': 99}
{x % 3 for x in range(10)}       # {0, 1, 2}  — set прибирає дублікати
```

---

## 2. Умови: фільтр vs тернарний

Дві різні позиції `if` — не плутай:

```python
# if У КІНЦІ — це ФІЛЬТР (пропустити елементи)
[x for x in range(5) if x % 2 == 0]          # [0, 2, 4]

# if/else ПЕРЕД for — це ТЕРНАРНИЙ вираз (трансформувати кожен)
[x if x % 2 == 0 else -x for x in range(5)]  # [0, -1, 2, -3, 4]

# можна разом: спершу трансформація-тернар, потім фільтр
[x * 2 if x > 0 else 0 for x in data if x is not None]
```

Кілька умов фільтра — просто кілька `if` (логічне І) або `and`:

```python
[x for x in nums if x > 0 if x < 100]        # = if x > 0 and x < 100
```

---

## 3. Вкладені цикли: flatten і transpose

Кілька `for` поспіль читаються **зліва направо**, як вкладені цикли:

```python
matrix = [[1, 2, 3], [4, 5, 6]]

# flatten — «розгорнути» в один список
[n for row in matrix for n in row]           # [1, 2, 3, 4, 5, 6]
# еквівалент:
# for row in matrix:
#     for n in row:
#         ...

# transpose — через вкладений comprehension
[[row[i] for row in matrix] for i in range(3)]   # [[1, 4], [2, 5], [3, 6]]
```

> **⚠️ Пастка порядку.** У `[... for a in A for b in B]` порядок `for` той самий,
> що у звичайних вкладених циклах: зовнішній `A`, внутрішній `B`. А ось вираз
> вкладеного comprehension (`[[...] for ...]`) читається інакше — внутрішні дужки
> створюють підсписок. Якщо плутаєшся — пиши звичайний цикл.

---

## 4. Walrus у comprehension

`:=` дозволяє обчислити дороге значення раз і використати і в умові, і в результаті:

```python
data = ["1", "x", "3"]
[n for s in data if (n := s).isdigit()]      # ['1', '3']

# реальний кейс: не викликати f(x) двічі
[y for x in xs if (y := f(x)) is not None]
```

---

## 5. Коли НЕ comprehension

Comprehensions потужні, але не універсальні:

- **Понад 2 рівні вкладеності** → нечитабельно. Пиши звичайний цикл або
  генератор-функцію ([Модуль 09](../09-iterators-and-generators.md)).
- **Побічні ефекти** (друк, запис) → НЕ роби comprehension лише заради циклу:
  ```python
  [print(x) for x in items]    # ❌ створює непотрібний список із None
  for x in items: print(x)     # ✓ звичайний цикл
  ```
- **Велике/нескінченне джерело** → бери generator expression `( ... )`, щоб не
  матеріалізувати все в пам'ять:
  ```python
  total = sum(x * x for x in range(10_000_000))   # без проміжного списку
  ```

> **Best practice.** Comprehension читабельніший за `map`/`filter` з `lambda`. Але
> `map(str, nums)` (готова функція, без `lambda`) теж ок. Правило: якщо логіка не
> влазить у простий вираз — звичайний цикл чи `def`.

---

## 6. `map`/`filter` — коли доречні

Існують і повертають **ліниві** ітератори:

```python
list(map(str, [1, 2, 3]))                 # ['1', '2', '3']
list(filter(None, [0, 1, "", "x"]))       # [1, 'x']  — filter(None) прибирає falsy
list(map(int, "123"))                     # [1, 2, 3]
```

`map(готова_функція, ...)` буває чистішим за comprehension. Але `map(lambda ...)`
майже завжди гірший за comprehension — бери comprehension.

---

## Шпаргалка / рецепти

```python
[f(x) for x in xs]                       # трансформація (map)
[x for x in xs if pred(x)]               # фільтр
[f(x) for x in xs if pred(x)]            # фільтр + трансформація
{x for x in xs}                          # унікальні (set)
{k: f(v) for k, v in d.items()}          # трансформація значень словника
{v: k for k, v in d.items()}             # інверсія словника (key ⇄ value)
[y for row in grid for y in row]         # flatten
sum(x*x for x in xs)                     # агрегація через генератор (без списку)
[x for x in xs if x]                     # прибрати falsy (0, '', None, [])
list(dict.fromkeys(xs))                  # унікальні зі збереженням порядку
```

## Див. також

- [Модуль 03 — Структури даних](../03-data-structures.md) — list/dict/set.
- [Модуль 09 — Ітератори та генератори](../09-iterators-and-generators.md) — generator expressions, `itertools`.
- [Модуль 03 · Сортування](sorting.md) і [Конвертації](conversions.md).
- [Тематичний індекс](../INDEX.md).
