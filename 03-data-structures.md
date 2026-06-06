# Модуль 03. Структури даних

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 03**

Туторіал: [§5 Структури даних](https://docs.python.org/uk/3/tutorial/datastructures.html).

Python має чотири вбудовані колекції: `list`, `tuple`, `set`, `dict`. Вони
мапляться на Swift, але з критичною різницею: **усі вони — reference-типи**
(окрім незмінних `tuple`/`frozenset`, які поводяться як value через незмінність).

**Поглиблені сторінки модуля** (повні довідники з прикладами):

| Сторінка | Про що |
|----------|--------|
| [list](03-data-structures/list.md) | динамічний масив: зрізи, методи, копіювання, продуктивність |
| [dict](03-data-structures/dict.md) | словник: `get`/`setdefault`, злиття, views, hashable-ключі |
| [set](03-data-structures/set.md) | множина: алгебра множин, `frozenset`, O(1)-членство |
| [tuple](03-data-structures/tuple.md) | незмінний кортеж: розпакування, як ключ, записи |
| [comprehensions](03-data-structures/comprehensions.md) | трансформація/фільтрація, generator expressions |
| [sorting](03-data-structures/sorting.md) | `sorted`/`sort`, `key=`, кілька ключів, `heapq`/`bisect` |
| [conversions](03-data-structures/conversions.md) | `int()`/`str()`/`list()`/…, парсинг, дедуплікація |

Нижче — оглядове ядро; за деталями йди на відповідну сторінку.

| Python | Swift | Mutable? | Впорядкований? |
|--------|-------|----------|----------------|
| `list` | `Array` | так | так |
| `tuple` | `(a, b)` / value | ні | так |
| `set` | `Set` | так | ні |
| `frozenset` | — | ні | ні |
| `dict` | `Dictionary` | так | так (за вставкою, 3.7+) |

## 1. list — динамічний масив

```python
nums: list[int] = [1, 2, 3]
nums.append(4)             # [1,2,3,4]
nums.insert(0, 0)          # [0,1,2,3,4]
nums.pop()                 # 4   (видаляє й повертає останній)
nums[0]                    # 0   (індексація)
nums[-1]                   # 3   (від'ємний індекс — з кінця!)
len(nums)                  # довжина
```

### ⚠️ Від'ємні індекси та зрізи (slices)

Цього немає у Swift — потужний, але незвичний інструмент:

```python
data = [10, 20, 30, 40, 50]
data[1:3]        # [20, 30]      — [start:stop), stop не включається
data[:2]         # [10, 20]      — з початку
data[2:]         # [30, 40, 50]  — до кінця
data[-2:]        # [40, 50]      — останні два
data[::2]        # [10, 30, 50]  — кожен другий (step)
data[::-1]       # [50,40,30,20,10] — реверс
```

```swift
// Swift-аналог data[1:3] — громіздкіший:
Array(data[1..<3])
```

### ⚠️ Копіювання list (reference semantics!)

```python
a = [1, 2, 3]
b = a              # ТЕ САМЕ посилання
b.append(4)
a                  # [1, 2, 3, 4]  — змінилось!

c = a.copy()       # ПОВЕРХНЕВА копія (або a[:] чи list(a))
c.append(5)
a                  # [1, 2, 3, 4]  — c незалежний

import copy
d = copy.deepcopy(a)   # глибока копія для вкладених структур
```

> **⚠️ Пастка.** Це найчастіша помилка для Swift-розробника. У Swift `var b = a`
> для `Array` дає копію. У Python — спільне посилання. Завжди свідомо вирішуй:
> треба тобі копія (`.copy()`) чи спільне посилання.

## 2. Comprehensions — ідіоматична трансформація

Замість `map`/`filter` у Python ідіоматичні **comprehensions**. Це найвиразніша
риса мови.

### Swift
```swift
let squares = (1...5).map { $0 * $0 }
let evens = numbers.filter { $0 % 2 == 0 }
let evenSquares = numbers.filter { $0 % 2 == 0 }.map { $0 * $0 }
```

### Python
```python
squares = [x * x for x in range(1, 6)]                    # [1,4,9,16,25]
evens = [x for x in numbers if x % 2 == 0]                # filter
even_squares = [x * x for x in numbers if x % 2 == 0]     # map + filter
```

Працює для всіх колекцій:

```python
{x * x for x in nums}                    # set comprehension
{k: v for k, v in pairs}                 # dict comprehension
(x * x for x in nums)                    # generator (lazy! — Модуль 09)
```

> **Best practice.** Comprehension читабельніший за `map`/`filter` із `lambda`.
> Але **не вкладай** більше двох рівнів — стає нечитабельно; тоді звичайний цикл
> або генератор-функція кращі.

`map`/`filter` теж існують, але повертають lazy-ітератори й рідше ідіоматичні:

```python
list(map(str, nums))         # рідше; comprehension зазвичай ясніший
```

## 3. tuple — незмінна впорядкована послідовність

```python
point: tuple[int, int] = (3, 4)
x, y = point                 # розпакування (як у Swift)
point[0]                     # 3
# point[0] = 5               # ПОМИЛКА: tuple незмінний
```

Кортеж зі змінним числом однотипних елементів:

```python
row: tuple[int, ...] = (1, 2, 3, 4)   # ... означає "будь-яка довжина"
```

> **⚠️ Пастка.** Кортеж із одного елемента — `(x,)` із комою! `(x)` — це просто
> `x` у дужках.

Кортежі добре підходять як легкі незмінні «record»-и, але без імен полів. Для
іменованих — `NamedTuple` (Модуль 06).

## 4. set — множина унікальних елементів

```python
s: set[int] = {1, 2, 3, 2}     # {1, 2, 3}
s.add(4)
s.discard(2)                   # видалити без помилки, якщо немає
3 in s                         # True — перевірка членства O(1)

a, b = {1, 2, 3}, {2, 3, 4}
a | b      # {1,2,3,4}  об'єднання  (Swift: a.union(b))
a & b      # {2,3}      перетин     (Swift: a.intersection(b))
a - b      # {1}        різниця     (Swift: a.subtracting(b))
a ^ b      # {1,4}      симетрична різниця
```

Порожня множина — `set()`, **не** `{}` (це порожній dict!).

```python
empty_set = set()       # порожня множина
empty_dict = {}         # порожній СЛОВНИК
```

## 5. dict — словник

```python
ages: dict[str, int] = {"Vasyl": 40, "Olha": 35}
ages["Vasyl"]              # 40
ages["Ivan"] = 28          # додати/оновити
ages.get("Ivan")           # 28
ages.get("Missing")        # None  (не падає!)
ages.get("Missing", 0)     # 0     (default)
"Vasyl" in ages            # True  (перевіряє КЛЮЧІ)
del ages["Ivan"]
```

> **⚠️ Пастка.** `ages["Missing"]` кидає `KeyError`. `ages.get("Missing")`
> повертає `None`. У Swift subscript словника завжди повертає `Optional`. У Python
> обирай свідомо: `[]` (кинути помилку) чи `.get()` (повернути default).

Ітерація:

```python
for key in ages:                     # за ключами (default)
    ...
for key, value in ages.items():      # пари
    ...
for value in ages.values():
    ...
```

`dict` зберігає **порядок вставки** (гарантовано з 3.7), на відміну від
Swift `Dictionary`, який невпорядкований.

## 6. Спеціалізовані колекції — `collections`

Stdlib-модуль `collections` дає важливі варіанти:

```python
from collections import defaultdict, Counter, deque

# defaultdict — словник з фабрикою default-значень
groups: defaultdict[str, list[int]] = defaultdict(list)
groups["a"].append(1)          # не треба перевіряти наявність ключа

# Counter — підрахунок
counts = Counter("abracadabra")        # {'a':5, 'b':2, 'r':2, 'c':1, 'd':1}
counts.most_common(2)                  # [('a', 5), ('b', 2)]

# deque — двостороння черга, O(1) з обох кінців (list — O(n) спереду)
queue: deque[int] = deque([1, 2, 3])
queue.appendleft(0)
queue.popleft()
```

| Завдання | Інструмент |
|----------|-----------|
| Стек | `list` (`.append`/`.pop`) |
| Черга / FIFO | `collections.deque` (НЕ list!) |
| Підрахунок | `collections.Counter` |
| Словник з дефолтами | `collections.defaultdict` |
| Незмінний record | `NamedTuple` / `frozen dataclass` (Модуль 06) |

> **Best practice.** Не використовуй `list` як чергу (`pop(0)` — це O(n)). Для
> FIFO бери `deque`.

## 7. Розпакування (unpacking) — потужний синтаксис

```python
first, *rest = [1, 2, 3, 4]     # first=1, rest=[2,3,4]
*init, last = [1, 2, 3, 4]      # init=[1,2,3], last=4
a, (b, c) = 1, (2, 3)           # вкладене

# об'єднання колекцій через розпакування
merged = [*list_a, *list_b]
combined = {**dict_a, **dict_b}     # пізніший перезаписує
```

## 8. Сортування

```python
sorted(nums)                          # нова відсортована копія
sorted(nums, reverse=True)
sorted(people, key=lambda p: p.age)   # за ключем (як Swift sorted(by:))
nums.sort()                            # сортує НА МІСЦІ (мутує)
```

> **⚠️ Пастка.** `sorted(x)` повертає новий список; `x.sort()` мутує наявний і
> повертає `None`. Не плутай — `result = x.sort()` дасть `None`.

> **📖 Глибше.** Стабільність, сортування за кількома ключами, змішані напрямки,
> `itemgetter`/`attrgetter`, сортування словників за значенням, власні
> `Comparable`-типи, `heapq`/`bisect` — на сторінці
> **[Сортування](03-data-structures/sorting.md)**.

## Best practices модуля

- Пам'ятай, що `list`/`dict`/`set` — **reference-типи**. Копіюй свідомо.
- Comprehensions замість `map`/`filter` (до 2 рівнів вкладеності).
- `dict.get(key, default)` коли відсутність ключа — нормальна ситуація.
- `collections`: `deque` для черг, `Counter` для підрахунків, `defaultdict`
  для групування.
- Для незмінних колекцій-констант — `tuple`/`frozenset`.

## Див. також

- Поглиблені сторінки: [list](03-data-structures/list.md) · [dict](03-data-structures/dict.md) · [set](03-data-structures/set.md) · [tuple](03-data-structures/tuple.md) · [comprehensions](03-data-structures/comprehensions.md) · [sorting](03-data-structures/sorting.md) · [conversions](03-data-structures/conversions.md).
- [Модуль 06 — Value-типи](06-structs-and-value-types.md) — `NamedTuple`, `@dataclass`, незмінні записи.
- [Модуль 09 — Ітератори](09-iterators-and-generators.md) — ліниві послідовності, `itertools`.
- [Модуль 13 — Stdlib](13-stdlib-and-ecosystem.md) — `collections`, `heapq`, `bisect`, `array`.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 04 — Складні типи та система типів](04-types-and-typing.md)
