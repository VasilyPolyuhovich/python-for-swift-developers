# Модуль 08. Інтерфейси / протоколи

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 08**

Це найцікавіший модуль для Swift-розробника, бо в Python є **два** механізми, що
покривають роль Swift `protocol`, і вони фундаментально різні за філософією:

- **`Protocol`** — *structural* typing (duck typing): «якщо крякає як качка — це
  качка». Тип підходить, бо має потрібні методи, **не оголошуючи** про це явно.
- **`ABC`** (Abstract Base Class) — *nominal* typing: тип підходить, бо **явно
  успадковує** базовий клас.

Swift протоколи — **nominal**: тип мусить явно написати `: Equatable`. Python
`Protocol` — навпаки, structural. Це найбільший зсув мислення.

## 1. Protocol — structural typing (головний інструмент)

### Swift (nominal — потрібне явне оголошення)
```swift
protocol Drawable {
    func draw() -> String
}

struct Circle: Drawable {        // ЯВНО заявляє відповідність
    func draw() -> String { "○" }
}
```

### Python (structural — відповідність неявна)
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

# Circle НЕ успадковує Drawable і НЕ знає про нього!
class Circle:
    def draw(self) -> str:
        return "○"

def render(item: Drawable) -> None:    # приймає будь-що з методом draw()
    print(item.draw())

render(Circle())        # OK! Circle структурно відповідає Drawable
```

`Circle` ніде не згадує `Drawable`, але `pyright` бачить, що в нього є метод
`draw(self) -> str`, і дозволяє передати його в `render`. **Відповідність — за
формою, не за оголошенням.**

> **⚠️ Найважливіша пастка/інсайт.** У Swift ти декларуєш відповідність
> (`struct Circle: Drawable`). У Python із `Protocol` цього не треба — тип
> «підходить» автоматично, якщо має потрібні члени. Це дозволяє типізувати
> класи, які ти **не контролюєш** (наприклад, із чужих бібліотек) — чого у Swift
> досягають через retroactive conformance (`extension SomeType: Drawable`).

### Чому це потужно

Можна писати протоколи постфактум для вже наявних типів:

```python
class SupportsClose(Protocol):
    def close(self) -> None: ...

def cleanup(resource: SupportsClose) -> None:
    resource.close()

# Працює з file, socket, своїми класами — будь-чим, що має close()
cleanup(open("data.txt"))
```

### Протоколи з атрибутами, властивостями та композиція

Протокол описує не лише методи, а й **атрибути** та **властивості**:

```python
class HasName(Protocol):
    name: str                          # вимога: атрибут name: str
    @property
    def label(self) -> str: ...        # вимога: властивість label

class User:
    name = "Vasyl"
    @property
    def label(self) -> str:
        return self.name.upper()

def greet(o: HasName) -> str:
    return o.label

greet(User())        # 'VASYL'  — User структурно відповідає HasName
```

Протоколи **комбінуються** через множинне успадкування (усі мусять мати
`Protocol` у базах):

```python
class Readable(Protocol):
    def read(self) -> bytes: ...
class Writable(Protocol):
    def write(self, b: bytes) -> None: ...

class ReadWrite(Readable, Writable, Protocol): ...   # композиція двох протоколів

def copy_stream(rw: ReadWrite) -> None:              # вимагає і read, і write
    rw.write(rw.read())
```

Це аналог Swift `typealias ReadWrite = Readable & Writable` (композиція протоколів).

## 2. ABC — nominal typing (коли потрібна явність)

Якщо хочеш Swift-подібну явну відповідність + спільну реалізацію:

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def describe(self) -> str:               # СПІЛЬНА реалізація (як protocol extension)
        return f"area={self.area()}, perimeter={self.perimeter()}"

class Rectangle(Shape):                      # ЯВНО успадковує
    def __init__(self, w: float, h: float) -> None:
        self.w, self.h = w, h

    def area(self) -> float:
        return self.w * self.h

    def perimeter(self) -> float:
        return 2 * (self.w + self.h)

# Shape()           # ПОМИЛКА в рантаймі: не можна інстанціювати абстрактний клас
# class Bad(Shape): pass; Bad()   # ПОМИЛКА: не реалізовано abstractmethod
```

`ABC` дає те, чого `Protocol` не дає:

- **Рантайм-примус**: не можна створити екземпляр без реалізації абстрактних
  методів (Protocol такого не перевіряє в рантаймі).
- **Явність**: `class Rectangle(Shape)` декларує намір, як у Swift.
- Спільні реалізовані методи (`describe`) — аналог protocol extension зі Swift.

### Абстрактні property, classmethod, staticmethod

`@abstractmethod` комбінується з іншими декораторами (порядок: `@abstractmethod`
**знизу**):

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @property
    @abstractmethod
    def legs(self) -> int: ...           # абстрактна властивість

    @classmethod
    @abstractmethod
    def species(cls) -> str: ...         # абстрактний метод класу

class Dog(Animal):
    @property
    def legs(self) -> int: return 4
    @classmethod
    def species(cls) -> str: return "dog"

Animal()    # TypeError: Can't instantiate abstract class Animal ...
```

### `register` — віртуальні підкласи (nominal без спадкування)

`ABC` дозволяє оголосити «чужий» клас своїм підкласом **без** спадкування — щось
середнє між structural і nominal:

```python
class Quacker(ABC):
    @abstractmethod
    def quack(self) -> str: ...

class Duck:                       # НЕ успадковує Quacker
    def quack(self) -> str: return "quack"

Quacker.register(Duck)            # оголошуємо Duck віртуальним підкласом
issubclass(Duck, Quacker)         # True
isinstance(Duck(), Quacker)       # True
```

> **⚠️ Пастка.** `register` робить `isinstance`/`issubclass` істинними, але
> **не** перевіряє, що методи реально є, і **не** дає успадкованих реалізацій. Це
> інструмент для інтеграції з кодом, який ти не можеш змінити. Саме так
> `collections.abc` оголошує `list`/`dict` своїми підкласами.

(Глибший механізм — `__subclasshook__`, який дозволяє ABC самому вирішувати, хто
його підклас, за наявністю методів. Це advanced; зазвичай достатньо `register`
або `Protocol`.)

## 3. Protocol vs ABC — коли що

| Критерій | `Protocol` (structural) | `ABC` (nominal) |
|----------|-------------------------|-----------------|
| Відповідність | неявна, за формою | явна, через спадкування |
| Типізувати чужі класи | так | ні (треба змінити клас) |
| Рантайм-примус реалізації | ні | так |
| Спільна реалізація методів | обмежено | так |
| Філософія | duck typing, Pythonic | OOP, Java/Swift-подібно |
| Аналог Swift | protocol + retroactive conformance | protocol + базовий клас |

> **Best practice.**
> - За замовчуванням бери **`Protocol`** — це Pythonic, гнучко, дозволяє duck
>   typing і типізацію чужого коду.
> - Бери **`ABC`**, коли потрібен рантайм-примус «усі підкласи МУСЯТЬ реалізувати
>   X» або значна спільна реалізація в базовому класі (framework/template method).

## 4. runtime_checkable — isinstance із протоколом

За замовчуванням `isinstance(x, MyProtocol)` не працює. Щоб увімкнути:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

isinstance(open("f"), Closeable)     # True (перевіряє НАЯВНІСТЬ методу close)
```

> **⚠️ Пастка.** `runtime_checkable` перевіряє лише *наявність* атрибутів/методів
> за іменем, **не їхні сигнатури**. Об'єкт із методом `close(self, force, extra)`
> теж пройде. Тож це слабша перевірка, ніж компайл-тайм. Використовуй обережно.

## 5. Стандартні протоколи (collections.abc)

Замість того, щоб винаходити свої, спирайся на готові протоколи stdlib — аналоги
`Sequence`, `Collection`, `IteratorProtocol` зі Swift:

```python
from collections.abc import (
    Iterable,      # __iter__         ~ Sequence (мінімум)
    Iterator,      # __iter__, __next__
    Sequence,      # індексоване + len  ~ Collection
    Mapping,       # read-only dict-подібне
    MutableMapping,
    Callable,      # викликане        ~ (Args) -> Result
    Hashable,      # __hash__         ~ Hashable
)

def process(data: Iterable[int]) -> int:    # приймає list, set, generator, tuple...
    return sum(data)
```

Свій клас стає повноцінною колекцією, реалізувавши потрібні dunder-методи
(structural) або успадкувавши ABC:

```python
from collections.abc import Sequence

class ReadonlyList[T](Sequence[T]):          # успадкування ABC дає купу методів безплатно
    def __init__(self, items: list[T]) -> None:
        self._items = items

    def __getitem__(self, index: int) -> T:   # реалізуєш 2 методи...
        return self._items[index]

    def __len__(self) -> int:
        return len(self._items)
    # ...а __contains__, __iter__, __reversed__, index, count — отримуєш безплатно
```

Це аналог того, як у Swift відповідність `Collection` дає масу методів за замовчуванням.

## 6. Protocol-oriented дизайн (твоя стихія)

Як і у Swift, у Python протоколи + композиція кращі за глибокі ієрархії
спадкування. Типовий патерн — dependency injection через протокол:

```python
from typing import Protocol

class UserRepository(Protocol):              # "інтерфейс" залежності
    def get(self, user_id: int) -> dict[str, str]: ...
    def save(self, user: dict[str, str]) -> None: ...

class Service:
    def __init__(self, repo: UserRepository) -> None:   # ін'єкція протоколу
        self._repo = repo

    def rename(self, user_id: int, name: str) -> None:
        user = self._repo.get(user_id)
        user["name"] = name
        self._repo.save(user)

# У тестах підставляєш будь-який клас із потрібними методами — без спадкування
class FakeRepo:
    def get(self, user_id: int) -> dict[str, str]: return {"id": str(user_id)}
    def save(self, user: dict[str, str]) -> None: pass

Service(FakeRepo())        # працює — structural typing робить мокінг тривіальним
```

> **Best practice.** Це найкраща практика для тестованого коду: залежності —
> через `Protocol`, не конкретні класи. Structural typing робить підстановку
> моків елементарною (не треба успадковувати від інтерфейсу, як у Swift/Java).

## Інструменти та бібліотеки

- **`typing.Protocol`**, **`abc.ABC`** — stdlib, основа.
- **`collections.abc`** — готові протоколи колекцій (використовуй їх, не винаходь).
- **`typing.runtime_checkable`** — для `isinstance` з протоколом.
- DI-фреймворки: зазвичай **не потрібні** — structural typing + конструктори
  покривають 95% потреб. Для складних випадків — `dependency-injector`, `punq`.

## Best practices модуля

- За замовчуванням — `Protocol` (structural, Pythonic, типізує й чужий код).
- `ABC` — коли треба рантайм-примус або значна спільна реалізація.
- `@runtime_checkable` лише за потреби `isinstance`; пам'ятай про слабкість перевірки.
- Спирайся на готові протоколи `collections.abc`.
- Залежності ін'єктуй через `Protocol` — це робить код тестованим без спадкування.
- `ABC.register` — для інтеграції з класами, які не можеш змінити.
- Абстрактні `@property`/`@classmethod` — `@abstractmethod` знизу.

## Див. також

- [Модуль 05 — Класи](05-classes-and-oop.md) — спадкування, MRO, dunder-методи.
- [Модуль 05 · Дескриптори/метакласи](05-classes-and-oop/descriptors-and-metaclasses.md) — `ABCMeta`, `__subclasshook__`, `__init_subclass__`.
- [Модуль 07 — Дженеріки](07-generics.md) — дженерик-протоколи, `Self`.
- [Модуль 09 — Ітератори](09-iterators-and-generators.md) — `Iterable`/`Iterator` протоколи.
- [Модуль 04 — Типи](04-types-and-typing.md) — `collections.abc` як анотації.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 09 — Ітератори та генератори](09-iterators-and-generators.md)
