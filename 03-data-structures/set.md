# Множини: `set` і `frozenset`

[← Курс](../README.md) · [Модуль 03](../03-data-structures.md) · **set**

У Swift `Set` — це колекція **унікальних**, `Hashable` елементів, value-тип
(копіюється за значенням). Python `set` дуже схожий ідеєю — унікальні **hashable**
елементи, O(1)-перевірка наявності — але з двома важливими відмінностями:
він **невпорядкований** (не «недетермінований Swift Set», а принципово без
поняття позиції) і це **mutable reference-тип**. Для незмінного, hashable
варіанта є `frozenset` (його можна класти ключем у `dict` чи елементом в інший
`set`).

---

## 1. Створення і пастка з `{}`

```python
{1, 2, 3}              # {1, 2, 3}
set([1, 1, 2, 3])      # {1, 2, 3}      — дедуплікація з ітерабельного
set("hello")           # {'e','h','l','o'}  — ⚠️ порядок НЕ гарантований
sorted(set("hello"))   # ['e', 'h', 'l', 'o']  — для показу сортуй
```

```swift
let s: Set = [1, 1, 2, 3]   // {1, 2, 3}
let chars = Set("hello")    // {"h", "e", "l", "o"}
```

> **⚠️ Пастка №1.** `{}` — це **порожній `dict`, а НЕ порожня множина**!
> `type({})` → `dict`. Для порожньої множини є тільки `set()`:
> ```python
> type({})       # <class 'dict'>
> type(set())    # <class 'set'>
> ```

---

## 2. Елементи мають бути hashable

Як і у Swift (де елемент має бути `Hashable`), елемент Python-множини має бути
hashable. Незмінні вбудовані типи (`int`, `str`, `tuple`, `frozenset`) — так;
змінні (`list`, `dict`, `set`) — ні.

```python
{(1, 2), (3, 4)}       # ок — кортежі hashable
{frozenset([1, 2])}    # ок — frozenset hashable

{[1, 2]}               # ❌ TypeError: unhashable type: 'list'
```

Якщо треба «множина списків» — конвертуй елементи у `tuple` чи `frozenset`.
Як зробити власний клас hashable (`__hash__`/`__eq__`) — [Модуль 05](../05-classes-and-oop.md).

---

## 3. Зміна вмісту: `add`, `discard` vs `remove`, `pop`

```python
s = {1, 2, 3}
s.add(4)               # {1, 2, 3, 4}
s.discard(10)          # тиша — елемента не було, помилки НЕМАЄ
s.remove(99)           # ❌ KeyError: 99 — remove вимагає наявності
s.update([10, 11])     # додати всі елементи ітерабельного
s.clear()              # {}  (порожня множина)
```

| Метод | Якщо елемента немає | Повертає |
|-------|---------------------|----------|
| `discard(x)` | нічого (безпечно) | `None` |
| `remove(x)` | `KeyError` | `None` |
| `pop()` | `KeyError` (на порожній) | **довільний** елемент |

> **⚠️ Пастка №2.** `set.pop()` **не** має аргумента й повертає **довільний**
> елемент (не «останній», бо порядку немає). Не покладайся на те, який саме —
> для детермінованого вибору сортуй: `min(s)` / `sorted(s)[0]`.

---

## 4. Алгебра множин: оператори і метод-форми

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b      # об'єднання        {1, 2, 3, 4, 5, 6}
a & b      # перетин           {3, 4}
a - b      # різниця           {1, 2}
a ^ b      # симетрична різниця {1, 2, 5, 6}
```

```swift
a.union(b); a.intersection(b); a.subtracting(b); a.symmetricDifference(b)
```

Кожному оператору відповідає метод (`.union`, `.intersection`, `.difference`,
`.symmetric_difference`) і **in-place**-форма (`|=`, `&=`, `-=`, `^=`):

```python
s = {1, 2, 3}
s |= {4, 5}        # {1, 2, 3, 4, 5}   об'єднати на місці
s &= {1, 2, 4}     # {1, 2, 4}         лишити перетин
s -= {1}           # {2, 4}            прибрати
s ^= {2, 99}       # {4, 99}           симетрична різниця
```

> **⚠️ Пастка №3.** **Оператори** вимагають, щоб обидві сторони були множинами;
> **метод-форми** приймають будь-яке ітерабельне:
> ```python
> a | [5, 6]              # ❌ TypeError: unsupported operand type(s) for |
> a.union([5, 6, 7])      # ок → {1, 2, 3, 4, 5, 6, 7}
> a.intersection([3, 4])  # ок → {3, 4}
> ```

---

## 5. Підмножина / надмножина / неперетин

```python
{1, 2} <= {1, 2, 3}       # True   — підмножина (issubset)
{1, 2} <  {1, 2}          # False  — строга підмножина (не дорівнює)
{1, 2, 3} >= {1, 2}       # True   — надмножина (issuperset)
{1, 2}.issubset({1, 2, 3})    # True   — метод приймає будь-яке ітерабельне
{1, 2}.isdisjoint({3, 4})     # True   — немає спільних елементів
```

Аналоги Swift: `a.isSubset(of: b)`, `a.isSuperset(of: b)`, `a.isDisjoint(with: b)`.

---

## 6. Головна причина — O(1) `in`

Основний привід тягнути `set` замість `list` — миттєва перевірка наявності.
Пошук у `list` лінійний (O(n)), у `set` — у середньому константний (O(1)),
бо це хеш-таблиця.

```python
2 in {1, 2, 3}      # True — O(1) у середньому
2 in [1, 2, 3]      # True — O(n), сканує список
```

> **Best practice.** Якщо колекцію використовуєш переважно для перевірок
> `x in coll`, або тримаєш набір «бачених» значень — бери `set`, а не `list`.
> Для великих наборів різниця колосальна.

---

## 7. Типові застосування

```python
# дедуплікація
items = [3, 1, 2, 1, 3, 2]
list(set(items))            # [1, 2, 3]  — ⚠️ порядок НЕ гарантований
list(dict.fromkeys(items))  # [3, 1, 2]  — зберігає порядок першої появи
```

> **Ідіома дедуплікації.** `list(set(x))` найкоротший, але **губить порядок**.
> Коли порядок важливий — `list(dict.fromkeys(x))` (деталі — [conversions.md](conversions.md)).

```python
# права/теги через алгебру множин
required  = {"read", "write", "admin"}
granted   = {"read", "write"}
missing   = required - granted          # {'admin'} — чого бракує
has_any   = bool(required & granted)    # True — є хоч один збіг
```

---

## 8. `frozenset` — незмінна й hashable

`frozenset` — це `set`, який не можна змінювати; натомість він hashable, тож
його **можна класти ключем у `dict` або елементом в інший `set`**. Усі
read-операції (`|`, `&`, `<=`, `in`, …) працюють; мутуючих (`add`, `update`) немає.

```python
fs = frozenset([1, 2, 3])
fs.add(4)          # ❌ AttributeError: 'frozenset' object has no attribute 'add'

# frozenset як ключ словника: набір прав → роль
roles = {frozenset({"read", "write"}): "editor"}
roles[frozenset({"write", "read"})]    # 'editor'  — порядок у ключі не важить
```

У Swift роль «незмінний hashable Set» грає сам `Set` (value-тип уже hashable);
у Python для цього потрібен саме `frozenset`, бо звичайний `set` unhashable.

---

## 9. Set comprehension

Як list/dict comprehension, але у фігурних дужках — результат автоматично
дедуплікований (деталі та правила — [comprehensions.md](comprehensions.md)):

```python
{x % 5 for x in range(20)}     # {0, 1, 2, 3, 4}
sorted({x % 5 for x in range(20)})   # [0, 1, 2, 3, 4]  — для показу
```

---

## Продуктивність

| Операція | Складність (середня) |
|----------|----------------------|
| `x in s` | O(1) |
| `s.add(x)` | O(1) |
| `s.discard(x)` / `s.remove(x)` | O(1) |
| `a | b`, `a & b`, `a - b` | O(len) задіяних |
| `x in list` (для контрасту) | O(n) |

> **⚠️ Пастка №4.** Множина **невпорядкована** — індексації немає:
> `s[0]` → `TypeError: 'set' object is not subscriptable`. Потрібен порядок —
> конвертуй у `list`/`sorted(s)`. Потрібен і порядок, і унікальність зразу —
> бери `dict.fromkeys(...)` (див. §7).

---

## Шпаргалка / рецепти

```python
set()                          # порожня множина ({} — це dict!)
{1, 2, 3}                      # літерал
set(iterable)                  # дедуплікація з ітерабельного
list(set(items))               # унікальні (порядок НЕ гарантований)
list(dict.fromkeys(items))     # унікальні зі збереженням порядку
x in s                         # O(1) перевірка наявності
s.add(x); s.discard(x)         # додати / прибрати без помилки
a | b   a & b   a - b   a ^ b  # union / intersect / diff / sym-diff
a <= b   a.isdisjoint(b)       # підмножина / неперетин
{f(x) for x in it if cond}     # set comprehension
frozenset(items)               # незмінна, hashable — ключ dict / елемент set
```

## Див. також

- [Модуль 03 — Структури даних](../03-data-structures.md) — list/dict/set/tuple.
- [Словники — `dict`](dict.md) — hash-таблиця з ключами й значеннями, `dict.fromkeys`.
- [Конвертації](conversions.md) — `set()`/`frozenset()`/`list()`, ідіома дедуплікації.
- [Модуль 05 — Класи](../05-classes-and-oop.md) — `__hash__`/`__eq__` для власних hashable-типів.
- [Тематичний індекс](../INDEX.md).
</content>
</invoke>
