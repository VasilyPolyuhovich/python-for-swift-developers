# Модуль 11. Модулі, пакети, проєкти

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 11**

Туторіал: [§6 Модулі](https://docs.python.org/uk/3/tutorial/modules.html),
[§12 Віртуальні середовища](https://docs.python.org/uk/3/tutorial/venv.html).

Система модулів Python концептуально схожа на SwiftPM (modules/targets/packages),
але дрібніша за гранулярністю: **кожен `.py`-файл — це модуль**, а тека з файлами —
пакет.

## 1. Модуль = файл

```
myapp/
├── math_utils.py        # модуль "math_utils"
└── main.py
```

`math_utils.py`:
```python
PI = 3.14159

def square(x: float) -> float:
    return x * x
```

`main.py`:
```python
import math_utils                       # імпорт усього модуля
math_utils.square(4)

from math_utils import square, PI       # імпорт конкретних імен
square(4)

from math_utils import square as sq     # з псевдонімом
import math_utils as mu                 # псевдонім модуля
```

```swift
import MathUtils          // Swift: імпортує весь модуль (target)
```

> **⚠️ Пастка №1.** У Swift `import` тягне весь модуль, і всі public-символи
> доступні. У Python `import math_utils` вимагає префікса `math_utils.square`, а
> `from math_utils import square` вносить `square` у поточний неймспейс. Обирай
> свідомо.

> **Best practice.** Уникай `from module import *` — він засмічує неймспейс і
> ховає походження імен. `ruff` (F403) попередить. Імпортуй явно.

## 2. Пакет = тека

```
myapp/
├── __init__.py          # робить теку пакетом (може бути порожнім)
├── core/
│   ├── __init__.py
│   ├── models.py
│   └── services.py
└── utils/
    ├── __init__.py
    └── text.py
```

```python
from myapp.core.models import User           # абсолютний імпорт (рекомендовано)
from myapp.utils.text import slugify
```

`__init__.py` виконується при імпорті пакета. Часто використовується, щоб
підняти публічний API наверх (як re-export):

```python
# myapp/core/__init__.py
from myapp.core.models import User
from myapp.core.services import UserService

__all__ = ["User", "UserService"]      # явний публічний API пакета
```

Тоді споживач пише коротко: `from myapp.core import User, UserService`.

> **`__all__`** — список публічних імен пакета/модуля. Контролює, що експортує
> `from package import *`, і документує публічний API. Аналог `public`-маркування
> у Swift, але декларативний список.

## 3. Абсолютні vs відносні імпорти

```python
# Абсолютний (РЕКОМЕНДОВАНО — однозначний)
from myapp.utils.text import slugify

# Відносний (від поточного пакета)
from .text import slugify          # . = поточний пакет
from ..core.models import User      # .. = батьківський пакет
```

> **Best practice.** Використовуй **абсолютні** імпорти. Відносні допустимі
> всередині пакета, але абсолютні читабельніші й стабільніші при рефакторингу.

## 4. `if __name__ == "__main__":` — точка входу

```python
def main() -> None:
    print("running")

if __name__ == "__main__":          # виконається ЛИШЕ при прямому запуску
    main()
```

Коли файл запускають напряму (`python main.py`), `__name__ == "__main__"`. Коли
його імпортують, `__name__` — це ім'я модуля. Тобто блок не виконається при
імпорті. Це аналог `@main` у Swift, але як рантайм-перевірка.

> **⚠️ Пастка №2.** Без цієї перевірки код верхнього рівня модуля виконається при
> *кожному імпорті*. Завжди обгортай точку входу в `if __name__ == "__main__":`.

### Циклічні імпорти

Якщо `a.py` імпортує `b`, а `b.py` імпортує `a` — отримаєш `ImportError` або
напівініціалізований модуль (бо імпорт виконує модуль зверху вниз, і на момент
циклу частина імен ще не існує).

```python
# ❌ a.py: from b import foo   ←┐
# ❌ b.py: from a import bar   ←┘  цикл на рівні модуля
```

Як лагодити (за пріоритетом):
1. **Перепроєктуй** — винеси спільне у третій модуль (`common.py`), від якого
   залежать обидва. Цикл зазвичай = знак неправильних меж.
2. **Імпортуй усередині функції** (lazy import) — не на верхньому рівні:
   ```python
   def bar() -> None:
       from a import foo     # імпорт у момент виклику, коли модулі вже готові
       foo()
   ```
3. Імпортуй **модуль**, а не імена (`import a; a.foo()` замість `from a import foo`).

> **Best practice.** Цикл імпортів — майже завжди симптом тісного зв'язування.
> Спершу подумай про межі модулів ([Модуль 08](08-protocols-and-interfaces.md):
> залежності через протоколи), а lazy import лиши як крайній засіб.

### Динамічні імпорти — `importlib`

Коли ім'я модуля відоме лише в рантаймі (плагіни, конфіги):

```python
import importlib

mod = importlib.import_module("json")     # імпорт за рядком-іменем
mod.dumps({"a": 1})                        # '{"a": 1}'

plugin = importlib.import_module(f"myapp.plugins.{name}")   # плагін за іменем
```

Це аналог рефлексивного завантаження; стандартний спосіб робити плагінні системи.

## 5. Структура сучасного проєкту

```
my-project/
├── pyproject.toml          # маніфест (аналог Package.swift)
├── uv.lock                 # lock-файл (аналог Package.resolved)
├── README.md
├── src/
│   └── my_project/         # пакет (зверни увагу: підкреслення, не дефіс)
│       ├── __init__.py
│       ├── core/
│       └── cli.py
└── tests/
    └── test_core.py
```

`pyproject.toml`:
```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["httpx>=0.27"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[dependency-groups]
dev = ["ruff", "pyright", "pytest"]

[tool.pyright]
typeCheckingMode = "strict"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

> **Best practice (`src`-layout).** Тримай код у `src/my_project/`, а не в корені.
> Це запобігає випадковому імпорту з робочої теки замість встановленого пакета й
> ловить помилки пакування. Це сучасний стандарт.

## 6. Залежності та віртуальні середовища

### Концепція

Кожен проєкт має ізольоване **віртуальне середовище** (venv) з власними версіями
залежностей — щоб проєкти не конфліктували. Це як ізоляція залежностей у SwiftPM
на рівні проєкту, але створюється явно.

### З uv (рекомендовано)

```bash
uv add httpx                # додати залежність + оновити lock + встановити
uv add --dev pytest         # dev-залежність
uv remove httpx             # прибрати
uv sync                     # відтворити середовище з lock (на новій машині/CI)
uv run python main.py       # запустити в середовищі проєкту
uv lock --upgrade           # оновити версії в межах обмежень
```

`uv` автоматично створює `.venv/` і `uv.lock`. Тобі майже ніколи не треба
активувати середовище вручну — `uv run` робить це сам.

### Класичний підхід (знати корисно)

```bash
python -m venv .venv            # створити venv
source .venv/bin/activate       # активувати (macOS/Linux)
pip install httpx               # встановити
pip freeze > requirements.txt   # зафіксувати (примітивний lock)
deactivate
```

> **⚠️ Пастка №3.** Ніколи не став пакети в системний/глобальний Python через
> `pip install` без venv — зламаєш систему й створиш конфлікти. Завжди — venv
> (або `uv`, який робить це за тебе).

## 7. Шлях пошуку модулів

Python шукає модулі в `sys.path` (поточна тека, встановлені пакети, stdlib). Коли
проєкт встановлено (`uv sync` робить editable-install), твій пакет імпортується
звідусіль за іменем.

```python
import sys
print(sys.path)        # подивитись, де Python шукає
```

> **⚠️ Пастка №4.** «ModuleNotFoundError» зазвичай означає: пакет не встановлено в
> активне середовище, або структура тек/`__init__.py` неправильна, або плутанина
> з `src`-layout. Перевір `uv sync` і структуру.

## 8. Публікація пакета (коротко)

```bash
uv build                    # зібрати wheel + sdist у dist/
uv publish                  # опублікувати на PyPI
```

PyPI — це аналог реєстру пакетів. Версіонування — семантичне (SemVer), як у SwiftPM.

## 9. Entry points, версія, editable-install

### Console scripts — CLI-команди пакета

Щоб після встановлення пакета з'явилася команда в терміналі (як виконуваний
продукт SwiftPM), оголоси entry point у `pyproject.toml`:

```toml
[project.scripts]
mytool = "my_project.cli:main"     # команда `mytool` → викличе main() з cli.py
```

Після `uv sync`/встановлення `mytool` доступна в середовищі. Це і є механізм
плагінів та CLI-утиліт (так роблять `ruff`, `pytest` тощо).

### `__version__` і `importlib.metadata`

Версію пакета не дублюй вручну — читай із метаданих встановленого дистрибутиву:

```python
from importlib import metadata

__version__ = metadata.version("my-project")   # бере з pyproject (single source)
```

```python
metadata.version("httpx")          # версія залежності (якщо встановлена)
# metadata.version("absent")       # PackageNotFoundError, якщо не встановлено
list(metadata.distributions())     # усі встановлені дистрибутиви
metadata.entry_points()            # доступ до entry points (для плагінних систем)
```

### Editable install

`uv sync` встановлює твій пакет у режимі **editable** (як `pip install -e .`):
зміни в `src/` одразу видно без перевстановлення. Це стандарт для розробки.

### Namespace packages (коротко)

Тека **без** `__init__.py` може бути *namespace package* — пакет, розкиданий по
кількох місцях/дистрибутивах (для плагінних екосистем). Для звичайних проєктів
це не потрібно — додавай `__init__.py`; namespace packages — нішевий інструмент.

## Інструменти та бібліотеки

- **`uv`** — версії Python, venv, залежності, build, publish (усе в одному).
- **`hatchling`** / **`setuptools`** — build-backend (зазвичай `hatchling`).
- **`pip`** — базовий менеджер (uv його замінює, але знати треба).
- **`pipx`** / `uv tool` — встановлення CLI-утиліт ізольовано й глобально.

## Best practices модуля

- Кожен `.py` — модуль; тека з `__init__.py` — пакет.
- Абсолютні імпорти; уникай `import *`.
- `__all__` для явного публічного API.
- Точку входу — в `if __name__ == "__main__":`.
- `src`-layout для серйозних проєктів.
- Завжди venv (через `uv`); ніколи не став у системний Python.
- `pyproject.toml` — єдине джерело правди про проєкт.
- Цикли імпортів лагодь перепроєктуванням, не lazy-import-ами.
- `__version__` бери з `importlib.metadata`, не дублюй; CLI — через `[project.scripts]`.

## Див. також

- [Модуль 00 — Інструментарій](00-tooling-and-mental-model.md) — `uv`, sys.path, import-механіка, `.pyc`.
- [Модуль 08 — Протоколи](08-protocols-and-interfaces.md) — розв'язання залежностей, межі модулів.
- [Модуль 13 — Stdlib](13-stdlib-and-ecosystem.md) — `argparse`/Typer для CLI, екосистема.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 12 — Асинхронність](12-async.md)
