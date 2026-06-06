# Файли та серіалізація

[← Курс](../README.md) · [Модуль 13](../13-stdlib-and-ecosystem.md) · **Файли та серіалізація**

У Swift роботою з файлами займаються `URL`, `FileManager`, `Data`, а серіалізацією —
`Codable` (JSON/PropertyList). У Python усе це в stdlib: `pathlib` (шляхи й
read/write), `open()` (потоки), `json`/`pickle` (серіалізація), `gzip`/`zipfile`/
`tarfile` (стиснення), `csv` (таблиці). Ключова відмінність: **encoding завжди
вказуй явно**, а ресурси відкривай через `with` — компілятор тут тебе не страхує.

---

## 1. `pathlib.Path` — об'єктні шляхи (≈ `URL` + `FileManager`)

`Path` — це і `URL`, і частина `FileManager` водночас: він і описує шлях, і вміє
читати/писати. З'єднання — оператором `/` (а не рядковою конкатенацією).

```python
from pathlib import Path

p = Path("/Users/vasyl/projects") / "data.tar.gz"   # / — з'єднання сегментів

p.name        # 'data.tar.gz'
p.stem        # 'data.tar'   — без останнього суфікса
p.suffix      # '.gz'
p.suffixes    # ['.tar', '.gz']
p.parent      # PosixPath('/Users/vasyl/projects')
p.parts       # ('/', 'Users', 'vasyl', 'projects', 'data.tar.gz')

p.with_suffix(".zip")          # .../data.tar.zip — заміна суфікса
p.with_name("backup.json")     # .../backup.json  — заміна імені файлу
```

```swift
// Swift Foundation — еквіваленти
let url = URL(fileURLWithPath: "/Users/vasyl/projects").appending(path: "data.tar.gz")
url.lastPathComponent          // "data.tar.gz"  ≈ .name
url.deletingPathExtension()    // ≈ .with_suffix("")
url.pathExtension              // "gz"            ≈ .suffix без крапки
```

### Перевірки та абсолютні шляхи

```python
p.exists()                 # чи існує
p.is_file()                # чи це файл
p.is_dir()                 # чи це тека
Path("data.json").absolute()   # додає cwd, НЕ нормалізує (.., симлінки)
Path("./a/../b").resolve()     # нормалізує + резолвить симлінки (≈ URL.standardized)
```

> **⚠️ Пастка.** `absolute()` лише префіксує поточну директорію; `..` та симлінки
> лишаються. Для канонічного шляху бери `resolve()` (≈ `URL.resolvingSymlinksInPath`).

### Перелік і пошук

```python
for child in Path(".").iterdir():    # один рівень (≈ contentsOfDirectory)
    print(child.name)

list(Path("src").glob("*.py"))       # за маскою, один рівень
list(Path("src").rglob("*.py"))      # рекурсивно (== glob("**/*.py"))
```

### Створення тек, читання, запис

```python
Path("out/logs").mkdir(parents=True, exist_ok=True)   # ≈ createDirectory(withIntermediateDirectories:)

p = Path("out/note.txt")
p.write_text("рядок1\nрядок2\n", encoding="utf-8")     # створює/перезаписує
p.read_text(encoding="utf-8")        # 'рядок1\nрядок2\n'

p.write_bytes(b"\x00\x01\x02")       # ≈ Data.write(to:)
p.read_bytes()                       # b'\x00\x01\x02'  (≈ Data(contentsOf:))

p.rename("out/renamed.txt")          # перейменувати/перемістити
Path("out/renamed.txt").unlink()     # видалити файл (≈ removeItem). unlink(missing_ok=True)
```

> **Best practice.** `read_text`/`write_text` зручні для невеликих файлів цілком.
> Для великих або порядкового читання — `open()` із `with` (нижче), щоб не тримати
> весь вміст у пам'яті.

---

## 2. `open()` — потоки, режими, `with`

Для порядкового читання й тонкого контролю — `open()`. У Swift немає прямого
аналога текстового файлового хендла з ітерацією по рядках; це дуже Python-ідіома:

```python
p = Path("out/big.log")
with open(p, encoding="utf-8") as f:     # 'r' за замовчуванням
    for line in f:                       # лінива ітерація — рядок за рядком
        process(line.rstrip("\n"))
```

| Режим | Що робить |
|-------|-----------|
| `"r"` | читання тексту (default) |
| `"w"` | запис, **обрізає** наявний файл |
| `"a"` | дозапис у кінець |
| `"x"` | створити; помилка, якщо файл є |
| `"rb"`/`"wb"` | бінарні дані (`bytes`, без encoding) |

> **⚠️ Пастка.** Завжди вказуй `encoding="utf-8"` для текстових файлів. Без нього
> Python бере локально-залежне кодування ОС — і той самий код ламається на іншій
> машині. Для бінарних режимів (`rb`/`wb`) `encoding` не вказують.

> **Best practice.** Завжди `with open(...)` — це context manager, що гарантовано
> закриває файл навіть при винятку (≈ `defer { try? fh.close() }` у Swift, але
> вбудовано). «Голий» `open()` без `with` — джерело витоків дескрипторів.

Аргумент `newline=""` вимикає трансляцію `\r\n`↔`\n` — обов'язковий для `csv`
(див. нижче) і для побайтово точного запису тексту.

---

## 3. `tempfile` — тимчасові файли й теки

```python
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as d:     # тека; видаляється на виході з with
    work = Path(d) / "scratch.txt"
    work.write_text("тимчасово", encoding="utf-8")
    # ... робота з work ...
# тут d уже не існує

with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8") as tf:
    tf.write("hi")
    tf.flush()
    print(Path(tf.name).exists())            # True — поки відкритий
# файл видалено
```

> **Best practice.** Усе тимчасове — через `tempfile`, не самописні шляхи у `/tmp`.
> Context manager гарантує прибирання, а імена унікальні (без гонок). Аналог
> `FileManager.temporaryDirectory`, але з автоочисткою.

---

## 4. `shutil` — операції високого рівня

```python
import shutil

shutil.copy(src, dst)            # копія файлу (≈ FileManager.copyItem)
shutil.copytree(src, dst)        # рекурсивна копія теки
shutil.move(src, dst)            # перемістити (через ФС-межі теж)
shutil.rmtree(path)             # видалити теку з вмістом (≈ removeItem) — НЕОБОРОТНО

shutil.which("python3")          # шлях до виконуваного у PATH або None (≈ `which`)
shutil.disk_usage(path)          # NamedTuple(total, used, free) у байтах
```

> **⚠️ Пастка.** `shutil.rmtree` видаляє рекурсивно й безповоротно — це `rm -rf`.
> Жодного «кошика». Перевір шлях двічі, особливо коли він із вводу користувача.

---

## 5. `glob` / `fnmatch` (коротко)

`Path.glob`/`rglob` зазвичай покривають усе. Окремі модулі знадобляться рідко:

```python
import fnmatch

fnmatch.fnmatch("a.py", "*.py")                      # True — звірка одного імені
fnmatch.filter(["a.py", "b.txt", "c.py"], "*.py")    # ['a.py', 'c.py']
```

> **⚠️ Пастка.** `fnmatch` для регістру спирається на `os.path.normcase`, тобто
> поведінка залежить від ОС. Для передбачуваності бери `fnmatch.fnmatchcase`
> (завжди з урахуванням регістру).

---

## 6. JSON — `json` (≈ `JSONEncoder`/`JSONDecoder`)

```python
import json

json.loads('{"id": 1}')                 # рядок → dict: {'id': 1}
json.dumps({"id": 1})                    # dict → рядок: '{"id": 1}'

json.dumps(
    {"ціна": 3.5, "tags": ["a", "b"], "id": 1},
    indent=2,            # форматований вивід (≈ .prettyPrinted)
    sort_keys=True,      # стабільний порядок ключів
    ensure_ascii=False,  # не екранувати кирилицю в \uXXXX
)
# {
#   "id": 1,
#   "tags": [
#     "a",
#     "b"
#   ],
#   "ціна": 3.5
# }
```

### У файл і з файлу

```python
with open("cfg.json", "w", encoding="utf-8") as f:
    json.dump({"k": "значення"}, f, ensure_ascii=False, indent=2)

with open("cfg.json", encoding="utf-8") as f:
    cfg = json.load(f)                   # {'k': 'значення'}
```

### Власні типи — `default=`

`json` із коробки не вміє `set`, `datetime`, `Decimal` тощо. Передай `default=` —
функцію, що перетворює невідомий об'єкт на серіалізовне:

```python
from datetime import date

def encode(o):
    if isinstance(o, date):
        return o.isoformat()
    raise TypeError(f"not serializable: {type(o)}")

json.dumps({"d": date(2025, 1, 15)}, default=encode)   # '{"d": "2025-01-15"}'
```

> **⚠️ Пастка №1.** `set`/`datetime` без `default=` кидають `TypeError: Object of
> type set is not JSON serializable`. JSON не має таких типів — це обмеження
> формату, не Python.

> **⚠️ Пастка №2.** Ключі JSON-об'єкта **завжди рядки**. `json.dumps({1: "x"})`
> дає `'{"1": "x"}'`, а після `loads` ключ лишається `'1'` (str), а не `1` (int).
> Round-trip не зберігає тип ключа.

> **Best practice.** Для типізованої серіалізації (як `Codable`) — не голий `json`,
> а **`pydantic`** (Модуль 06): валідація, вкладені моделі, `model_dump_json()`.
> `json` лишай для простих dict/list або швидких скриптів.

---

## 7. `pickle` — нативна серіалізація Python

`pickle` зберігає майже будь-який Python-об'єкт (включно з `set`, вкладеними
класами), на відміну від JSON. У Swift аналога немає — це не текстовий, а
бінарний Python-специфічний формат.

```python
import pickle

blob = pickle.dumps({"nums": [1, 2, 3], "set": {1, 2}})   # → bytes
pickle.loads(blob)                       # {'nums': [1, 2, 3], 'set': {1, 2}}

# у файл (бінарний режим!)
with open("state.pkl", "wb") as f:
    pickle.dump(obj, f)
with open("state.pkl", "rb") as f:
    obj = pickle.load(f)
```

> **⚠️ Пастка безпеки (критична).** **Ніколи не розпіклюй дані з ненадійного
> джерела.** `pickle.loads` може виконати довільний код під час десеріалізації —
> це повноцінний RCE-вектор. Для обміну з зовнішнім світом — JSON, не pickle.

> **Best practice.** `pickle` — лише для Python-до-Python усередині довіреного
> контуру (кеш, передача між процесами свого застосунку). Для будь-якого обміну
> чи зберігання, що переживе версію коду, — JSON/`pydantic`. Формат pickle ще й
> крихкий до перейменування класів.

---

## 8. Стиснення — `gzip`, `zipfile`, `tarfile`

### `gzip` — один потік

```python
import gzip

with gzip.open("data.txt.gz", "wt", encoding="utf-8") as f:   # 'wt' = текст
    f.write("привіт\n")

with gzip.open("data.txt.gz", "rt", encoding="utf-8") as f:
    f.read()                             # 'привіт\n'
```

### `zipfile` — архів з багатьма файлами

```python
import zipfile

with zipfile.ZipFile("arc.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write("a.txt", arcname="a.txt")   # додати файл з диска
    zf.writestr("c.txt", "CCC")          # додати з рядка/bytes

with zipfile.ZipFile("arc.zip") as zf:
    zf.namelist()                        # ['a.txt', 'c.txt']
    zf.read("c.txt").decode()            # 'CCC'
    zf.extractall("out/")                # розпакувати все
```

### `tarfile` — `.tar`, `.tar.gz` (коротко)

```python
import tarfile

with tarfile.open("arc.tar.gz", "w:gz") as tf:   # w:gz / w:bz2 / w:xz
    tf.add("b.txt", arcname="b.txt")

with tarfile.open("arc.tar.gz", "r:gz") as tf:
    tf.getnames()                        # ['b.txt']
```

> **⚠️ Пастка.** `extractall` з ненадійного архіву небезпечний (path traversal,
> «zip bomb»). На 3.14 фільтр за замовчуванням для tar — `'data'` (безпечний), але
> для чужих архівів усе одно валідуй імена записів перед розпакуванням.

---

## 9. CSV — `csv` (коротко, але часто потрібно)

```python
import csv

# запис словників
with open("people.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["name", "age"])
    w.writeheader()
    w.writerow({"name": "Alice", "age": 30})
    w.writerow({"name": "Bob", "age": 25})

# читання у dict-и
with open("people.csv", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
    # [{'name': 'Alice', 'age': '30'}, {'name': 'Bob', 'age': '25'}]
```

Простіший варіант — `csv.reader`/`csv.writer` (рядки/списки замість dict).

> **⚠️ Пастка.** Файл для `csv` відкривай із `newline=""` — інакше на Windows
> з'являться порожні рядки між записами. І пам'ятай: `csv` читає **усе як рядки** —
> `age` буде `'30'`, а не `30`; конвертуй типи самостійно.

---

## Шпаргалка / рецепти

```python
from pathlib import Path
p = Path("data") / "file.json"          # з'єднання шляхів
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(s, encoding="utf-8")       # запис тексту цілком
p.read_text(encoding="utf-8")           # читання тексту цілком
list(Path("src").rglob("*.py"))         # рекурсивний пошук
p.with_suffix(".bak")                   # заміна розширення

with open(p, encoding="utf-8") as f:    # порядкове читання
    for line in f: ...

import json
json.dumps(d, indent=2, ensure_ascii=False)    # гарний UTF-8 JSON
json.dump(d, f); json.load(f)                   # у/з файл
# default=encode для set/datetime/Decimal; ключі завжди str

import shutil
shutil.copy(src, dst); shutil.rmtree(dir)       # rmtree безповоротний!

import zipfile
with zipfile.ZipFile("a.zip") as zf: zf.namelist()

import tempfile
with tempfile.TemporaryDirectory() as d: ...    # автоприбирання
```

## Див. також

- [Модуль 13 — Стандартна бібліотека та екосистема](../13-stdlib-and-ecosystem.md) — `pathlib`, `json`, мапінг на Foundation.
- [Модуль 03 — Конвертації типів](../03-data-structures/conversions.md) — dict↔JSON, парсинг CSV-значень.
- [Модуль 01 — Рядки](../01-syntax-and-control-flow/strings.md) — encoding, `bytes` vs `str`.
- [Регулярні вирази](regex.md) — парсинг текстових файлів.
- [Тематичний індекс](../INDEX.md).
