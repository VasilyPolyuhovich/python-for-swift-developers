# Модуль 09. Ітератори та генератори

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 09**

Туторіал: [§9.8–9.10](https://docs.python.org/uk/3/tutorial/classes.html#iterators).

Ітерування в Python мапляться на Swift `Sequence`/`IteratorProtocol`, але Python
додає **генератори** (`yield`) — потужний синтаксис для ліниво обчислюваних
послідовностей, близький до Swift `AsyncSequence`/lazy, але набагато компактніший.

## 1. Протокол ітерування

### Swift
```swift
struct Countdown: Sequence, IteratorProtocol {
    var current: Int
    mutating func next() -> Int? {
        guard current > 0 else { return nil }
        defer { current -= 1 }
        return current
    }
}
```

### Python (ручна реалізація)
```python
from collections.abc import Iterator

class Countdown:
    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self) -> Iterator[int]:    # повертає ітератор
        return self

    def __next__(self) -> int:              # наступний елемент
        if self.current <= 0:
            raise StopIteration             # ⚠️ КІНЕЦЬ — через виняток, не None!
        value = self.current
        self.current -= 1
        return value

for n in Countdown(3):
    print(n)            # 3, 2, 1
```

> **⚠️ Пастка.** Кінець ітерації позначається **винятком `StopIteration`**, а не
> поверненням `nil`/`None`, як у Swift. `for` ловить його автоматично. Це
> незвично, але рідко пишеться вручну — бо є генератори.

### Iterable vs Iterator — і чому це впливає на повторні проходи

Це два різні поняття:
- **Iterable** (`__iter__`) — «по мені можна ітерувати»; повертає *новий* ітератор.
- **Iterator** (`__iter__` + `__next__`) — сам процес проходу; **одноразовий**.

У прикладі `Countdown` вище клас є *і тим, і тим* (`__iter__` повертає `self`) —
тому по ньому можна пройти лише **раз**. Щоб об'єкт можна було ітерувати
**багаторазово**, `__iter__` має повертати **новий** ітератор щоразу:

```python
class Squares:
    def __init__(self, n: int) -> None:
        self.n = n
    def __iter__(self):
        return (i * i for i in range(self.n))   # НОВИЙ генератор щоразу

sq = Squares(3)
list(sq)        # [0, 1, 4]
list(sq)        # [0, 1, 4]  — знову працює (на відміну від голого генератора)
```

> **Best practice.** Якщо твій тип — це колекція, по якій ітеруватимуть не раз,
> роби його **iterable** (повертай новий ітератор у `__iter__`), а не самим
> iterator. Це і є контракт Swift `Sequence` (багаторазового) vs одноразового
> `IteratorProtocol`.

### `iter(callable, sentinel)` — ітерувати до стоп-значення

Маловідома, але корисна форма `iter`: викликати функцію, поки вона не поверне
sentinel. Ідеально для читання потоків блоками:

```python
# читати по 1024 байти, поки не порожньо
for chunk in iter(lambda: f.read(1024), b""):
    process(chunk)

data = iter([1, 2, 0, 3])
list(iter(lambda: next(data), 0))      # [1, 2]  — зупинка на sentinel 0
```

## 2. Генератори — `yield` (головний інструмент)

Замість ручного класу-ітератора Python пропонує функцію з `yield`. Це найідіоматичніший
спосіб створити ліниву послідовність.

```python
from collections.abc import Iterator

def countdown(start: int) -> Iterator[int]:
    current = start
    while current > 0:
        yield current          # "віддає" значення й ПАУЗУЄ тут
        current -= 1

for n in countdown(3):
    print(n)            # 3, 2, 1
```

`yield` робить функцію генератором: при виклику вона не виконується одразу, а
повертає об'єкт-генератор. Кожна ітерація виконує тіло **до наступного `yield`**,
запам'ятовуючи стан. Це аналог coroutine-подібної ліні.

Безкінечні послідовності — безпечно, бо ліниво:

```python
def naturals() -> Iterator[int]:
    n = 1
    while True:            # безкінечно, але ОК — обчислюється на вимогу
        yield n
        n += 1

import itertools
first_five = list(itertools.islice(naturals(), 5))    # [1,2,3,4,5]
```

```swift
// Swift-аналог — lazy sequence:
let firstFive = Array(sequence(first: 1) { $0 + 1 }.prefix(5))
```

## 3. Generator expressions — лінива версія comprehension

```python
squares_list = [x * x for x in range(1_000_000)]    # СПИСОК: уся пам'ять одразу
squares_gen = (x * x for x in range(1_000_000))     # ГЕНЕРАТОР: ліниво, майже 0 пам'яті

total = sum(x * x for x in range(1_000_000))        # можна без зайвих дужок як аргумент
```

> **Best practice.** Коли результат одразу споживається (`sum`, `any`, `max`,
> цикл) — використовуй generator expression `(...)`, не list `[...]`. Економить
> пам'ять і часто швидше. Це як `.lazy` у Swift, але за замовчуванням компактніше.

## 4. `yield from` — делегування

```python
def chain_ranges() -> Iterator[int]:
    yield from range(3)        # 0,1,2
    yield from range(10, 13)   # 10,11,12
    # еквівалент вкладеного циклу з yield
```

## 4b. Генератор як корутина: `send`, `throw`, `close`, `return`

Генератор — двосторонній канал: можна не лише брати з нього, а й **слати** в
нього значення через `.send()`. Це основа корутин (на цьому колись будувався
`asyncio`):

```python
def echo():
    while True:
        received = yield          # yield-вираз ПОВЕРТАЄ те, що прислали
        print("got", received)

e = echo()
next(e)            # "прокрутити" до першого yield (обов'язково)
e.send("a")        # got a
e.send("b")        # got b
e.close()          # зупинити генератор (кине GeneratorExit усередині)
```

Генератор може **повертати** значення (через `return`) — воно потрапляє в
`StopIteration.value` (і саме його бере `yield from`):

```python
def gen():
    yield 1
    return "done"          # не значення ітерації, а підсумок

g = gen()
next(g)                    # 1
try:
    next(g)
except StopIteration as e:
    e.value                # 'done'
```

> `.throw(Exc)` кидає виняток усередину генератора (у точці `yield`) — рідко
> потрібно вручну, але на цьому стоять контекст-менеджери з `@contextmanager`
> ([Модуль 10](10-errors-and-exceptions.md)).

## 5. itertools — стандартна бібліотека ітерування

`itertools` — це аналог комбінаторів зі Swift (`prefix`, `dropFirst`, `zip`,
`flatMap`), але набагато ширший. Усе ліниве.

```python
import itertools as it

it.count(10)                      # 10, 11, 12, ... (безкінечно)
it.cycle([1, 2, 3])               # 1,2,3,1,2,3,... (безкінечно)
it.repeat("x", 3)                 # x, x, x
it.islice(gen, 5)                 # перші 5 (~ .prefix(5))
it.chain([1, 2], [3, 4])          # 1,2,3,4 (~ flatMap по послідовностях)
it.takewhile(lambda x: x < 5, xs) # поки умова (~ prefix(while:))
it.dropwhile(lambda x: x < 5, xs) # після того як умова стала хибною
it.groupby(sorted_data, key=fn)   # групування підряд
it.product([1, 2], ["a", "b"])    # декартів добуток
it.combinations(range(4), 2)      # комбінації
it.permutations([1, 2, 3])        # перестановки
it.accumulate([1, 2, 3, 4])       # 1,3,6,10 (~ reduce з проміжними)
it.pairwise([1, 2, 3, 4])         # (1,2),(2,3),(3,4) — сусідні пари (3.10+)
it.batched(range(7), 3)           # (0,1,2),(3,4,5),(6,) — порціями (3.12+)
it.starmap(pow, [(2, 3), (2, 4)]) # 8, 16 — map із розпакуванням аргументів
it.zip_longest([1, 2], [3], fillvalue=0)   # (1,3),(2,0) — zip без обрізання
it.chain.from_iterable([[1, 2], [3]])      # 1,2,3 — flatten списку списків
it.filterfalse(lambda x: x % 2, range(6))  # 0,2,4 — інверсія filter
it.tee(iterable, 2)               # роздвоїти ітератор на 2 незалежні
```

> **Best practice.** Перш ніж писати власний цикл — перевір, чи немає готового в
> `itertools`. Це швидкий C-код і читабельніший намір. `batched` — частий кейс
> «обробити по N»; `pairwise` — «порівняти із сусідом».

> **⚠️ Пастка `tee`.** `it.tee` буферизує елементи, щоб «роздвоїти» ітератор —
> якщо одну гілку споживають набагато швидше за іншу, буфер росте. І **не**
> використовуй оригінальний ітератор після `tee`.

## 6. Корисні вбудовані функції ітерування

```python
sum(nums)                         # сума
max(nums), min(nums)              # макс/мін
any(x > 0 for x in nums)          # хоч один (~ contains(where:))
all(x > 0 for x in nums)          # усі (~ allSatisfy)
sorted(nums, key=fn)              # відсортований список
reversed(seq)                     # зворотний ітератор
enumerate(seq)                    # (index, value) пари
zip(a, b)                         # паралельна ітерація (~ zip)
map(fn, seq)                      # ліниве застосування
filter(pred, seq)                 # лінива фільтрація
```

> **⚠️ Пастка.** Ітератор/генератор **одноразовий**: пройшовши по ньому раз, він
> вичерпується.
> ```python
> gen = (x for x in range(3))
> list(gen)        # [0, 1, 2]
> list(gen)        # []  — вже вичерпано!
> ```
> На відміну від Swift `Sequence`, по якій можна часто ітерувати повторно. Якщо
> треба кілька проходів — матеріалізуй у `list(...)` або зроби клас-iterable, що
> повертає новий ітератор у `__iter__`.

## 7. Async-генератори (анонс)

Для асинхронних потоків даних є `async def` + `yield` — прямий аналог Swift
`AsyncSequence`. Детально — у [Модулі 12](12-async.md):

```python
async def fetch_pages() -> AsyncIterator[str]:
    for url in urls:
        yield await fetch(url)

async for page in fetch_pages():      # ~ for await ... in (Swift)
    ...
```

## Інструменти та бібліотеки

- **`itertools`** (stdlib) — комбінатори ітерування (lazy).
- **`functools.reduce`** — згортка (аналог `reduce`).
- **`more-itertools`** (PyPI) — розширення: `chunked`, `windowed`, `flatten`,
  `unique_everseen` тощо. Дуже корисно для обробки потоків.
- **`collections.abc.Iterator`/`Iterable`** — типи для анотацій.

## Best practices модуля

- Для лінивих послідовностей пиши генератори (`yield`), а не ручні класи-ітератори.
- Generator expressions `(...)` коли результат одразу споживається — економія пам'яті.
- Спирайся на `itertools` замість ручних циклів-комбінаторів.
- Пам'ятай: генератор одноразовий; для повторних проходів — матеріалізуй або
  зроби iterable-клас.
- `any`/`all`/`sum`/`sorted` із генераторами — ідіоматично й ефективно.
- Для багаторазової ітерації — iterable (новий ітератор у `__iter__`), не iterator.
- `iter(callable, sentinel)` для читання потоків до стоп-значення.

## Див. також

- [Модуль 02 — Функції](02-functions.md) — генератор-функції, `yield` vs `return`.
- [Модуль 03 · Comprehensions](03-data-structures/comprehensions.md) — generator expressions.
- [Модуль 05 · Dunder](05-classes-and-oop/dunder-methods.md) — `__iter__`/`__next__`/`__contains__`.
- [Модуль 10 — Помилки](10-errors-and-exceptions.md) — `@contextmanager` на генераторах.
- [Модуль 12 — Async](12-async.md) — `async`-генератори, `async for`.
- [Модуль 13 — Stdlib](13-stdlib-and-ecosystem.md) — `itertools`, `more-itertools`.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 10 — Помилки та винятки](10-errors-and-exceptions.md)
