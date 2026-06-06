# SQLite (sqlite3)

[← Курс](../README.md) · [Модуль 13](../13-stdlib-and-ecosystem.md) · **SQLite (sqlite3)**

SQLite вбудований у Python так само, як у iOS: на телефоні є системний `libsqlite3`,
а у Swift ти або викликаєш C-API напряму, або береш обгортку (SQLite.swift, GRDB).
У Python вся обгортка вже в stdlib — модуль `sqlite3`, без жодних залежностей.
Це повноцінна реляційна БД у файлі (або в пам'яті), ідеальна для локального
сховища, кешів, тестів і прототипів.

```swift
// Swift: потрібна стороння обгортка (SQLite.swift)
let db = try Connection("app.db")
let users = Table("users")
try db.run(users.insert(name <- "Alice"))
```

```python
import sqlite3
conn = sqlite3.connect("app.db")        # або ":memory:"
conn.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
conn.commit()
```

---

## 1. Connect, cursor, execute, fetch

`connect()` дає з'єднання; запити виконуєш через `cursor()` (як ітератор по
результату) або прямо на з'єднанні. Шлях `":memory:"` створює БД у RAM — живе
доти, доки відкрите з'єднання (ідеально для тестів).

```python
import sqlite3

conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("""
    CREATE TABLE users (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age  INTEGER
    )
""")
cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("Alice", 30))
cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("Bob", 25))

cur.execute("SELECT name, age FROM users ORDER BY age")
cur.fetchone()      # ('Bob', 25)          — один рядок (або None)
cur.execute("SELECT name, age FROM users ORDER BY age")
cur.fetchall()      # [('Bob', 25), ('Alice', 30)]   — усі рядки
cur.fetchmany(2)    # до N рядків (тут уже порожньо — курсор вичерпано)
```

Курсор — ітерабельний; це найекономніший спосіб обійти великий результат
(рядки тягнуться поступово, а не всі в пам'ять):

```python
cur.execute("SELECT name FROM users ORDER BY name")
for row in cur:                 # row — кортеж
    print(row[0])               # Alice / Bob
```

`lastrowid` — id останнього INSERT; `rowcount` — скільки рядків зачепив
UPDATE/DELETE (для SELECT недостовірний):

```python
cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("Carol", 40))
cur.lastrowid                   # 3
cur.execute("UPDATE users SET age = age + 1 WHERE age > 30")
cur.rowcount                    # 1
```

---

## 2. Параметризовані запити — і пастка SQL-ін'єкції

Це **найважливіший** урок усієї сторінки. Значення в запит підставляй **тільки**
через плейсхолдери — `?` (позиційні) або `:name` (іменовані). Драйвер екранує їх
сам. **Ніколи** не вставляй дані користувача через f-рядок чи конкатенацію.

```python
# позиційні ? — кортеж значень (навіть для одного: (x,))
cur.execute("SELECT * FROM users WHERE age > ?", (26,))

# іменовані :name — словник
cur.execute("SELECT name FROM users WHERE age > :min_age", {"min_age": 26})
cur.fetchall()                  # [('Alice',)]
```

> **⚠️ Пастка: SQL-ін'єкція.** f-рядок із вводом користувача — діра в безпеці.
> Спецсимволи в даних ламають запит або зливають усю таблицю:
>
> ```python
> user_input = "x' OR '1'='1"
> bad = f"SELECT * FROM users WHERE name = '{user_input}'"
> # SELECT * FROM users WHERE name = 'x' OR '1'='1'
> conn.execute(bad).fetchall()                              # ['Alice', 'Bob'] — злито ВСЕ!
>
> conn.execute("SELECT * FROM users WHERE name = ?", (user_input,)).fetchall()
> # []  — безпечно: рядок порівняли як літерал, такого імені немає
> ```
>
> Плейсхолдери — це і безпека, і коректність (типи, лапки, NULL — усе за тебе).
> Зауваж: плейсхолдери працюють для **значень**, не для імен таблиць/колонок.

---

## 3. Масова вставка — `executemany`

Для багатьох рядків — `executemany` з послідовністю кортежів. Швидше за цикл
(один виклик, одна підготовка запиту):

```python
cur.executemany(
    "INSERT INTO users (name, age) VALUES (?, ?)",
    [("Carol", 40), ("Dave", 35), ("Eve", 28)],
)
cur.rowcount                    # 3
```

---

## 4. Транзакції — `with conn:`, commit, rollback

За замовчуванням зміни тримаються у відкритій транзакції й **зникають**, якщо їх
не зафіксувати через `commit()`. Закрив з'єднання без коміту — дані втрачені:

```python
conn = sqlite3.connect("app.db")
conn.execute("INSERT INTO users (name) VALUES ('Frank')")
conn.close()                    # БЕЗ commit() — рядок НЕ збережено
# наступне з'єднання побачить 0 нових рядків
```

> **⚠️ Пастка.** Найчастіша помилка новачка — забути `conn.commit()`. Зміни є в
> поточному з'єднанні, але на диск не потрапили.

Ідіоматичний спосіб — з'єднання як **контекстний менеджер**: `with conn:` коммітить
при успіху й робить `rollback()` при винятку. Це не закриває з'єднання — лише керує
транзакцією (на відміну від `with open(...)`):

```python
with conn:                                  # атомарний блок
    conn.execute("UPDATE acc SET bal = bal - 50 WHERE id = 1")
    conn.execute("UPDATE acc SET bal = bal + 50 WHERE id = 2")
# тут уже зафіксовано; якби всередині стався виняток — rollback усього блоку
```

Ручне керування — `conn.commit()` / `conn.rollback()`. У Python 3.12+ є явний
режим `autocommit`:

```python
conn = sqlite3.connect(":memory:", autocommit=True)   # кожен statement сам по собі
conn.autocommit                 # True
```

> **Best practice.** Обгортай логічні одиниці роботи в `with conn:` — отримуєш
> атомарність безкоштовно, як `db.transaction { ... }` у GRDB. Ручні
> `commit/rollback` лиш коли треба тонкий контроль.

---

## 5. Row factory — доступ за іменем колонки

За замовчуванням рядок — кортеж (доступ за індексом). `sqlite3.Row` дає доступ і
за індексом, і за іменем колонки (зручно й читабельно):

```python
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT id, name FROM users LIMIT 1").fetchone()
row["name"]                     # 'Alice'   — за іменем
row[0]                          # 1         — за індексом теж працює
row.keys()                      # ['id', 'name']
```

Потрібен звичайний `dict` (наприклад, для JSON-відповіді) — власна фабрика:

```python
def dict_factory(cursor, row):
    cols = [col[0] for col in cursor.description]
    return dict(zip(cols, row))

conn.row_factory = dict_factory
conn.execute("SELECT id, name FROM users LIMIT 1").fetchone()
# {'id': 1, 'name': 'Alice'}
```

---

## 6. Типи й схема: динамічна типізація SQLite

SQLite має **динамічну типізацію** (type affinity): оголошений тип колонки —
лише підказка, фактично туди можна покласти будь-що. Це шокує після суворого
Core Data:

```python
conn.execute("CREATE TABLE t (n INTEGER)")
conn.execute("INSERT INTO t VALUES (?)", ("not a number",))
conn.execute("SELECT n, typeof(n) FROM t").fetchone()
# ('not a number', 'text')      — INTEGER-колонка зберегла текст!
```

Маппінг типів Python↔SQLite: `int`→INTEGER, `float`→REAL, `str`→TEXT,
`bytes`→BLOB, `None`→NULL. `bool` зберігається як 0/1, `datetime` — як TEXT
(серіалізуй у ISO-рядок сам). `PRIMARY KEY AUTOINCREMENT` дає автоінкрементний id,
як `@Attribute(.unique)` + автоген у Core Data.

> **⚠️ Пастка.** Не покладайся на БД у валідації типів — SQLite її майже не робить.
> Валідуй на рівні Python (pydantic, Модуль 06), а не сподівайся на `CHECK`.

---

## 7. Закриття й керування ресурсами

З'єднання й курсори — ресурси; закривай їх. `conn.close()` явно, або
`contextlib.closing` для гарантії при винятках (зв'язок із Модулем 10):

```python
from contextlib import closing

with closing(sqlite3.connect("app.db")) as conn:
    with conn:                                  # транзакція
        conn.execute("INSERT INTO users (name) VALUES (?)", ("Grace",))
# тут conn гарантовано закрито, транзакцію зафіксовано
```

Зверни увагу на **дві різні** `with`: зовнішня (`closing`) закриває з'єднання,
внутрішня (`with conn`) керує транзакцією. Сам `sqlite3.Connection` як менеджер
транзакцію фіксує, але з'єднання НЕ закриває — звідси `closing`.

---

## 8. Коли переростати `sqlite3`

`sqlite3` — це сирий драйвер: ти пишеш SQL руками. Для серйозного застосунку це
швидко стає громіздким. Переходь на ORM, коли потрібні:

- **мапінг на об'єкти/типи** замість кортежів — **SQLAlchemy 2.0** / **SQLModel**;
- **міграції схеми** (еволюція БД) — **alembic**;
- **інші СУБД** (PostgreSQL, MySQL) — той самий ORM, інший драйвер.

Це аналог переходу від ручного C-API до GRDB/Core Data у Swift. Деталі екосистеми —
у [хабі Модуля 13](../13-stdlib-and-ecosystem.md) (розділ «Бази даних / ORM»).
Сам `sqlite3` лишається відмінним вибором для локального сховища, кешів і тестів.

---

## Шпаргалка / рецепти

```python
import sqlite3
from contextlib import closing

conn = sqlite3.connect(":memory:")             # або шлях до файлу
conn.row_factory = sqlite3.Row                 # доступ за іменем колонки

conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, x TEXT)")
conn.execute("INSERT INTO t (x) VALUES (?)", ("a",))         # ? — позиційний
conn.execute("SELECT * FROM t WHERE x = :v", {"v": "a"})     # :name — іменований
conn.executemany("INSERT INTO t (x) VALUES (?)", [("b",), ("c",)])  # масово

cur = conn.execute("SELECT * FROM t")
cur.fetchone(); cur.fetchall(); cur.fetchmany(10)            # вибірка
for row in conn.execute("SELECT * FROM t"): ...              # ітерування

with conn:                                                   # транзакція (commit/rollback)
    conn.execute("UPDATE t SET x = ? WHERE id = ?", ("z", 1))

with closing(sqlite3.connect("app.db")) as c:                # гарантоване закриття
    ...

# НІКОЛИ: f"... WHERE name = '{user_input}'"  — SQL-ін'єкція!
# ЗАВЖДИ:  "... WHERE name = ?", (user_input,)
```

## Див. також

- [Модуль 13 — Стандартна бібліотека та екосистема](../13-stdlib-and-ecosystem.md) — хаб, SQLAlchemy/SQLModel/alembic.
- [Файли та серіалізація](files-and-serialization.md) — `json`/`pickle`, коли БД зайва.
- [Тематичний індекс](../INDEX.md).
