# Модуль 01. Синтаксис і керування потоком

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 01**

Туторіал: [§3 Вступ](https://docs.python.org/uk/3/tutorial/introduction.html),
[§4 Керування потоком](https://docs.python.org/uk/3/tutorial/controlflow.html).

**Поглиблені сторінки модуля:**
- [Рядки: повний довідник методів](01-syntax-and-control-flow/strings.md) — `split`/`join`/`strip`/`replace`/форматування/`bytes`.
- [Structural pattern matching (`match`)](01-syntax-and-control-flow/match.md) — усі види патернів, вичерпність.

## 1. Блоки: відступи замість фігурних дужок

### Swift
```swift
if x > 0 {
    print("positive")
}
```

### Python
```python
if x > 0:
    print("positive")
```

Блок задається **відступом** (за конвенцією — 4 пробіли, ніколи табуляції).
Двокрапка `:` відкриває блок. Немає `{}`, немає `;` у кінці рядка.

> **⚠️ Пастка.** Змішування пробілів і табів — синтаксична помилка. `ruff format`
> прибирає цю проблему автоматично; просто завжди форматуй код.

## 2. Змінні та константи

### Swift
```swift
var counter = 0
let name = "Vasyl"   // незмінна
```

### Python
```python
counter = 0
NAME = "Vasyl"   # КОНВЕНЦІЯ: константи — UPPER_CASE
```

> **⚠️ Пастка: немає констант.** У Python **немає справжніх констант**. `let` не існує.
> `NAME = "Vasyl"` — це угода (PEP 8), а не гарантія: значення можна перезаписати.
> Незмінність забезпечують лише на рівні *типів* (`tuple`, `frozenset`,
> `frozen dataclass`), а не змінних. Якщо хочеш гарантію — Модуль 06.

Оголошення типу опціональне, але рекомендоване:

```python
counter: int = 0
name: str = "Vasyl"
```

## 3. Числа й арифметика

```python
3 + 2        # 5
7 / 2        # 3.5   — / ЗАВЖДИ дає float
7 // 2       # 3     — // це цілочисельне ділення (floor!)
7 % 2        # 1
2 ** 10      # 1024  — піднесення до степеня (у Swift: pow / немає оператора)
divmod(17, 5)   # (3, 2)  — частка й остача одночасно
abs(-3)         # 3
round(3.14159, 2)   # 3.14
```

> **⚠️ Пастка: `/` завжди float.** `/` завжди повертає `float`, навіть `4 / 2 == 2.0`. Для
> цілого результату використовуй `//`. У Swift `/` між `Int` дає `Int`.

> **⚠️ Пастка: немає `++`/`--`.** Немає `++` і `--`. Тільки `x += 1` (augmented assignment:
> `+= -= *= /= //= %= **= &= |= ^= <<= >>=`).

> **⚠️ Пастка: `//` це floor division.** `//` — це **floor division**, не «відкинути дробову частину»:
> `-7 // 2 == -4` (не `-3`!), і `-7 % 2 == 1` (остача завжди має знак дільника).
> У Swift `/` і `%` округлюють до нуля — поведінка різна на від'ємних.

```python
round(2.5)   # 2   ⚠️ banker's rounding: 0.5 округляється до ПАРНОГО
round(3.5)   # 4
```

> **⚠️ Пастка: банкірське округлення.** `round()` використовує «округлення до парного» (half-to-even),
> а не «завжди вгору». `round(2.5) == 2`. Це навмисно (зменшує системну похибку),
> але дивує. Для фінансів — `Decimal` із явним режимом округлення.

### Цілі довільної точності, бітові операції

`int` у Python — **довільної точності** (немає переповнення):

```python
2 ** 1000    # величезне число, без жодної помилки
```

У Swift це б переповнило `Int`. Бітові операції — як у Swift:

```python
5 & 3    # 1    AND
5 | 2    # 7    OR
5 ^ 1    # 4    XOR
~5       # -6   NOT
1 << 4   # 16   зсув вліво
255 >> 4 # 15   зсув вправо
pow(2, 10, 1000)   # 24   — (2**10) % 1000 ефективно (модульне піднесення)
```

Літерали в різних системах числення:

```python
0xFF        # 255   hex
0o17        # 15    oct
0b1010      # 10    bin
1_000_000   # підкреслення-роздільник для читабельності
```

### Точні числа: Decimal, Fraction, complex

```python
0.1 + 0.2                       # 0.30000000000000004  ⚠️ float неточний!

from decimal import Decimal
Decimal("0.1") + Decimal("0.2")  # Decimal('0.3')  — точно (гроші, фінанси)

from fractions import Fraction
Fraction(1, 3) + Fraction(1, 6)  # Fraction(1, 2)  — точні раціональні

(2 + 3j) * (1 - 1j)             # (5+1j)  — комплексні вбудовані в мову
```

> **Best practice.** Для грошей **ніколи** не використовуй `float` — лише
> `Decimal` (з рядка, не з float: `Decimal("0.1")`, не `Decimal(0.1)`). Це прямий
> аналог того, чому у фінансах не беруть `Double`. Деталі —
> [Модуль 13](13-stdlib-and-ecosystem.md).

## 4. Рядки

### Інтерполяція: f-strings vs string interpolation

```swift
let name = "Vasyl"
let msg = "Hello, \(name)! \(2 + 2)"
```

```python
name = "Vasyl"
msg = f"Hello, {name}! {2 + 2}"     # f-string — головний спосіб
```

f-strings — найідіоматичніше форматування. Вони ще й підтримують специфікатори:

```python
pi = 3.14159
f"{pi:.2f}"          # '3.14'
f"{1_000_000:,}"     # '1,000,000'
f"{value=}"          # 'value=42'  — зручно для дебагу (3.8+)
```

Багаторядкові рядки — потрійні лапки (аналог Swift `"""`):

```python
text = """
Multi-line
string
"""
```

> **Best practice.** Не конкатенуй через `+` і не використовуй старий
> `"%s" % x` чи `.format()` без потреби. f-strings — стандарт.

> **📖 Це лише вступ.** Робота з рядками — окрема велика тема: методи
> `split`/`join`/`strip`/`replace`/`find`/`startswith`, зміна регістру,
> вирівнювання, `translate`, `bytes` vs `str`, regex. Повний довідник з
> прикладами — на сторінці **[Рядки](01-syntax-and-control-flow/strings.md)**.

## 5. Колекції-літерали (огляд; деталі — Модуль 03)

```python
nums = [1, 2, 3]              # list   ~ Array (але mutable reference!)
point = (1, 2)               # tuple  ~ незмінний кортеж
unique = {1, 2, 3}           # set    ~ Set
ages = {"Vasyl": 40}         # dict   ~ Dictionary
```

## 6. Умови

```python
if score >= 90:
    grade = "A"
elif score >= 80:      # elif, не "else if"
    grade = "B"
else:
    grade = "C"
```

Тернарний вираз має незвичний порядок слів:

```python
grade = "A" if score >= 90 else "B"
#        ^value_if_true  ^cond      ^value_if_false
```

```swift
let grade = score >= 90 ? "A" : "B"   // Swift
```

### Truthiness — важлива відмінність

У Python в булевому контексті порожні колекції/нуль/`None` вважаються `False`:

```python
items: list[int] = []
if not items:           # ідіоматично: "якщо список порожній"
    print("empty")

name = ""
if not name:            # порожній рядок теж falsy
    print("no name")
```

> **⚠️ Пастка: всеохопна truthiness.** У Swift умова має бути строго `Bool`. У Python `if items:`
> перевіряє «непорожність». Це потужно, але обережно: `if x:` спрацює як `False`
> і для `0`, і для `""`, і для `[]`, і для `None`. Якщо треба перевірити саме на
> `None` — пиши явно `if x is None:`.

### Порівняння з None

```python
if value is None:        # ПРАВИЛЬНО — identity-перевірка
    ...
if value == None:        # НЕ роби так
    ...
```

`is` перевіряє ідентичність об'єкта (як `===` у Swift), `==` — рівність значень
(як `==`). Для `None`, `True`, `False` завжди використовуй `is`.

Ланцюгові порівняння (чого немає у Swift):

```python
if 0 <= x < 100:         # читається як математичний запис
    ...
```

## 7. Цикли

### for — це завжди «for-in»

У Python немає C-style `for (i=0; ...)`. Цикл `for` ітерує по послідовності —
як `for-in` у Swift.

```python
for item in [10, 20, 30]:
    print(item)

for i in range(5):          # 0,1,2,3,4
    print(i)

for i in range(2, 10, 2):   # start, stop, step → 2,4,6,8
    print(i)
```

```swift
for i in 0..<5 { print(i) }              // Swift
for i in stride(from: 2, to: 10, by: 2)  // аналог range(2,10,2)
```

Коли потрібен індекс — `enumerate` (аналог `.enumerated()`):

```python
for index, value in enumerate(["a", "b", "c"]):
    print(index, value)
```

Паралельна ітерація — `zip` (як `zip` у Swift):

```python
for name, age in zip(names, ages):
    print(name, age)
```

### while

```python
while not done:
    done = step()
```

### break / continue / else на циклі

```python
for n in range(2, 10):
    for d in range(2, n):
        if n % d == 0:
            break
    else:
        # виконається, ЯКЩО цикл завершився БЕЗ break
        print(f"{n} is prime")
```

> **⚠️ Пастка: `else` на циклі.** `else` на циклі — унікальна конструкція Python, якої немає у
> Swift. Блок `else` виконується, якщо цикл *не перервали* через `break`. Зручно
> для пошуку («не знайшли — зробити Х»), але читачам часто незрозуміло; додавай
> коментар.

## 8. match — потужніший за switch

Python 3.10+ має structural pattern matching. Це не просто `switch` — це ближче
до Swift `switch` із `case let` і pattern matching по структурі.

### Swift
```swift
switch point {
case (0, 0): print("origin")
case (let x, 0): print("on x-axis at \(x)")
case (0, let y): print("on y-axis at \(y)")
case (let x, let y): print("at \(x), \(y)")
}
```

### Python
```python
match point:
    case (0, 0):
        print("origin")
    case (x, 0):
        print(f"on x-axis at {x}")
    case (0, y):
        print(f"on y-axis at {y}")
    case (x, y):
        print(f"at {x}, {y}")
```

Match по класах/полях (аналог матчингу enum з associated values):

```python
from dataclasses import dataclass

@dataclass
class Circle:
    radius: float

@dataclass
class Rect:
    w: float
    h: float

def area(shape: Circle | Rect) -> float:
    match shape:
        case Circle(radius=r):
            return 3.14159 * r * r
        case Rect(w=w, h=h):
            return w * h
```

Guard-умови (аналог `where` у Swift `case`):

```python
match command:
    case ["move", direction] if direction in {"north", "south"}:
        ...
    case ["quit"]:
        ...
    case _:                      # _ — це default (як `default:` у Swift)
        print("unknown")
```

> **⚠️ Пастка: немає вичерпності.** На відміну від Swift, `match` у Python **не
> вимагає вичерпності** (exhaustiveness). Якщо жоден `case` не збігся — блок
> мовчки нічого не виконує. Майже завжди додавай `case _:`. Для enum-подібної
> вичерпності покладайся на `pyright` + `assert_never`.

> **📖 Глибше.** `match` має ще mapping-патерни (`{"key": v}`), OR-патерни (`|`),
> `as`-capture, позиційну деструктуризацію (`__match_args__`), та пастку
> «capture vs порівняння». Повний розбір усіх видів патернів і статичної
> вичерпності — на сторінці **[match](01-syntax-and-control-flow/match.md)**.

## 9. Walrus `:=` — присвоєння-вираз

Оператор `:=` (3.8+) присвоює **і одночасно повертає** значення — зручно, щоб не
обчислювати/не викликати щось двічі. У Swift прямого аналога немає (там
`if let` робить схожу річ для опціоналів).

```python
# Без walrus — виклик або довжина рахується двічі / зайвий рядок
data = fetch()
if len(data) > 100:
    print(f"too big: {len(data)}")

# З walrus — обчислили один раз, прямо в умові
if (n := len(data)) > 100:
    print(f"too big: {n}")

# Класичний патерн «читати, поки не порожньо»
while (line := input()) != "quit":
    process(line)

# У comprehension — щоб не рахувати дороге f(x) двічі
results = [y for x in data if (y := f(x)) is not None]
```

> **⚠️ Пастка.** Дужки навколо `:=` в умові майже завжди потрібні
> (`if (n := ...) > 0`), бо інакше пріоритет операторів зробить не те, що ти
> хочеш. Не зловживай — walrus виправданий, коли реально прибирає дублювання
> обчислення; інакше звичайне присвоєння читабельніше.

## 10. pass і заглушки

```python
def todo() -> None:
    pass        # порожнє тіло-заглушка (синтаксис вимагає хоч щось)
```

`pass` — порожня операція, потрібна там, де синтаксис вимагає блок, але робити
нічого. Альтернатива для «ще не реалізовано»:

```python
def todo() -> None:
    raise NotImplementedError
```

## Best practices модуля

- 4 пробіли, ніколи таби. Довірся `ruff format`.
- f-strings для всього форматування.
- `is None` / `is not None` — для перевірки на `None`.
- Не плутай `/` і `//`.
- Використовуй truthiness ідіоматично (`if not items:`), але пам'ятай про її
  «всеохопність».
- `match` — для розбору структур; майже завжди закривай `case _:`.
- Walrus `:=` — коли прибирає подвійне обчислення; з дужками.
- Для грошей — `Decimal`, ніколи `float`.
- Тримай `pyright` strict — він компенсує відсутність вичерпності й типобезпеки.

## Див. також

- [Рядки: повний довідник методів](01-syntax-and-control-flow/strings.md) — `split`/`join`/форматування/`bytes`/regex.
- [Structural pattern matching](01-syntax-and-control-flow/match.md) — усі види патернів, `assert_never`.
- [Модуль 03 — Структури даних](03-data-structures.md) — list/dict/set, зрізи, сортування, конвертації.
- [Модуль 06 — Value-типи](06-structs-and-value-types.md) — `@dataclass` для `match`, immutability.
- [Модуль 13 — Stdlib](13-stdlib-and-ecosystem.md) — `re`, `decimal`, `textwrap`.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 02 — Функції](02-functions.md)
