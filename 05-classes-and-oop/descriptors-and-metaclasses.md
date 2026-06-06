[← Курс](../README.md) · [Модуль 05](../05-classes-and-oop.md) · **Дескриптори та метакласи**

Це сторінка про «нутрощі» класів Python: як `@property` працює зсередини, що
таке дескриптори, навіщо `__slots__`, як реєструвати підкласи без метакласів і
як насправді влаштований `super()` з MRO.

> **Чесно про застосовність.** Більшість прикладного коду **ніколи** не пише
> власних дескрипторів і метакласів. Але цей механізм живить речі, якими ти
> користуєшся щодня: `@property`, `@cached_property`, `@dataclass`, `enum`, ORM
> (SQLAlchemy, Django models), валідатори Pydantic. Мета цієї сторінки — щоб ти
> розумів машинерію й не лякався, коли її побачиш у traceback чи чужому коді.

---

## 1. Дескриптори — протокол `__get__`/`__set__`/`__set_name__`

**Дескриптор** — це об'єкт, що визначає, як атрибут читається/записується/
видаляється, через спеціальні методи. Коли такий об'єкт лежить **на рівні
класу**, Python викликає його методи замість звичайного доступу до `__dict__`.

Найближчий аналог зі Swift — **property wrapper** (`@propertyWrapper`).
Дескриптор так само інкапсулює логіку get/set і перевикористовується на багатьох
полях. Різниця: у Swift wrapper огортає тип значення (`@Clamped var x: Int`), у
Python дескриптор — це окремий клас-об'єкт, що сидить атрибутом класу.

### `@property` — це теж дескриптор

```python
class C:
    @property
    def x(self): return 1

print(type(C.__dict__['x']))                              # <class 'property'>
print(hasattr(C.__dict__['x'], '__get__'),
      hasattr(C.__dict__['x'], '__set__'))                # True True
```

`property` — звичайний клас, що реалізує протокол дескриптора. `@property` не
магія компілятора (як computed property у Swift), а об'єкт, що сидить у
`C.__dict__['x']` і перехоплює доступ. Ти можеш написати власний.

### Свій валідований дескриптор — «чому» дескрипторів

Сила дескрипторів — **перевикористання** логіки доступу на кількох атрибутах.
Якщо тобі потрібна та сама валідація на трьох полях, `@property` доведеться
писати тричі. Дескриптор пишеться раз:

```python
class Positive:
    def __set_name__(self, owner, name):       # викликається при створенні КЛАСУ
        self._name = "_" + name                # де зберігати значення в екземплярі

    def __get__(self, obj, objtype=None):
        if obj is None:                         # доступ через КЛАС, не екземпляр
            return self
        return getattr(obj, self._name)

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self._name[1:]} must be positive, got {value}")
        setattr(obj, self._name, value)

class Account:
    balance = Positive()                        # один дескриптор...
    rate = Positive()                           # ...перевикористаний на двох полях

    def __init__(self, balance, rate):
        self.balance = balance                  # йде через Positive.__set__
        self.rate = rate

a = Account(100, 5)
print(a.balance, a.rate)                        # 100 5
a.balance = -10                                 # ValueError: balance must be positive, got -10
```

Три методи протоколу:

- `__set_name__(self, owner, name)` — Python викликає його **автоматично** при
  створенні класу, передаючи ім'я, під яким дескриптор присвоєно (`"balance"`).
  Так дескриптор дізнається своє ім'я й не дублює його вручну.
- `__get__(self, obj, objtype)` — читання. `obj is None` означає доступ через
  клас (`Account.balance`) — за конвенцією повертаємо сам дескриптор.
- `__set__(self, obj, value)` — запис із валідацією.

> **⚠️ Пастка — рекурсія в `__set__`.** Не зберігай значення в атрибут із тим
> самим іменем (`obj.balance = value` всередині `Positive.__set__`) — це
> рекурсивно покличе `__set__` знову. Зберігай під **іншим** ім'ям (тут
> `_balance`) або в `obj.__dict__[...]` напряму.

### Data vs non-data дескриптори (і пріоритет над `__dict__`)

Це тонкість, яка пояснює магію `cached_property`. Дескриптор буває двох видів:

- **Data-дескриптор** — має `__set__` (або `__delete__`). Має **пріоритет над**
  `__dict__` екземпляра. Саме тому `@property` не можна «затінити» присвоєнням.
- **Non-data дескриптор** — має лише `__get__`. `__dict__` екземпляра має
  пріоритет **над ним**.

```python
class DataDesc:
    def __get__(self, obj, objtype=None): return "from descriptor"
    def __set__(self, obj, value): pass

class NonDataDesc:
    def __get__(self, obj, objtype=None): return "from descriptor"

class A:
    d = DataDesc()
    n = NonDataDesc()

a = A()
a.__dict__['d'] = "from instance dict"          # пишемо напряму в __dict__
a.__dict__['n'] = "from instance dict"
print("data:", a.d)                             # data: from descriptor   (дескриптор виграв)
print("non-data:", a.n)                         # non-data: from instance dict  (__dict__ виграв)
```

Порядок пошуку атрибута: **data-дескриптор класу → `__dict__` екземпляра →
non-data дескриптор класу → `__getattr__`**.

### Чому `functools.cached_property` працює саме так

`cached_property` — **non-data дескриптор** (має `__get__`, але не `__set__`).
Це і є механізм кешування: при першому доступі він обчислює значення і записує
його **в `__dict__` екземпляра під тим самим іменем**. Оскільки дескриптор
non-data, наступні читання беруться з `__dict__` (швидко) і дескриптор більше не
викликається.

```python
from functools import cached_property
class Box:
    @cached_property
    def total(self):
        print("computing")
        return 42

b = Box()
print(hasattr(Box.__dict__['total'], '__set__'))   # False  → non-data
print(b.total)                                      # computing → 42
print(b.total)                                      # 42  (без "computing")
print('total' in b.__dict__)                        # True — закешовано в екземплярі
```

> **Best practice.** Хочеш просту валідацію на одному полі — `@property`. Хочеш
> ту саму логіку доступу на багатьох полях/класах — дескриптор. Кешування
> дорогого незмінного результату — `@cached_property` (детальніше про нього —
> [хаб модуля, §3](../05-classes-and-oop.md#3-properties--обчислювані-та-контрольовані-атрибути)).

---

## 2. `__slots__` — економія пам'яті без `__dict__`

За замовчуванням кожен екземпляр тримає `__dict__` — словник атрибутів. Це гнучко
(можна додати будь-який атрибут будь-коли), але дорого: словник споживає пам'ять.
`__slots__` каже Python: «атрибути цього класу фіксовані, зберігай їх у
компактних слотах, без `__dict__`».

```python
import sys

class WithDict:
    def __init__(self, x, y):
        self.x = x; self.y = y

class WithSlots:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x; self.y = y

a = WithDict(1, 2)
b = WithSlots(1, 2)
print(sys.getsizeof(a), "+ __dict__:", sys.getsizeof(a.__dict__))  # 48 + __dict__: 296
print(sys.getsizeof(b))                                            # 48  (і жодного __dict__)
print(hasattr(b, '__dict__'))                                      # False
```

Екземпляр без слотів тягне ще й окремий словник (~296 байт тут). Зі слотами цей
оверхед зникає — суттєво при мільйонах об'єктів. Доступ до атрибутів теж трохи
швидший (слот — це по суті дескриптор з фіксованим зміщенням).

Аналога в Swift немає прямого: там layout `class`/`struct` і так фіксований
компілятором. `__slots__` — це спосіб повернути Python ближче до такої
«фіксованої» моделі.

### Пастки `__slots__`

```python
b.z = 3
# AttributeError: 'WithSlots' object has no attribute 'z' and no __dict__ for setting new attributes
```

- **Не можна додавати атрибути поза списком слотів** — у цьому весь сенс, але це
  ламає динамічний код (моки, monkey-patching).
- **Немає `__dict__` і `__weakref__`** — якщо потрібні, додай їх явно:
  `__slots__ = ('x', '__dict__', '__weakref__')` (тоді частина економії зникає).
- **Спадкування — головна пастка.** Якщо хоч один клас в ієрархії **не** оголошує
  `__slots__`, екземпляри знову отримують `__dict__`, і вся економія пропадає:

```python
class Base:
    __slots__ = ('a',)
class Child(Base):          # НЕ оголосив __slots__
    pass

c = Child()
c.whatever = 2              # працює! __dict__ повернувся
print(hasattr(c, '__dict__'))   # True
```

> **⚠️ Пастка №1.** Щоб слоти працювали через усю ієрархію, **кожен** клас має
> оголосити `__slots__` (порожній `__slots__ = ()` теж рахується). Один пропуск —
> і `__dict__` повертається мовчки.

> **Best practice.** Не сип `__slots__` усюди «для швидкості». Додавай їх лише
> там, де профілювання показало проблему пам'яті при великій кількості
> екземплярів. Для dataclass використовуй `@dataclass(slots=True)`
> ([Модуль 06](../06-structs-and-value-types.md)) — він згенерує слоти коректно.

---

## 3. `__getattr__`/`__setattr__` — динамічний доступ (короткий приклад)

Повний каталог методів доступу до атрибутів — на сторінці
[dunder-методів](dunder-methods.md). Тут — один практичний патерн: **проксі**, що
делегує невідомі атрибути іншому об'єкту через `__getattr__` (викликається лише
коли звичайний пошук провалився):

```python
class Proxy:
    def __init__(self, target):
        self._target = target

    def __getattr__(self, name):              # лише для НЕзнайдених атрибутів
        print(f"proxying {name}")
        return getattr(self._target, name)

p = Proxy([1, 2, 3])
print(p.count(1))                             # proxying count → 1  (делеговано в list)
```

> **⚠️ Пастка.** `__getattr__` спрацьовує **тільки** для атрибутів, яких не
> знайдено звичайним шляхом. Не плутай із `__getattribute__`, який перехоплює
> **кожне** звертання (легко влаштувати нескінченну рекурсію). Деталі —
> [dunder-методи](dunder-methods.md).

---

## 4. `__init_subclass__` — реєстрація підкласів без метакласу

Найчастіша причина, з якої колись тягнулися до метакласів, — «зробити щось
автоматично, коли хтось успадкує мій клас» (реєстр плагінів, перевірка контракту).
З Python 3.6 для цього є хук `__init_subclass__` — він викликається **на
батьківському класі щоразу, коли визначають підклас**. Це сучасна заміна метакласу
для 90% випадків.

```python
class Plugin:
    registry: dict[str, type] = {}

    def __init_subclass__(cls, /, key=None, **kwargs):
        super().__init_subclass__(**kwargs)            # кооперативно — завжди
        if key is None:
            raise TypeError(f"{cls.__name__} must declare key=")
        Plugin.registry[key] = cls

class JsonExporter(Plugin, key="json"):                # key= йде в __init_subclass__
    pass

class CsvExporter(Plugin, key="csv"):
    pass

print(Plugin.registry)
# {'json': <class '__main__.JsonExporter'>, 'csv': <class '__main__.CsvExporter'>}

class Bad(Plugin):                                     # забули key=
    pass
# TypeError: Bad must declare key=
```

Зауваж: `key="json"` у списку баз — це не база, а **іменований аргумент класу**,
що потрапляє в `__init_subclass__`. Сам `__init_subclass__` неявно
`classmethod`. Цей патерн дає авто-реєстрацію, валідацію підкласів, додавання
методів — без жодного метакласу.

> **Best practice.** Потрібно щось зробити при створенні підкласу — спершу
> розглянь `__init_subclass__`. Потрібно щось на рівні самого атрибута/поля —
> `__set_name__` дескриптора. Метаклас — лише якщо обидва не підходять.

---

## 5. Метакласи — клас класів

Ключова ідея: **класи — це об'єкти, а їхній клас (тип) — `type`**.

```python
class Foo: pass
print(type(Foo))                 # <class 'type'>
print(isinstance(Foo, type))     # True
```

`type` — це метаклас за замовчуванням. А ще `type` — фабрика класів: можна
створити клас динамічно, без `class`-синтаксису:

```python
# type(name, bases, namespace)
Dyn = type("Dyn", (), {"x": 1, "greet": lambda self: "hi"})
d = Dyn()
print(d.x, d.greet())            # 1 hi
```

Коли пишеш `class Foo: ...`, Python під капотом викликає
`type("Foo", bases, namespace)`. **Метаклас** — це клас, що успадковує `type` і
перехоплює це створення:

```python
class Meta(type):
    def __new__(mcs, name, bases, ns, **kwargs):
        cls = super().__new__(mcs, name, bases, ns)
        print(f"creating class {name}")
        cls.created_by = "Meta"                # додаємо атрибут усім класам на Meta
        return cls

class Service(metaclass=Meta):                 # creating class Service
    pass

print(Service.created_by)                      # Meta
print(type(Service))                           # <class '__main__.Meta'>
```

`Meta.__new__` запускається при **створенні класу** (не екземпляра). Тут можна
змінити namespace, перевірити інваріанти, зареєструвати клас. Це те, на чому
збудовані `enum.EnumMeta`, `abc.ABCMeta`, декларативні бази ORM.

> **Best practice.** Метаклас — **останній засіб**. Спочатку: декоратор класу
> (просто функція, що приймає й повертає клас), потім `__init_subclass__`, потім
> `__set_name__`. Метаклас потрібен лише коли треба контролювати **саме
> створення** класу так, як хуки не дозволяють, або інтегруватися з чужим
> метакласом. Він ускладнює спадкування (конфлікти метакласів) і читабельність.

> **⚠️ Пастка.** Два батьки з **різними** несумісними метакласами → `TypeError:
> metaclass conflict` при спадкуванні. Це одна з причин, чому метакласи погано
> комбінуються, а `__init_subclass__` — добре.

**Той, що ти реально зустрінеш — `ABCMeta`.** Абстрактні базові класи
(`abc.ABC`/`@abstractmethod`) реалізовані через метаклас `ABCMeta`. Зазвичай ти
просто успадковуєш `abc.ABC` і не думаєш про метаклас — деталі в
[Модулі 08](../08-protocols-and-interfaces.md).

---

## 6. MRO і кооперативний `super()`

На відміну від Swift (одиночне спадкування + протоколи), Python має **множинне
спадкування**, і `super()` тут означає **не «батько», а «наступний у MRO»**.

**MRO** (Method Resolution Order) — лінеаризація ієрархії за алгоритмом **C3**:
єдиний послідовний порядок, у якому шукаються методи. Подивитися — `__mro__`.

### Кооперативне множинне спадкування, що працює

Класичний «diamond»: два класи з спільним предком. Щоб кожен `__init__`
виконався **рівно раз** і в правильному порядку, усі ланки мають бути
**кооперативними**: викликати `super().__init__(**kwargs)` і прокидати зайві
аргументи через `**kwargs`.

```python
class Base:
    def __init__(self, **kwargs):
        super().__init__()                   # кінець ланцюга → object

class Loud(Base):
    def __init__(self, *, volume=10, **kwargs):
        super().__init__(**kwargs)           # super() → НАСТУПНИЙ у MRO, не Base напряму
        self.volume = volume

class Timed(Base):
    def __init__(self, *, duration=60, **kwargs):
        super().__init__(**kwargs)
        self.duration = duration

class Track(Loud, Timed):
    def __init__(self, *, title, **kwargs):
        super().__init__(**kwargs)
        self.title = title

t = Track(title="Song", volume=11, duration=200)
print(t.title, t.volume, t.duration)                  # Song 11 200
print([c.__name__ for c in Track.__mro__])
# ['Track', 'Loud', 'Timed', 'Base', 'object']
```

Ключове прозріння: у `Loud.__init__` виклик `super()` веде **не в `Base`**, а в
`Timed` — наступний у MRO `Track`. Тобто `super()` залежить від **фактичного
типу екземпляра**, а не від місця написання. Саме тому `**kwargs` обов'язкові:
кожна ланка «відкушує» свої параметри й прокидає решту далі по ланцюгу.

### Класична пастка: змішування кооперативного й некооперативного `__init__`

Якщо **проміжна** ланка забуває викликати `super().__init__()`, ланцюг
обривається — наступні класи в MRO не ініціалізуються, **мовчки**:

```python
class A:
    def __init__(self):
        print("A.__init__"); super().__init__()
class B:
    def __init__(self):
        print("B.__init__"); super().__init__()
class Breaker(A):
    def __init__(self):
        print("Breaker.__init__")            # забули super().__init__() → обрив

class D(Breaker, B):
    def __init__(self):
        print("D.__init__"); super().__init__()

print([c.__name__ for c in D.__mro__])
# ['D', 'Breaker', 'A', 'B', 'object']
D()
# D.__init__
# Breaker.__init__          ← і все. A.__init__ та B.__init__ НЕ виконались!
```

`Breaker` не покликав `super()`, тож `A` і `B` далі по MRO не отримали
ініціалізації. Жодної помилки — просто напівініціалізований об'єкт. Це найгірший
вид багу: тихий.

> **⚠️ Пастка №2.** У кооперативній ієрархії **кожна** ланка має викликати
> `super().__init__(**kwargs)`, інакше ланцюг рветься без попередження. Або вся
> ієрархія кооперативна, або не змішуй. Тому й радять уникати глибокого
> множинного спадкування поза дисциплінованими mixin-ами
> ([хаб модуля, §6](../05-classes-and-oop.md#множинне-успадкування-та-mro)).

> **Best practice.** `super()` — не «виклик батька», а «наступний у MRO».
> Проєктуй mixin-и кооперативними з самого початку (`**kwargs` + `super()`).
> Якщо ієрархія стає схожою на головоломку — це сигнал перейти на композицію /
> протоколи ([Модуль 08](../08-protocols-and-interfaces.md)), як у
> protocol-oriented Swift.

---

## Шпаргалка / рецепти

```python
# Дескриптор з валідацією (перевикористання на багатьох полях)
class Positive:
    def __set_name__(self, owner, name): self._name = "_" + name
    def __get__(self, obj, objtype=None):
        return self if obj is None else getattr(obj, self._name)
    def __set__(self, obj, value):
        if value <= 0: raise ValueError(f"{self._name[1:]} must be positive")
        setattr(obj, self._name, value)

# Data-дескриптор (__set__)      → виграє в __dict__ екземпляра (як @property)
# Non-data (__get__ only)        → __dict__ виграє (механізм @cached_property)

# Економія пам'яті — фіксовані атрибути
class P:
    __slots__ = ('x', 'y')        # кожен клас в ієрархії має оголосити свій

# Реєстрація підкласів БЕЗ метакласу
class Plugin:
    registry = {}
    def __init_subclass__(cls, /, key, **kw):
        super().__init_subclass__(**kw)
        Plugin.registry[key] = cls

# Динамічний клас / метаклас
Dyn = type("Dyn", (Base,), {"x": 1})        # клас на льоту
class Meta(type):
    def __new__(mcs, name, bases, ns, **kw):
        return super().__new__(mcs, name, bases, ns)

# Кооперативний super() для множинного спадкування
class Mixin(Base):
    def __init__(self, *, opt=0, **kwargs):
        super().__init__(**kwargs)          # наступний у MRO, не "батько"
        self.opt = opt
Cls.__mro__                                  # порядок розв'язання методів (C3)
```

**Порядок вибору інструмента:** публічний атрибут → `@property` → дескриптор →
`__init_subclass__` / `__set_name__` → декоратор класу → **метаклас (останній
засіб)**.

## Див. також

- [Модуль 05 — Класи та ООП](../05-classes-and-oop.md) — `@property`, `@cached_property`, спадкування, `super()`.
- [Dunder-методи: повний каталог](dunder-methods.md) — `__getattr__`/`__getattribute__`/`__setattr__`, доступ до атрибутів.
- [Модуль 06 — Value-типи](../06-structs-and-value-types.md) — `@dataclass(slots=True)`, immutability.
- [Модуль 08 — Протоколи](../08-protocols-and-interfaces.md) — `abc.ABC`/`ABCMeta`, structural typing, mixins.
- [Модуль 04 — Типи](../04-types-and-typing.md) — `ClassVar`, `Final`, `@override`.
- [Тематичний індекс](../INDEX.md).
