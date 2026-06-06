# Модуль 07. Дженеріки

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 07**

Дженеріки в Python мапляться на Swift майже один-до-одного. З Python 3.12
([PEP 695](https://peps.python.org/pep-0695/)) синтаксис став майже ідентичним
Swift. Це один із наймиліших для Swift-розробника модулів.

> Дженеріки — суто **компайл-тайм** інструмент (для `pyright`/`mypy`). У рантаймі
> Python їх «стирає» (type erasure). Тобто це контракт для аналізатора, а не
> рантайм-перевірка — як generics у Swift не несуть оверхеду, але тут навіть
> сильніше: інформація про тип у рантаймі недоступна.

## 1. Дженерик-функції

### Swift
```swift
func first<T>(_ items: [T]) -> T? {
    items.first
}
```

### Python (3.12+, PEP 695)
```python
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None
```

Синтаксис `[T]` після імені — точний аналог `<T>` у Swift. До 3.12 потрібен був
явний `TypeVar`:

```python
from typing import TypeVar
T = TypeVar("T")

def first(items: list[T]) -> T | None:    # старий стиль
    return items[0] if items else None
```

> **Best practice.** Для нового коду (3.12+) використовуй PEP 695-синтаксис
> (`def f[T](...)`). Він локальний, читабельніший і збігається зі Swift.

## 2. Дженерик-класи

### Swift
```swift
struct Stack<Element> {
    private var items: [Element] = []
    mutating func push(_ item: Element) { items.append(item) }
    mutating func pop() -> Element? { items.popLast() }
}
```

### Python
```python
from dataclasses import dataclass, field

class Stack[T]:                          # PEP 695: параметр типу в [ ]
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T | None:
        return self._items.pop() if self._items else None

s: Stack[int] = Stack()
s.push(1)
s.push(2)
s.pop()              # 2  (pyright знає, що це int | None)
```

## 3. Обмеження типів (bounds / constraints)

### Swift — `where` clause / protocol constraint
```swift
func maxElement<T: Comparable>(_ items: [T]) -> T? {
    items.max()
}
```

### Python — bound на TypeVar
```python
def largest[T: (int, float)](items: list[T]) -> T:   # T обмежений int або float
    return max(items)
```

Bound через протокол (структурне обмеження, аналог `T: Comparable`):

```python
from typing import Protocol

class Comparable(Protocol):
    def __lt__(self, other: object) -> bool: ...

def maximum[T: Comparable](items: list[T]) -> T:     # T має підтримувати <
    result = items[0]
    for x in items[1:]:
        if result < x:
            result = x
    return result
```

Два види обмежень:

```python
def f[T: SomeBase](x: T) -> T: ...           # bound: T — підтип SomeBase
def g[T: (int, str)](x: T) -> T: ...         # constraint: T — РІВНО int АБО str
```

> **⚠️ Пастка.** `[T: (int, str)]` (у дужках) — це *constraint* (T — точно один із
> переліку). `[T: SomeBase]` (без дужок) — це *bound* (T — будь-який підтип). У
> Swift немає прямого аналога constraint-форми; найближче — generic із обмеженням
> протоколом.

## 4. Кілька параметрів типу

### Swift
```swift
struct Pair<A, B> {
    let first: A
    let second: B
}
```

### Python
```python
@dataclass(frozen=True)
class Pair[A, B]:
    first: A
    second: B

p: Pair[int, str] = Pair(1, "one")
```

## 5. Дженерик-протоколи

Протоколи теж можуть бути дженериками (детально — Модуль 08):

```python
from typing import Protocol

class Container[T](Protocol):
    def get(self, index: int) -> T: ...
    def add(self, item: T) -> None: ...
```

Аналог Swift протоколу з associated type:

```swift
protocol Container {
    associatedtype Item
    func get(at index: Int) -> Item
    mutating func add(_ item: Item)
}
```

> **Примітка.** У Swift associated types та generic protocols — окремі механізми
> з відомими складнощами (`some`/`any`, type erasure). У Python дженерик-протоколи
> простіші: просто параметризуєш протокол `[T]`.

## 6. Дженерик type alias (зокрема рекурсивні)

```python
type Pair[T] = tuple[T, T]          # PEP 695 generic alias
type Result[T] = T | Exception

coords: Pair[float] = (1.0, 2.0)

# Рекурсивний аліас — посилається на себе (для деревоподібних даних, JSON):
type Json = dict[str, "Json"] | list["Json"] | str | int | float | bool | None
data: Json = {"a": [1, 2, {"b": None}]}      # валідно для pyright
```

## 6b. `ParamSpec` і `TypeVarTuple` — спеціальні параметри

Окрім звичайного `T`, PEP 695 дає два особливі види параметрів:

```python
from collections.abc import Callable
from functools import wraps

# **P (ParamSpec) — захопити ВСЮ сигнатуру (args + kwargs). Для декораторів:
def trace[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        return fn(*args, **kwargs)
    return inner

# *Ts (TypeVarTuple) — змінна кількість параметрів типу (variadic generics):
def first[T, *Ts](x: T, *rest: *Ts) -> T:
    return x

first(1, "a", 2.0)        # pyright знає, що результат — int
```

`ParamSpec` — основа типобезпечних декораторів
([декоратори](02-functions/decorators.md)). `TypeVarTuple` рідкісніший — для
функцій над кортежами довільної форми (типу операцій над тензорами в ML).

До 3.12 їх писали явно: `P = ParamSpec("P")`, `Ts = TypeVarTuple("Ts")`.

## 7. Варіантність (variance) — коротко

`pyright` виводить варіантність автоматично для PEP 695-дженериків. Якщо коротко:

- **Коваріантність**: `list[Dog]` *не є* `list[Animal]` (бо list mutable —
  invariant). А от `Sequence[Dog]` сумісний із `Sequence[Animal]` (read-only,
  covariant).
- Це аналогічно до того, як у Swift `Array<Dog>` не підставляється замість
  `Array<Animal>`.

```python
from collections.abc import Sequence

def describe(animals: Sequence[Animal]) -> None: ...

dogs: list[Dog] = [...]
describe(dogs)        # OK: Sequence коваріантний; list — підтип Sequence
```

> **Best practice.** Приймай коваріантні read-only типи (`Sequence`, `Iterable`,
> `Mapping`) у параметрах функцій — це робить API гнучкішим, як приймання
> `some Sequence` у Swift.

Для PEP 695 варіантність виводиться автоматично. У старому стилі її задавали
вручну при оголошенні `TypeVar`:

```python
from typing import TypeVar
T_co = TypeVar("T_co", covariant=True)        # producer (тільки повертає)
T_contra = TypeVar("T_contra", contravariant=True)   # consumer (тільки приймає)
```

> **Правило великого пальця:** якщо тип лише **видає** значення `T` (producer) —
> коваріантний; якщо лише **приймає** `T` (consumer, як `Callable[[T], ...]`) —
> контраваріантний; якщо й те, й те (mutable-контейнер) — інваріантний.

## 8. Self type — повернення власного типу

Для fluent-API та factory-методів, що повертають точний підтип:

```python
from typing import Self

class QueryBuilder:
    def where(self, cond: str) -> Self:      # повертає точний підтип
        ...
        return self

    def limit(self, n: int) -> Self:
        ...
        return self
```

Аналог Swift `Self` у протоколах / методах, що повертають `Self`.

## Інструменти та бібліотеки

- **`typing`** — `TypeVar`, `Generic`, `ParamSpec` (для типізації декораторів),
  `Self`, `TypeVarTuple` (variadic generics).
- **`pyright`/`mypy`** — без них дженеріки безглузді: уся перевірка тут.

## Best practices модуля

- Новий код — PEP 695-синтаксис (`def f[T]`, `class C[T]`). Найближче до Swift.
- Обмежуй типи через bound (`[T: Base]`) або протокол (structural constraint).
- Приймай коваріантні read-only типи (`Sequence`, `Mapping`) у параметрах.
- `Self` для fluent-API.
- Пам'ятай про type erasure: у рантаймі параметр типу недоступний — не покладайся
  на нього в логіці виконання:
  ```python
  class Box[T]:
      def __init__(self, v: T) -> None: self.v = v
  b = Box[int](5)
  type(b).__name__        # 'Box'        — параметр стерто
  isinstance(b, Box)      # True
  # isinstance(b, Box[int])   # ❌ TypeError — не можна перевіряти параметризований тип
  ```

## Див. також

- [Модуль 02 · Декоратори](02-functions/decorators.md) — `ParamSpec` на практиці.
- [Модуль 04 — Типи](04-types-and-typing.md) — `TypeVar`, аліаси, `cast`, варіантність.
- [Модуль 08 — Протоколи](08-protocols-and-interfaces.md) — дженерик-протоколи, `Self`, structural typing.
- [Модуль 03 — Структури даних](03-data-structures.md) — `Sequence`/`Mapping` коваріантність на практиці.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 08 — Інтерфейси / протоколи](08-protocols-and-interfaces.md)
