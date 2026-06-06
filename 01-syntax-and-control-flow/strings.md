# Рядки: повний довідник методів

[← Курс](../README.md) · [Модуль 01](../01-syntax-and-control-flow.md) · **Рядки**

У Swift рядок — це `String` (value-тип, колекція `Character`, Unicode-коректний).
У Python `str` — це **незмінна** послідовність Unicode code points. «Незмінна»
означає: жоден метод не міняє рядок на місці — усі повертають **новий** рядок.

```python
s = "hello"
s.upper()        # 'HELLO'  — новий рядок
print(s)         # 'hello'  — оригінал не змінився
s[0] = "H"       # ❌ TypeError: 'str' object does not support item assignment
```

```swift
// Swift: String — теж value, але var дозволяє мутацію на місці
var s = "hello"
s = s.uppercased()
```

> **⚠️ Найчастіша помилка.** `s.replace("a", "b")` нічого не «робить із `s`» —
> ти **мусиш** забрати результат: `s = s.replace("a", "b")`. Це стосується **всіх**
> методів рядків.

---

## 1. Створення та літерали

```python
single = 'one'
double = "two"                 # лапки рівноцінні; обирай ті, що уникають \"
triple = """багато
рядків"""                       # аналог Swift """..."""
raw = r"C:\new\path"           # raw: \n НЕ є переходом рядка (для regex/шляхів)
joined = "a" "b" "c"           # сусідні літерали склеюються → 'abc'
byte_str = b"raw bytes"        # bytes, не str (див. §10)
```

Конкатенація і повторення:

```python
"foo" + "bar"        # 'foobar'   (тільки str + str; "x" + 1 → TypeError)
"ab" * 3             # 'ababab'
"-" * 20             # роздільник
```

> **⚠️ Пастка продуктивності.** Не будуй рядок у циклі через `+=` — кожна
> ітерація створює новий об'єкт (O(n²)). Збирай у `list` і роби `"".join(...)`
> наприкінці (§4). Це Python-аналог `String.reserveCapacity` + append.

Перетворення в рядок — `str()` (детальніше — [конвертації](../03-data-structures/conversions.md)):

```python
str(42)        # '42'
str(3.14)      # '3.14'
str([1, 2])    # '[1, 2]'
repr("hi")     # "'hi'"   — repr дає «налагоджувальне» представлення (з лапками)
```

---

## 2. Індексація та зрізи

Рядок — послідовність, тож працюють індекси й зрізи (повна механіка —
[Модуль 03 · list](../03-data-structures/list.md#3-зрізи-slicing)):

```python
s = "Python"
s[0]        # 'P'
s[-1]       # 'n'      від'ємний індекс — з кінця
s[0:3]      # 'Pyt'    [start:stop)
s[::-1]     # 'nohtyP'  реверс
len(s)      # 6
"y" in s    # True      перевірка входження підрядка
```

> **⚠️ Пастка.** Окремого типу `Character` немає: `s[0]` — це рядок довжини 1.
> Ітерація `for ch in s` дає по одному code point (≈ символу).

---

## 3. f-strings і мова форматування

f-strings — головний спосіб форматування (PEP 498). Усередині `{}` — будь-який
вираз, після `:` — **специфікатор формату**.

```python
name, pi = "Vasyl", 3.14159
f"Hi, {name}"               # 'Hi, Vasyl'
f"{2 + 2}"                  # '4'        — вираз
f"{name.upper()}"           # 'VASYL'    — виклики методів теж
f"{pi:.2f}"                 # '3.14'     — 2 знаки після коми
f"{x=}"                     # 'x=42'     — debug-вивід «ім'я=значення» (3.8+)
```

### Міні-мова специфікаторів `[[fill]align][sign][#][0][width][,][.prec][type]`

```python
f"{3.14159:.2f}"     # '3.14'        точність для float
f"{1234567:,}"       # '1,234,567'   роздільник тисяч (кома)
f"{1234567:_}"       # '1_234_567'   роздільник підкресленням
f"{0.1234:.1%}"      # '12.3%'       відсотки
f"{255:#x}"          # '0xff'        hex з префіксом (#o, #b — oct/bin)
f"{42:08.2f}"        # '00042.00'    нулі зліва, ширина 8
f"{'hi':>8}|"        # '      hi|'   вирівнювання праворуч (ширина 8)
f"{'hi':<8}|"        # 'hi      |'   ліворуч
f"{'hi':^8}|"        # '   hi   |'   по центру
f"{'x':*^9}"         # '****x****'   заповнювач '*'
```

Специфікатор може містити вкладені `{}` (динамічна ширина/точність) і працює для
дат:

```python
width = 10
f"{42:>{width}}"                       # ширина з змінної
from datetime import date
f"{date(2024, 1, 2):%Y/%m/%d}"         # '2024/01/02'  (формат — як у strftime)
```

> **Best practice.** f-strings — стандарт. Старі `"%s" % x` і `"{}".format(x)`
> лишилися для рідкісних випадків (напр. шаблон, відомий лише в рантаймі, або
> логування — там `logging` робить підстановку сам, [Модуль 10](../10-errors-and-exceptions.md)).

---

## 4. `split` і `join` — робочі конячки

Це найчастіші операції з рядками: розбити вхід і зібрати вихід.

```python
"a,b,c".split(",")        # ['a', 'b', 'c']
"a,b,,c".split(",")       # ['a', 'b', '', 'c']   порожні зберігаються
"a b   c".split()         # ['a', 'b', 'c']       без аргументу: по whitespace,
                          #                        кілька пробілів = один роздільник
"a,b,c".split(",", 1)     # ['a', 'b,c']          maxsplit — лише перший поділ
"a\nb\nc".splitlines()    # ['a', 'b', 'c']       по рядках (універсально \n/\r\n)
"a,b,c".rsplit(",", 1)    # ['a,b', 'c']          з кінця
```

`join` — **зворотна** операція; викликається на роздільнику:

```python
"-".join(["2024", "01", "02"])     # '2024-01-02'
"".join(["a", "b", "c"])           # 'abc'
", ".join(str(n) for n in [1, 2, 3])   # '1, 2, 3'  (елементи МАЮТЬ бути str!)
```

> **⚠️ Пастка для Swift-розробника.** `join` — метод **роздільника**, не списку:
> `sep.join(items)`, а не `items.join(sep)`. І всі елементи мають бути `str`,
> інакше `TypeError` — конвертуй: `", ".join(map(str, nums))`.

> **Ідіома парсингу.** Розбір рядка `"key=value"`:
> ```python
> key, _, value = "color=blue".partition("=")   # ('color', '=', 'blue')
> ```
> `partition` завжди повертає 3 елементи (навіть якщо роздільника немає) — на
> відміну від `split`, тому його зручно розпаковувати без перевірок.

---

## 5. Видалення пробілів і обрізка

```python
"  hi  ".strip()        # 'hi'      з обох боків
"  hi  ".lstrip()       # 'hi  '    лише зліва
"  hi  ".rstrip()       # '  hi'    лише справа
"xxabcxx".strip("x")    # 'abc'     обрізати конкретні символи (набір, не підрядок!)
"...hi...".strip(".")   # 'hi'
```

> **⚠️ Пастка.** Аргумент `strip` — це **набір символів**, а не підрядок:
> `"banana".strip("ba")` → `'n'` (зрізає всі `b` і `a` з країв). Щоб прибрати
> саме префікс/суфікс — використовуй `removeprefix`/`removesuffix`:

```python
"test_file.py".removesuffix(".py")     # 'test_file'   (3.9+)
"__name__".removeprefix("__")          # 'name__'
"  spaced  ".removeprefix("  ").removesuffix("  ")   # 'spaced'
```

---

## 6. Пошук і перевірки

```python
"hello".find("l")        # 2       індекс першого входження
"hello".find("z")        # -1      НЕ знайдено → -1 (не виняток)
"hello".index("l")       # 2       як find, але кидає ValueError, якщо немає
"hello".rfind("l")       # 3       з кінця
"hello world".count("o") # 2       кількість входжень

"file.py".startswith("file")            # True
"file.py".endswith((".py", ".pyi"))     # True   — кортеж варіантів!
"hello" in "hello world"                # True   — найпростіша перевірка входження
```

Булеві перевірки вмісту:

```python
"abc".isalpha()      # True    лише літери
"123".isdigit()      # True    лише цифри
"a1".isalnum()       # True    літери+цифри
"  ".isspace()       # True    лише пробіли
"Title".istitle()    # True
"ABC".isupper()      # True
"id_1".isidentifier()# True    чи валідний як ім'я змінної
```

> **⚠️ Пастка.** `find` повертає `-1`, а `index` кидає `ValueError`. Якщо тобі
> просто треба «чи є підрядок» — пиши `if "x" in s:`, а не `if s.find("x") != -1:`.

---

## 7. Зміна регістру

```python
"hello".upper()          # 'HELLO'
"HELLO".lower()          # 'hello'
"hello world".title()    # 'Hello World'   кожне слово з великої
"hello".capitalize()     # 'Hello'         лише перша літера речення
"Abc".swapcase()         # 'aBC'
"CAFÉ".casefold()        # 'café' — агресивний lower для коректного порівняння
```

> **Best practice.** Для **порівняння без регістру** (особливо з Unicode) бери
> `casefold`, не `lower`: `a.casefold() == b.casefold()`. `casefold` правильно
> обробляє хитрі випадки (нім. `ß` → `ss`).

---

## 8. Вирівнювання та заповнення

```python
"42".zfill(5)            # '00042'        нулі зліва (для чисел)
"hi".center(10, "*")     # '****hi****'
"hi".ljust(10, ".")      # 'hi........'
"hi".rjust(10, ".")      # '........hi'
```

(Для форматованого виводу частіше зручніші f-string-специфікатори з §3.)

---

## 9. Заміна та трансляція

```python
"hello".replace("l", "L")        # 'heLLo'     всі входження
"hello".replace("l", "L", 1)     # 'heLlo'     лише перші N
"a.b.c".replace(".", "/")        # 'a/b/c'

# translate — посимвольна заміна за таблицею (швидко для багатьох символів)
table = str.maketrans("aeiou", "*****")
"encyclopedia".translate(table)  # '*ncycl*p*d**'

# видалення символів: третій аргумент maketrans
strip_punct = str.maketrans("", "", ".,!?")
"a.b,c!".translate(strip_punct)  # 'abc'
```

---

## 10. `bytes` vs `str` — текст проти байтів

Це строге розмежування, як `String` vs `Data` у Swift. `str` — це **текст**
(Unicode); `bytes` — це **сирі байти** (мережа, файли, бінарні дані).

```python
text = "café"
data = text.encode("utf-8")      # str → bytes:  b'caf\xc3\xa9'  (4 символи → 5 байт)
back = data.decode("utf-8")      # bytes → str:  'café'
len(text), len(data)             # (4, 5)

b"\x48\x49".decode("ascii")      # 'HI'
bytes([72, 73])                  # b'HI'   із чисел
```

> **⚠️ Пастка.** Не змішуй `str` і `bytes`: `"a" + b"b"` → `TypeError`. На межі
> вводу/виводу (сокети, `open(..., "rb")`) ти отримуєш `bytes` — одразу
> `.decode()` у `str`, працюй із текстом, і `.encode()` назад перед відправкою.
> Кодування **завжди** вказуй явно (`"utf-8"`), не покладайся на дефолт ОС.

---

## 11. Регулярні вирази (вступ)

Для складного парсингу — модуль `re`. Тут лише міст; повний розбір — у
[Модулі 13 · re](../13-stdlib-and-ecosystem.md).

```python
import re

re.findall(r"\d+", "a12 b34")          # ['12', '34']   усі збіги
re.sub(r"\s+", " ", "a   b\t c")       # 'a b c'         нормалізація пробілів
m = re.match(r"(\w+)@(\w+)", "user@host")
m.group(1), m.group(2)                  # ('user', 'host')
re.split(r"[,;]\s*", "a, b; c")        # ['a', 'b', 'c']
```

> **Best practice.** Якщо задачу вирішують `split`/`replace`/`partition` —
> використовуй їх (швидше й читабельніше). `re` бери, коли потрібні справжні
> патерни. Завжди пиши шаблони як **raw**-рядки (`r"..."`), щоб `\d` не плутати з
> escape-послідовностями.

---

## Шпаргалка / рецепти

```python
# Нормалізувати пробіли
" ".join("a   b\t c".split())                      # 'a b c'

# Зрізати розширення файлу
"report.final.pdf".rsplit(".", 1)[0]               # 'report.final'

# Безпечний парсинг "k=v" з дефолтом
key, _, val = line.partition("=")                  # val == '' якщо немає '='

# CSV-рядок із чисел
",".join(map(str, [1, 2, 3]))                      # '1,2,3'

# Порівняння без регістру
a.casefold() == b.casefold()

# Перевірити кілька суфіксів
fname.endswith((".jpg", ".png", ".gif"))

# Багаторядковий шаблон без зайвих відступів
import textwrap
textwrap.dedent("""
    line 1
    line 2
""").strip()

# Зробити slug
re.sub(r"[^a-z0-9]+", "-", "Hello, World!".lower()).strip("-")   # 'hello-world'
```

## Див. також

- [Модуль 01 — Синтаксис](../01-syntax-and-control-flow.md) — звідки ти сюди прийшов.
- [Модуль 03 · Зрізи та list](../03-data-structures/list.md) — повна механіка `[start:stop:step]`.
- [Модуль 03 · Конвертації типів](../03-data-structures/conversions.md) — `str()`/`int()`/парсинг.
- [Модуль 13 — Стандартна бібліотека](../13-stdlib-and-ecosystem.md) — `re`, `textwrap`, `string`.
- [Тематичний індекс](../INDEX.md).
