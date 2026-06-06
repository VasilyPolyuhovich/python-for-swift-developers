[← Курс](../README.md) · [Модуль 05](../05-classes-and-oop.md) · **Dunder-методи**

«Dunder» = **d**ouble **under**score (`__name__`). Це гачки, через які Python
вбудовує твій тип у мову: `+`, `==`, `len()`, `for`, `with`, `[]`, виклик `()`.
У Swift це робота **протоколів** (`Equatable`, `Comparable`, `ExpressibleByX`,
`subscript`, `callable`); у Python — набір спеціальних методів. Дві ключові
відмінності від Swift:

- Це **duck typing, а не номінальні протоколи**: тип «вміє ітеруватися», якщо
  має `__iter__`, незалежно від ієрархії. Не треба оголошувати конформність.
- Інтерпретатор шукає dunder-методи **на типі**, а не на екземплярі: `len(x)`
  кличе `type(x).__len__(x)`, а не `x.__len__`.

Нижче — повний каталог за категоріями. Майже все це для класів-«даних»
згенерує `@dataclass` ([Модуль 06](../06-structs-and-value-types.md)) — пиши
руками лише там, де потрібна нестандартна семантика.

---

## 1. Життєвий цикл та представлення

### `__init__` / `__new__`

`__init__` — це **ініціалізатор** (об'єкт уже створено), а не конструктор.
Створенням займається `__new__` (рідко перевизначається — для immutable-типів,
синглтонів, метакласів). 99% часу пишеш лише `__init__` (див.
[Модуль 05 §1](../05-classes-and-oop.md)). `__new__` детально —
[дескриптори та метакласи](descriptors-and-metaclasses.md).

### `__repr__` vs `__str__` vs `__format__`

| Метод | Хто кличе | Swift-аналог | Призначення |
|-------|-----------|--------------|-------------|
| `__repr__` | `repr()`, REPL, дебагер, `repr` у контейнерах | `CustomDebugStringConvertible` | однозначне, для розробника |
| `__str__` | `str()`, `print()`, `f"{x}"` (як fallback) | `CustomStringConvertible` | читабельне, для користувача |
| `__format__` | `format()`, `f"{x:spec}"` | `String(format:)` / spec | форматування зі спецификатором |

```python
class Money:
    def __init__(self, cents: int) -> None:
        self.cents = cents

    def __repr__(self) -> str:                  # завжди визначай це
        return f"Money(cents={self.cents})"

    def __str__(self) -> str:                   # для print/користувача
        return f"${self.cents / 100:.2f}"

    def __format__(self, spec: str) -> str:     # f"{m:spec}"
        if spec == "full":
            return f"{self.cents} cents"
        return format(self.cents / 100, spec)   # делегуємо float

m = Money(1599)
repr(m)        # 'Money(cents=1599)'
str(m)         # '$15.99'
f"{m}"         # '15.99'   ← порожній spec → __format__("") → format(15.99, "")
f"{m:.1f}"     # '16.0'
f"{m:full}"    # '1599 cents'
```

> **⚠️ Пастка: f-string кличе `__format__`, не `__str__`.** `f"{m}"`
> (без spec) йде у `__format__("")`, а не в `__str__`. У базовому `object`
> `__format__("")` повертає `str(self)`, тож якщо `__format__` не визначати —
> усе працює очікувано. Але **визначивши `__format__`, не забудь обробити
> порожній spec**, інакше `print(m)` і `f"{m}"` дадуть різний результат.

```swift
// Swift: два окремі протоколи
struct Money: CustomStringConvertible, CustomDebugStringConvertible {
    let cents: Int
    var description: String { String(format: "$%.2f", Double(cents)/100) }
    var debugDescription: String { "Money(cents: \(cents))" }
}
```

Якщо `__str__` не визначено, `str()`/`print()` **падають назад на `__repr__`**.
Тому одного `__repr__` достатньо для базового дебагу:

```python
class NoStr:
    def __repr__(self) -> str: return "NoStr()"
str(NoStr())   # 'NoStr()'  — fallback на __repr__
```

`__bytes__` викликається `bytes(obj)` — серіалізація у байти:

```python
class Money:
    def __init__(self, c): self.cents = c
    def __bytes__(self) -> bytes:
        return self.cents.to_bytes(4, "big")
bytes(Money(1599))   # b'\x00\x00\x06?'
```

> **Best practice.** **Завжди визначай `__repr__`** — це безцінно в логах,
> дебагері й під час падінь у тестах. `__str__` додавай лише коли потрібне
> окреме «людське» представлення.

---

## 2. Рівність та впорядкування

### `__eq__` і правило `NotImplemented`

`__eq__` — аналог `Equatable`. Для «чужого» типу повертай **`NotImplemented`**
(не `False`!): тоді Python спробує `other.__eq__(self)`, і лише якщо й там
`NotImplemented` — повертає `False`. Це дозволяє іншому типу визначити рівність
із твоїм.

```python
class Money:
    def __init__(self, cents): self.cents = cents
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented            # НЕ False
        return self.cents == other.cents
    def __hash__(self) -> int:
        return hash(self.cents)

Money(100) == Money(100)   # True
Money(100) == 100          # False  (NotImplemented → fallback → False)
Money(100) == "x"          # False
```

### `__hash__` — правило, яке кусає

**Визначивши `__eq__`, ти втрачаєш успадкований `__hash__`** — клас стає
**нехешованим** (його не можна покласти в `set`/dict-ключ). Логіка: рівні
об'єкти зобов'язані мати рівний хеш, і Python не вгадає твою рівність:

```python
class Pt:
    def __init__(self, x): self.x = x
    def __eq__(self, other):
        return isinstance(other, Pt) and self.x == other.x
    # __hash__ НЕ визначено

{Pt(1)}        # TypeError: unhashable type: 'Pt'  (3.14 додає "cannot use 'Pt' as a set element")
Pt.__hash__    # None  ← саме так Python «прибирає» хеш
```

Три варіанти дій:

- **Незмінний value-тип** → визнач `__hash__` на тих самих полях, що й `__eq__`.
- **Mutable-об'єкт** → залиш нехешованим (`__hash__ = None` явно). Хешований
  mutable — баг: зміниш поле, і об'єкт «загубиться» в set.
- Хочеш дефолтну identity-рівність — не визначай `__eq__` взагалі.

```python
class Money:
    def __init__(self, c): self.cents = c
    def __eq__(self, o): return isinstance(o, Money) and self.cents == o.cents
    def __hash__(self): return hash(self.cents)   # ті самі поля, що в __eq__

len({Money(100), Money(100), Money(200)})   # 2  — дедуплікація працює
```

Це прямо стосується set/dict-ключів із [Модуля 03](../03-data-structures.md):
ключем словника може бути лише хешований об'єкт. У Swift це `Hashable` +
`Equatable` разом.

### Впорядкування: `__lt__`/`__le__`/`__gt__`/`__ge__` + `total_ordering`

Для сортування й порівнянь (`Comparable`). Python для `sorted()` достатньо
`__lt__`. Щоб не писати всі шість методів вручну — `functools.total_ordering`
згенерує решту з `__eq__` + `__lt__`:

```python
from functools import total_ordering

@total_ordering                  # генерує >, >=, <= з __eq__ і __lt__
class Version:
    def __init__(self, major, minor):
        self.major, self.minor = major, minor
    def __eq__(self, o):
        return (self.major, self.minor) == (o.major, o.minor)
    def __lt__(self, o):
        return (self.major, self.minor) < (o.major, o.minor)

Version(1, 2) <= Version(1, 3)   # True
Version(2, 0) > Version(1, 9)    # True
sorted([Version(2,0), Version(1,5)])   # працює без key=
```

```swift
// Swift: Comparable дає всі оператори з одного <
struct Version: Comparable {
    let major, minor: Int
    static func < (l: Version, r: Version) -> Bool {
        (l.major, l.minor) < (r.major, r.minor)
    }
}
```

> **Best practice.** `@total_ordering` зручний, але повільніший за повний
> ручний набір. Для record-типів `@dataclass(order=True, frozen=True)` генерує
> `__eq__`, усі порівняння **і** `__hash__` автоматично —
> [Модуль 06](../06-structs-and-value-types.md). Пиши dunder-и руками лише за
> нестандартної семантики.

---

## 3. Числові оператори

Бінарні (`__add__`, `__sub__`, `__mul__`, `__truediv__` для `/`,
`__floordiv__` для `//`, `__mod__` для `%`, `__pow__` для `**`) та унарні
(`__neg__` для `-x`, `__abs__` для `abs(x)`).

**Reflected** (`__radd__`, `__rmul__`, …) кличеться, коли лівий операнд **не
вміє** додавати правий: для `3 * v` Python спершу пробує `int.__mul__(3, v)`
(повертає `NotImplemented`), потім `v.__rmul__(3)`.

**In-place** (`__iadd__`, `__imul__`, …) — для `+=`. Якщо `__iadd__` не
визначено, `x += y` стає `x = x + y` (нове прив'язування через `__add__`).

```python
class Vec:
    def __init__(self, x, y): self.x, self.y = x, y
    def __repr__(self): return f"Vec({self.x}, {self.y})"
    def __eq__(self, o): return isinstance(o, Vec) and (self.x,self.y)==(o.x,o.y)
    def __add__(self, o):                       # v + w
        if isinstance(o, Vec): return Vec(self.x+o.x, self.y+o.y)
        return NotImplemented
    def __mul__(self, s):  return Vec(self.x*s, self.y*s)    # v * 3
    def __rmul__(self, s): return self.__mul__(s)           # 3 * v
    def __neg__(self):     return Vec(-self.x, -self.y)     # -v
    def __abs__(self):     return (self.x**2 + self.y**2) ** 0.5

Vec(1, 2) + Vec(3, 4)   # Vec(4, 6)
Vec(1, 2) * 3           # Vec(3, 6)   — __mul__
3 * Vec(1, 2)           # Vec(3, 6)   — __rmul__ (int не знає Vec)
-Vec(1, 2)              # Vec(-1, -2)
abs(Vec(3, 4))          # 5.0
```

Без `__iadd__` оператор `+=` створює **новий** об'єкт (як value-семантика):

```python
a = Vec(0, 0); b = a
a += Vec(1, 1)          # a = a + Vec(1,1) через __add__
a, b, a is b            # (Vec(1, 1), Vec(0, 0), False)  ← b не змінився
```

> **⚠️ Пастка: reflected повертає `NotImplemented`, а не кидає виняток.**
> Якщо забути `__radd__`/`__rmul__`, то `3 * v` дасть `TypeError`, навіть коли
> `v * 3` працює. Для комутативних операцій реалізуй обидва (`__rmul__ =
> __mul__` як скорочення).

---

## 4. Протокол контейнера

| Метод | Операція | Swift-аналог |
|-------|----------|--------------|
| `__len__` | `len(x)` | `count` (Collection) |
| `__getitem__` | `x[i]`, `x[a:b]` | `subscript(_:) { get }` |
| `__setitem__` | `x[i] = v` | `subscript(_:) { set }` |
| `__delitem__` | `del x[i]` | — |
| `__contains__` | `v in x` | `contains(_:)` |
| `__iter__` | `for v in x` | `Sequence` / `makeIterator()` |

```python
class Vector:
    def __init__(self, *comps): self._c = list(comps)
    def __repr__(self):        return f"Vector{tuple(self._c)}"
    def __len__(self):         return len(self._c)
    def __getitem__(self, i):  return self._c[i]      # підтримує і slice
    def __setitem__(self, i, v): self._c[i] = v
    def __delitem__(self, i):  del self._c[i]
    def __contains__(self, v): return v in self._c
    def __iter__(self):        return iter(self._c)

v = Vector(1, 2, 3, 4)
len(v)              # 4
v[1]                # 2
v[1:3]              # [2, 3]   — slice прокидається у list
v[0] = 99           # __setitem__  → Vector(99, 2, 3, 4)
del v[0]            # __delitem__  → Vector(2, 3, 4)
3 in v              # True      — __contains__
[x*2 for x in v]    # [4, 6, 8] — __iter__
```

```swift
// Swift: subscript + Sequence
struct Vector: Sequence {
    private var c: [Double]
    subscript(i: Int) -> Double {
        get { c[i] } set { c[i] = newValue }
    }
    func makeIterator() -> IndexingIterator<[Double]> { c.makeIterator() }
}
```

> **Best practice.** Якщо немає `__iter__`, але є `__getitem__` з цілими
> індексами від 0, Python усе одно зітерує (старий протокол послідовності).
> Але краще явно дати `__iter__`. Повноцінний ітератор з `__next__`,
> генератори й лінива ітерація — [Модуль 09](../09-iterators-and-generators.md).

---

## 5. Доступ до атрибутів

| Метод | Коли кличеться | Ризик |
|-------|----------------|-------|
| `__getattribute__` | на **кожен** доступ `x.attr` | легко зациклити |
| `__getattr__` | лише коли звичайний пошук **не знайшов** | безпечніший |
| `__setattr__` | на кожне `x.attr = v` | легко зациклити |
| `__delattr__` | на `del x.attr` | |
| `__dir__` | `dir(x)` | |

`__getattr__` — головний інструмент проксі/динамічних атрибутів. Кличеться
**тільки на промах** звичайного пошуку:

```python
class Proxy:
    def __init__(self, data): self._data = data
    def __getattr__(self, name):              # лише коли атрибут НЕ знайдено
        return self._data.get(name)

p = Proxy({"foo": 1})
p._data        # {'foo': 1}  — знайдено напряму, __getattr__ не кличеться
p.foo          # 1           — промах атрибута → __getattr__ → _data["foo"]
p.bar          # None        — промах → _data.get("bar")
```

`__getattribute__` перехоплює **геть усе** (навіть `self._data`), тому всередині
треба делегувати в `super()`, інакше — нескінченна рекурсія:

```python
class Logged:
    def __getattribute__(self, name):
        print(f"access: {name}")
        return super().__getattribute__(name)   # делегуємо, НЕ self.<...>
```

> **⚠️ Пастка: нескінченна рекурсія в `__setattr__`.** Усередині `__setattr__`
> рядок `self.name = value` знову кличе `__setattr__` → стек переповнюється.
> Виправлення — `super().__setattr__(...)` або пряма робота з `self.__dict__`:
>
> ```python
> class Bad:
>     def __setattr__(self, name, value):
>         self.__dict__[name] = value      # ✅ обходить __setattr__
>         # self.name = value              # ❌ нескінченна рекурсія
> ```

Типове застосування — frozen-об'єкт (immutability через заборону присвоєнь):

```python
class Frozen:
    def __init__(self, x):
        super().__setattr__("x", x)        # обходимо власний __setattr__
    def __setattr__(self, name, value):
        raise AttributeError("frozen")

f = Frozen(7)
f.x            # 7
f.x = 9        # AttributeError: frozen
```

`__dir__` кастомізує вивід `dir()` (Python його **сортує**):

```python
class WithDir:
    def __dir__(self): return ["custom", "attrs"]
dir(WithDir())   # ['attrs', 'custom']
```

---

## 6. Callable — об'єкт як функція

`__call__` робить екземпляр викликуваним: `obj(args)` → `obj.__call__(args)`.
Це функтор зі станом (аналог Swift `callAsFunction`):

```python
class Multiplier:
    def __init__(self, factor): self.factor = factor
    def __call__(self, x): return x * self.factor

double = Multiplier(2)
double(21)          # 42
callable(double)    # True
```

```swift
// Swift: callAsFunction
struct Multiplier {
    let factor: Int
    func callAsFunction(_ x: Int) -> Int { x * factor }
}
let double = Multiplier(factor: 2); double(21)   // 42
```

Декоратори-класи, кешувальники, конфігуровані стратегії — типові кейси для
`__call__`.

---

## 7. Контекст-менеджер

`__enter__`/`__exit__` обслуговують `with` — детермінований cleanup (як Swift
`defer`, але прив'язаний до блоку). `__exit__` отримує деталі винятку (або три
`None`, якщо без винятку) і керує його придушенням через return-значення:

```python
class Timer:
    def __enter__(self):
        print("enter"); return self            # значення йде в 'as'
    def __exit__(self, exc_type, exc, tb):
        print("exit", exc_type)
        return False                           # НЕ придушувати виняток

with Timer() as t:
    print("body")
# enter / body / exit None
```

> **Best practice.** `return True` з `__exit__` **проковтне** виняток — роби це
> свідомо. Для простих менеджерів зручніший `@contextlib.contextmanager`
> поверх генератора. Деталі та обробка винятків — [Модуль 10](../10-errors-and-exceptions.md).

---

## 8. Конвертації та істинність

`__bool__` визначає істинність в `if`/`while`. Якщо його немає — Python
**падає назад на `__len__`** (порожній контейнер = `False`); якщо немає й
`__len__` — об'єкт завжди `True`.

```python
class Box:
    def __init__(self, items): self.items = items
    def __len__(self): return len(self.items)    # bool падає назад на len

bool(Box([]))     # False
bool(Box([1]))    # True
```

`__int__` (`int(x)`), `__float__` (`float(x)`), `__index__` (для **точного**
цілочисельного контексту: зрізи, `bin()`/`hex()`, `range`):

```python
class Temp:
    def __init__(self, c): self.c = c
    def __bool__(self):  return self.c != 0
    def __int__(self):   return int(self.c)
    def __float__(self): return float(self.c)
    def __index__(self): return int(self.c)      # для slice/hex/bin

bool(Temp(0))               # False
int(Temp(3.7))              # 3
float(Temp(3))              # 3.0
["a","b","c","d"][Temp(2):] # ['c', 'd']   — __index__ у зрізі
hex(Temp(255))              # '0xff'        — __index__
```

> **⚠️ Пастка: `__index__` ≠ `__int__`.** Зрізи й `hex()`/`bin()` вимагають
> **`__index__`**, а не `__int__`. `__int__` — для «лосі» конвертації
> (як `Int(x)`); `__index__` каже «я **є** цілим без втрат» — Python не
> приймає `float.__index__`, тому `x[1.0:]` падає, а кастомний `__index__`
> працює.

---

## 9. Кастомізація класів (тизер)

Просунуті гачки, що керують **створенням і поведінкою самих класів**, а не
екземплярів:

- **`__init_subclass__`** — кличеться при оголошенні **підкласу** (реєстрація
  плагінів, валідація ієрархії) — легша альтернатива метакласу.
- **`__set_name__`** — дескриптор дізнається ім'я, під яким його присвоїли в
  класі (основа `@property`-подібних об'єктів).
- **`__class_getitem__`** — `MyClass[int]` (узагальнені типи, [Модуль 07](../07-generics.md)).
- **метаклас `__call__`** — перехоплює `MyClass(...)` (синглтони, кешування
  екземплярів).

Усе це — окрема тема: [дескриптори, `__slots__`, метакласи, MRO](descriptors-and-metaclasses.md).

---

## Шпаргалка / рецепти

| Категорія | Dunder | Викликає | Swift-аналог |
|-----------|--------|----------|--------------|
| **Життєвий цикл** | `__init__` | `T(...)` | `init` |
| | `__new__` | створення (рідко) | `init` (immutable/factory) |
| **Представлення** | `__repr__` | `repr()`, REPL, дебаг | `CustomDebugStringConvertible` |
| | `__str__` | `str()`, `print()` | `CustomStringConvertible` |
| | `__format__` | `f"{x:spec}"`, `format()` | `String(format:)` |
| | `__bytes__` | `bytes()` | — |
| **Рівність** | `__eq__` | `==` (→ `NotImplemented`!) | `Equatable` |
| | `__hash__` | `hash()`, set/dict-ключ | `Hashable` |
| **Порядок** | `__lt__` `__le__` `__gt__` `__ge__` | `<` `<=` `>` `>=` | `Comparable` |
| | `@total_ordering` | генерує решту з `<`+`==` | (Comparable дає все з `<`) |
| **Числа** | `__add__` `__sub__` `__mul__` | `+` `-` `*` | оператори |
| | `__truediv__` `__floordiv__` `__mod__` `__pow__` | `/` `//` `%` `**` | |
| | `__neg__` `__abs__` | `-x` `abs(x)` | |
| | `__radd__` … | reflected (`3 * v`) | — |
| | `__iadd__` … | in-place (`+=`) | — |
| **Контейнер** | `__len__` | `len(x)` | `count` |
| | `__getitem__` `__setitem__` `__delitem__` | `x[i]`, `x[i]=v`, `del x[i]` | `subscript` |
| | `__contains__` | `v in x` | `contains` |
| | `__iter__` | `for v in x` | `Sequence` |
| **Атрибути** | `__getattr__` | доступ на **промах** | `dynamicMemberLookup` |
| | `__getattribute__` | **кожен** доступ | — |
| | `__setattr__` `__delattr__` | `x.a=v`, `del x.a` | — |
| | `__dir__` | `dir(x)` | — |
| **Виклик** | `__call__` | `x(...)` | `callAsFunction` |
| **Контекст** | `__enter__` `__exit__` | `with x:` | (`defer`) |
| **Конвертації** | `__bool__` | `if x:` (fallback `__len__`) | (немає) |
| | `__int__` `__float__` `__index__` | `int()` `float()` / зрізи | `ExpressibleByX` (обернено) |
| **Класи** | `__init_subclass__` `__set_name__` `__class_getitem__` | оголошення/дескриптори/generics | — |

```python
# Мінімальний value-тип уручну (краще @dataclass — Модуль 06):
class T:
    def __init__(self, ...): ...
    def __repr__(self): ...               # ЗАВЖДИ
    def __eq__(self, o):                  # → NotImplemented для чужого типу
        if not isinstance(o, T): return NotImplemented
        ...
    def __hash__(self): ...               # ті самі поля, що в __eq__ (або = None)
```

## Див. також

- [Модуль 05 — Класи та ООП](../05-classes-and-oop.md) — базові класи, `@property`, спадкування.
- [Дескриптори, `__slots__`, метакласи, MRO](descriptors-and-metaclasses.md) — `__new__`, `__set_name__`, `__init_subclass__`, метакласи зсередини.
- [Модуль 06 — Value-типи](../06-structs-and-value-types.md) — `@dataclass` генерує `__init__`/`__repr__`/`__eq__`/`__hash__`/порядок автоматично.
- [Модуль 09 — Ітератори та генератори](../09-iterators-and-generators.md) — повний `__iter__`/`__next__`, лінива ітерація.
- [Модуль 10 — Помилки та винятки](../10-errors-and-exceptions.md) — `__enter__`/`__exit__`, `@contextmanager`.
- [Тематичний індекс](../INDEX.md).
