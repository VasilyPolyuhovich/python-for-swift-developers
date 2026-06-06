# Модуль 13. Стандартна бібліотека та екосистема

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 13**

Туторіал: [§10–11 Огляд стандартної бібліотеки](https://docs.python.org/uk/3/tutorial/stdlib.html).

**Поглиблені сторінки модуля** (реальні приклади використання):

| Сторінка | Про що |
|----------|--------|
| [Файли та серіалізація](13-stdlib-and-ecosystem/files-and-serialization.md) | `pathlib`, `open`, `tempfile`, `shutil`, `json`, `pickle`, zip/gzip, csv |
| [Дати та час](13-stdlib-and-ecosystem/datetime.md) | `datetime`, `zoneinfo`, `timedelta`, парсинг/форматування |
| [Регулярні вирази](13-stdlib-and-ecosystem/regex.md) | `re`: патерни, групи, `sub`, прапори, рецепти |
| [Процеси та ОС](13-stdlib-and-ecosystem/subprocess-and-os.md) | `subprocess`, `os`, `sys`, env, `shlex` |
| [CLI-застосунки](13-stdlib-and-ecosystem/cli.md) | `argparse`, Typer, Rich |
| [SQLite](13-stdlib-and-ecosystem/sqlite.md) | `sqlite3`: запити, параметри, транзакції, `Row` |
| [Тестування](13-stdlib-and-ecosystem/pytest.md) | `pytest`: assert, `raises`, parametrize, fixtures |
| [Паралелізм](13-stdlib-and-ecosystem/concurrency.md) | `concurrent.futures`, `threading`, `multiprocessing` |

Нижче — карта-огляд stdlib і екосистеми; за реальними прикладами йди на сторінки вище.

Цей модуль — карта: що з Foundation/інших фреймворків Swift чим замінюється в
Python, і які бібліотеки PyPI є стандартом де-факто за напрямами. Python славиться
гаслом «batteries included» — багато з того, для чого у Swift потрібен Foundation
чи сторонні пакети, тут у stdlib.

## Частина 1. Стандартна бібліотека (мапінг на Foundation)

### Файли та шляхи — `pathlib`

Замість рядкових шляхів — об'єктний `Path` (аналог `URL`/`FileManager`):

```python
from pathlib import Path

p = Path.home() / "projects" / "data.json"     # / — оператор з'єднання шляхів
p.exists()
p.suffix                  # ".json"
p.stem                    # "data"
p.parent                  # тека
p.read_text(encoding="utf-8")
p.write_text("...", encoding="utf-8")
list(Path(".").glob("**/*.py"))                 # рекурсивний пошук
```

> **Best practice.** Завжди `pathlib.Path`, ніколи рядкові маніпуляції шляхами
> (`os.path.join`). Це сучасний стандарт, читабельніший і кросплатформенний.

### Дати й час — `datetime`, `zoneinfo`

```python
from datetime import datetime, timedelta, UTC
from zoneinfo import ZoneInfo

now = datetime.now(UTC)                           # завжди з таймзоною!
kyiv = now.astimezone(ZoneInfo("Europe/Kyiv"))
later = now + timedelta(hours=3)
now.isoformat()                                   # ISO 8601
datetime.fromisoformat("2025-01-15T10:00:00+00:00")
```

> **⚠️ Пастка.** Уникай «наївних» datetime без таймзони. Завжди працюй із
> timezone-aware (`datetime.now(UTC)`), як радять і в Swift із `Date`/`Calendar`.

### JSON — `json`

```python
import json

data = json.loads('{"id": 1}')                    # рядок → dict
text = json.dumps({"id": 1}, indent=2)            # dict → рядок
```

Для типізованої серіалізації (як `Codable`) — `pydantic` (Модуль 06), не голий `json`.

### Колекції, функції, ітерування

| Завдання | Модуль |
|----------|--------|
| `Counter`, `deque`, `defaultdict` | `collections` |
| `cache`, `reduce`, `partial`, `total_ordering` | `functools` |
| `count`, `chain`, `islice`, `groupby` | `itertools` |
| `Decimal` (фінанси), `Fraction` | `decimal`, `fractions` |
| Регулярні вирази | `re` |
| Випадковість | `random`, `secrets` (крипто) |
| Математика, статистика | `math`, `statistics` |

### Інше корисне з stdlib

```python
import logging              # логування (НЕ print у продакшені)
import subprocess           # запуск зовнішніх процесів (~ Process)
import os, sys              # ОС, аргументи, env
import argparse             # парсинг CLI-аргументів (базовий)
import sqlite3              # вбудована БД (як у Swift)
import http.server          # простий HTTP-сервер
import unittest             # тести (але краще pytest)
import dataclasses, enum, abc, typing, contextlib    # бачили в попередніх модулях
```

### Логування замість print

```python
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

logger.info("started")
logger.warning("low memory: %s MB", free)         # лінива інтерполяція
logger.exception("failed")                          # з трейсбеком (у except-блоці)
```

> **Best practice.** У бібліотеках/сервісах — `logging`, не `print`. Дає рівні,
> формати, маршрутизацію. `print` — лише для CLI-виводу користувачу й дрібних
> скриптів. Сучасна альтернатива з кращим DX — `structlog` або `loguru`.

## Частина 2. Екосистема за напрямами

Нижче — стандарти де-факто. Усі ставляться через `uv add <пакет>`.

### Тестування

- **`pytest`** — стандарт (замість `unittest`). Простий, потужний, плагіни.
  ```python
  def test_square() -> None:
      assert square(4) == 16

  import pytest
  def test_raises() -> None:
      with pytest.raises(ValueError):
          parse("bad")
  ```
  Аналог swift-testing/XCTest, але мінімалістичніший (звичайний `assert`).
- **`hypothesis`** — property-based тестування (генерує вхідні дані).
- **`coverage`** / `pytest-cov` — покриття.

### HTTP-клієнти

- **`httpx`** — сучасний, sync + async, HTTP/2. Рекомендований.
- **`requests`** — класичний sync, дуже поширений (але без async).

```python
import httpx
resp = httpx.get("https://api.example.com/users")
resp.raise_for_status()
data = resp.json()
```

### Web-фреймворки (бекенд)

- **FastAPI** — сучасний, async, на `pydantic` + типах. Автодокументація (OpenAPI),
  валідація з коробки. Найкращий вибір для нових API.
  ```python
  from fastapi import FastAPI
  from pydantic import BaseModel

  app = FastAPI()

  class Item(BaseModel):
      name: str
      price: float

  @app.post("/items")
  async def create(item: Item) -> Item:        # валідація автоматична
      return item
  ```
- **Django** — «батарейки включені» (ORM, адмінка, auth) для великих застосунків.
- **Flask** — мінімалістичний, гнучкий, sync.
- **Litestar** — сучасна альтернатива FastAPI.

ASGI-сервер для запуску async-застосунків: **`uvicorn`**.

### Бази даних / ORM

- **SQLAlchemy 2.0** — стандарт ORM + Core (типізований API). Аналог потужного
  Core Data / GRDB.
- **SQLModel** — SQLAlchemy + pydantic від автора FastAPI.
- **`asyncpg`** / **`psycopg`** — драйвери PostgreSQL.
- **`alembic`** — міграції схеми.

### Дані, наука, ML (релевантно твоєму CoreML/CV-досвіду)

- **NumPy** — масиви й лінійна алгебра. Фундамент усього наукового стеку.
  ```python
  import numpy as np
  a = np.array([[1, 2], [3, 4]])
  a @ a.T                    # матричне множення
  ```
- **pandas** — таблиці/DataFrame (аналог роботи з табличними даними). Стандарт
  для аналізу.
- **Polars** — швидша сучасна альтернатива pandas (на Rust, lazy).
- **PyTorch** — нейромережі, де-факто стандарт досліджень/продакшену. Якщо ти
  деплоїш CoreML-моделі — тренування часто саме тут, із подальшою конвертацією
  через **`coremltools`**.
- **scikit-learn** — класичний ML (не нейромережі).
- **OpenCV** (`opencv-python`) / **Pillow** — комп'ютерний зір та обробка
  зображень (аналог CoreImage/Vision). Для YOLO — `ultralytics`.
- **Matplotlib** / **Plotly** — візуалізація.

### CLI-застосунки

- **Typer** — CLI на основі type hints (від автора FastAPI). Найприємніший DX.
  ```python
  import typer

  def main(name: str, count: int = 1) -> None:
      for _ in range(count):
          print(f"Hello {name}")

  if __name__ == "__main__":
      typer.run(main)            # типи → аргументи + --help автоматично
  ```
- **Click** — потужний, на якому базується Typer.
- **Rich** — кольоровий вивід, таблиці, прогрес-бари в терміналі.
- **argparse** (stdlib) — базовий, без залежностей.

### Конфігурація та валідація

- **`pydantic`** / **`pydantic-settings`** — моделі даних і конфіги з env/файлів.
- **`python-dotenv`** — читання `.env`.

### Дата-інженерія / завдання

- **`celery`** — черги завдань.
- **`APScheduler`** — планувальник.
- **`tenacity`** — ретраї.

### Карта «Swift → Python» (швидкий довідник)

| Swift / iOS | Python |
|-------------|--------|
| `URLSession` | `httpx` / `requests` |
| `Codable` | `pydantic` |
| `FileManager`/`URL` | `pathlib` |
| `Date`/`Calendar` | `datetime` + `zoneinfo` |
| Core Data / GRDB | SQLAlchemy / SQLModel |
| Combine / async streams | `asyncio` + `anyio` |
| CoreImage / Vision | OpenCV / Pillow |
| CoreML (інференс) | PyTorch + `coremltools` (тренування/конвертація) |
| XCTest / swift-testing | `pytest` |
| SwiftLint / swift-format | `ruff` |
| SwiftPM | `uv` + `pyproject.toml` |

## Best practices модуля

- `pathlib` для шляхів, timezone-aware `datetime` для часу, `logging` замість `print`.
- Перш ніж тягнути залежність — перевір stdlib («batteries included»).
- Стандартний набір нового проєкту: `uv` + `ruff` + `pyright` + `pytest`.
- Для типових напрямів є чіткі стандарти: API → FastAPI, дані → pandas/Polars,
  ML → PyTorch, CLI → Typer, HTTP → httpx, валідація → pydantic.
- Не винаходь — спирайся на de-facto стандарти екосистеми.

## Див. також

- Сторінки модуля: [файли](13-stdlib-and-ecosystem/files-and-serialization.md) · [дати](13-stdlib-and-ecosystem/datetime.md) · [regex](13-stdlib-and-ecosystem/regex.md) · [процеси](13-stdlib-and-ecosystem/subprocess-and-os.md) · [CLI](13-stdlib-and-ecosystem/cli.md) · [SQLite](13-stdlib-and-ecosystem/sqlite.md) · [pytest](13-stdlib-and-ecosystem/pytest.md) · [паралелізм](13-stdlib-and-ecosystem/concurrency.md).
- [Модуль 12 — Async](12-async.md) — `asyncio`, `httpx`, `anyio`.
- [Модуль 03 — Структури даних](03-data-structures.md) — `collections`, `heapq`, `bisect`.
- [Тематичний індекс](INDEX.md).

---

## Завершення курсу

Ти пройшов шлях від ментальної моделі (reference semantics, динамічна типізація)
через синтаксис, функції, типи, ООП, дженеріки, протоколи, ітерування, помилки,
модулі й асинхронність — щоразу через призму того, що вже знаєш зі Swift.

Головні зсуви мислення, які варто закріпити:

1. **Reference semantics за замовчуванням** — копіюй свідомо.
2. **Динамічна типізація + `pyright` strict** — це твоя заміна компілятору.
3. **Structural typing (`Protocol`)** — відповідність за формою, не за оголошенням.
4. **`asyncio` ≠ паралелізм** — GIL; async лише для I/O.
5. **Винятки неявні** — сигнатура їх не показує; дисципліна й `with` для ресурсів.

Куди далі: офіційний [HOWTO з типів](https://docs.python.org/3/library/typing.html),
[PEP 8](https://peps.python.org/pep-0008/), документація `asyncio`, та практика —
перепиши якийсь свій невеликий Swift-інструмент на Python із `uv` + `ruff` +
`pyright` + `pytest`.

**Назад до [README / змісту курсу](README.md).**
