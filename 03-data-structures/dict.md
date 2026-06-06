# Словник (`dict`)

[← Курс](../README.md) · [Модуль 03](../03-data-structures.md) · **dict**

Swift-розробнику `dict` знайомий — це хеш-мапа, як `Dictionary`. Але є три
відмінності, які варто тримати в голові: Python-словник **упорядкований за
вставкою** (гарантовано з 3.7), має **референсну семантику** (це об'єкт, не
value-тип), а доступ за неіснуючим ключем кидає **виняток**, а не повертає
`Optional`.

```swift
var d: [String: Int] = ["a": 1]   // value-тип, копіюється при присвоєнні
let x = d["missing"]               // Optional(nil) — failable subscript
```

```python
d = {"a": 1}                       # референс-тип
x = d["missing"]                   # ❌ KeyError — НЕ None
```

---

## 1. Створення

```python
{"a": 1, "b": 2}                   # літерал
dict(a=1, b=2)                     # {'a': 1, 'b': 2}    — з keyword-аргументів
dict([("a", 1), ("b", 2)])         # {'a': 1, 'b': 2}    — зі списку пар
dict(zip(["x", "y"], [1, 2]))      # {'x': 1, 'y': 2}    — з двох списків
dict.fromkeys(["a", "b"], 0)       # {'a': 0, 'b': 0}    — спільне значення
{c: ord(c) for c in "abc"}         # {'a': 97, 'b': 98, 'c': 99}  — comprehension
```

`dict.fromkeys` зручний для ініціалізації, але має небезпечну пастку:

```python
d = dict.fromkeys(["a", "b"], [])  # одне значення на всі ключі!
d["a"].append(1)
d                                  # {'a': [1], 'b': [1]}  — список СПІЛЬНИЙ
```

> **⚠️ Пастка №1.** `dict.fromkeys(keys, [])` кладе **один і той самий** об'єкт
> у кожен ключ (значення обчислюється раз). Для незалежних мутабельних значень
> бери comprehension: `{k: [] for k in keys}`.

Деталі comprehension — [comprehensions.md](comprehensions.md). Конструктор
`dict(...)` із різних джерел — [conversions.md](conversions.md).

---

## 2. Доступ: `d[k]` vs `.get()`

```python
d = {"name": "Bob"}

d["name"]              # 'Bob'
d["age"]               # ❌ KeyError: 'age'

d.get("age")           # None    — без винятку
d.get("age", 0)        # 0       — свій дефолт
```

Це **навмисний** дизайн, протилежний Swift. У Swift subscript завжди повертає
`Optional`, і ти мусиш розпакувати навіть там, де ключ точно є. Python розділяє
два наміри: `d[k]` каже «ключ мусить бути, інакше це баг → виняток», а `.get(k)`
каже «ключа може й не бути → дай дефолт».

```swift
let v = d["age"] ?? 0   // Swift: завжди через Optional
```

```python
v = d.get("age", 0)     # Python: явний намір "може не бути"
```

> **Best practice.** `d[k]` для ключів, які за інваріантом мають існувати (баг,
> якщо ні). `.get(k, default)` для опціональних. Не глуши `KeyError` загальним
> `try/except` там, де доречний `.get()`.

### `setdefault` — взяти-або-створити

```python
d = {}
d.setdefault("tags", []).append("py")     # створює [], якщо нема, і повертає його
d.setdefault("tags", []).append("swift")  # вже існує — повертає той самий список
d                                          # {'tags': ['py', 'swift']}
```

Для накопичення `setdefault` працює, але для цього зазвичай чистіший
`collections.defaultdict` (див. §8 і рецепти).

---

## 3. Мутація

```python
d = {"a": 1}
d["b"] = 2                      # додати/перезаписати
d.update({"c": 3}, d=4)         # масово: {'a': 1, 'b': 2, 'c': 3, 'd': 4}

d.pop("a")                      # 1        — видалити й повернути
d.pop("z", -1)                  # -1       — дефолт, якщо ключа нема (без KeyError)
d.popitem()                     # ('d', 4) — видалити ОСТАННЮ вставлену пару (LIFO)
del d["c"]                      # видалити без повернення (KeyError, якщо нема)
d.clear()                       # спорожнити
```

### Оператори злиття `|` та `|=` (3.9+)

```python
a = {"x": 1, "y": 2}
b = {"y": 20, "z": 3}

a | b      # {'x': 1, 'y': 20, 'z': 3}   — новий dict, праве перемагає
a |= b     # мутує a на місці (як a.update(b))
```

> **⚠️ Пастка №2.** При злитті за конфлікту ключів **перемагає правий** операнд
> (останній). Тому `defaults | overrides` (overrides виграють), а не навпаки —
> порядок не комутативний.

---

## 4. Перевірка наявності: `in` за КЛЮЧАМИ

```python
d = {"a": 1}
"a" in d        # True
1 in d          # False   — перевіряє КЛЮЧІ, не значення!
```

Перевірка `in` — O(1) у середньому (хеш-таблиця), як `Dictionary` у Swift. Щоб
шукати **за значенням**, потрібен `1 in d.values()` (це вже O(n)).

---

## 5. Ітерація

За замовчуванням ітерація словника дає **ключі**:

```python
d = {"a": 1, "b": 2}
list(d)              # ['a', 'b']   — keys за замовчуванням
list(d.keys())       # ['a', 'b']
list(d.values())     # [1, 2]
list(d.items())      # [('a', 1), ('b', 2)]

for k, v in d.items():    # ідіоматичний обхід пар
    ...
```

`.keys()`, `.values()`, `.items()` повертають **живі view-об'єкти**: вони не
копіюють дані, а відображають поточний стан словника.

```python
d = {"a": 1}
v = d.keys()
d["b"] = 2
list(v)              # ['a', 'b']   — view побачив зміну
```

> **⚠️ Пастка №3.** Не можна **змінювати розмір** словника під час ітерації:
> ```python
> for k in d:
>     d[k + "_"] = 0    # ❌ RuntimeError: dictionary changed size during iteration
> ```
> Ітеруй по копії ключів — `for k in list(d):` — або збирай зміни окремо й
> застосовуй після циклу.

---

## 6. Ключі мають бути hashable (незмінні)

Ключем може бути лише **hashable** об'єкт: `str`, `int`, `float`, `bool`,
`tuple` (з hashable елементів), `frozenset`. Мутабельні `list`/`dict`/`set` —
не можна.

```python
d = {}
d[(1, 2)] = "tuple ok"          # кортеж — ок
d[42] = "int ok"
d[[1, 2]] = "nope"
# ❌ TypeError: unhashable type: 'list'  (3.14 додає префікс "cannot use 'list' as a dict key")
```

Це аналог Swift-вимоги `Key: Hashable`, лише перевіряється в рантаймі, а не
компілятором. Як зробити власний клас придатним для ключа (`__hash__` +
`__eq__`) — [Модуль 05](../05-classes-and-oop.md).

---

## 7. Злиття словників

```python
defaults  = {"color": "red", "size": "M"}
overrides = {"size": "L"}

{**defaults, **overrides}    # {'color': 'red', 'size': 'L'}   — overrides виграли
defaults | overrides         # те саме (3.9+)

{**overrides, **defaults}    # {'size': 'M', 'color': 'red'}   — ⚠️ defaults виграли!
```

Обидва способи (`{**a, **b}` і `a | b`) рівноцінні; `|` читабельніший. Головне —
пам'ятати про §3: за конфлікту перемагає **останній** словник.

---

## 8. Comprehension і сортування — коротко

Інверсія (поміняти ключі зі значеннями) і фільтрація:

```python
d = {"a": 1, "b": 2}
{v: k for k, v in d.items()}            # {1: 'a', 2: 'b'}   — інверсія
{k: v for k, v in d.items() if v > 1}   # {'b': 2}           — фільтрація
```

> **⚠️ Пастка №4.** Інверсія губить пари, якщо значення не унікальні
> (два ключі з однаковим значенням → лишиться один). Деталі — [comprehensions.md](comprehensions.md).

Словник не сортується «на місці» (він упорядкований за вставкою) — сортуй
`.items()` і збирай назад:

```python
from operator import itemgetter
scores = {"math": 90, "art": 85, "cs": 95}
dict(sorted(scores.items(), key=itemgetter(1), reverse=True))
# {'cs': 95, 'math': 90, 'art': 85}
max(scores, key=scores.get)             # 'cs'   — ключ з макс. значенням
```

Повна історія про `key=`, стабільність, кілька ключів — [sorting.md](sorting.md).

---

## 9. Вкладені словники й спільні референси

`dict` — референс-тип, тож «копія» через `dict(...)` або `|` — **поверхнева**:
вкладені об'єкти лишаються спільними.

```python
import copy
base = {"cfg": {"debug": False}}

shallow = dict(base)            # поверхнева копія
shallow["cfg"]["debug"] = True
base["cfg"]["debug"]            # True   — ⚠️ вкладений dict СПІЛЬНИЙ!

deep = copy.deepcopy(base)      # глибока копія
deep["cfg"]["debug"] = False
base["cfg"]["debug"]            # True   — base незалежний від deep
```

> **⚠️ Пастка №5.** У Swift `Dictionary` — value-тип: присвоєння копіює (CoW), і
> вкладені структури теж. У Python присвоєння словника — це **спільний референс**,
> а `dict(x)`/`x.copy()` копіюють лише верхній рівень. Для повної незалежності —
> `copy.deepcopy`.

---

## 10. Продуктивність

| Операція | Складність |
|----------|------------|
| `d[k]`, `k in d`, `d[k] = v`, `del d[k]` | O(1) у середньому |
| ітерація | O(n) |
| `value in d.values()` | O(n) — лінійний пошук |

Це та сама хеш-таблиця, що й Swift `Dictionary`. Платою за швидкість і
впорядкованість є пам'ять: `dict` помітно «важчий» за `list` тих самих даних. Для
тисяч однотипних записів зі сталим набором полів розглянь `@dataclass(slots=True)`
([Модуль 06](../06-structs-and-value-types.md)) замість словника-на-запис.

---

## Шпаргалка / рецепти

```python
# Безпечний доступ
d.get(k, default)                        # без KeyError
d.setdefault(k, []).append(x)            # взяти-або-створити список

# Підрахунок частот
counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1     # {'a': 3, 'b': 2, 'c': 1}
# або ідіоматично:
from collections import Counter
Counter(words)                           # Counter({'a': 3, 'b': 2, 'c': 1})
Counter(words).most_common(2)            # [('a', 3), ('b', 2)]

# Групування
from collections import defaultdict
groups = defaultdict(list)
for cat, item in pairs:
    groups[cat].append(item)             # {'fruit': ['apple', 'pear'], 'veg': [...]}

# Інверсія / злиття з дефолтами
{v: k for k, v in d.items()}             # поміняти ключі та значення
{**defaults, **overrides}                # overrides перемагають
config = defaults | user_config          # те саме (3.9+)

# Сортування за значенням
dict(sorted(d.items(), key=lambda kv: kv[1], reverse=True))
max(d, key=d.get)                        # ключ з макс. значенням
```

> **Best practice.** Для підрахунку — `collections.Counter`; для групування й
> накопичення — `collections.defaultdict(list)`/`(int)`: вони уникають
> `KeyError` без зайвого `setdefault`/`get`. Звичайний `dict` лиши для
> «справжніх» мап ключ→значення.

## Див. також

- [Модуль 03 — Структури даних](../03-data-structures.md) — list/dict/set/tuple.
- [sorting.md](sorting.md) — сортування `.items()`, `key=`, стабільність.
- [comprehensions.md](comprehensions.md) — dict comprehension, інверсія, фільтрація.
- [conversions.md](conversions.md) — `dict(zip(...))`, `dict.fromkeys`, пари ⇄ dict.
- [set.md](set.md) — `set`/`frozenset`, hashable-елементи, дедуплікація.
- [Модуль 05 — Класи](../05-classes-and-oop.md) — `__hash__`/`__eq__` для власних ключів.
- [Тематичний індекс](../INDEX.md).
</content>
</invoke>
