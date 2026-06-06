# Python для Swift-розробника

[![Читати онлайн](https://img.shields.io/badge/📖_Читати_онлайн-MkDocs_сайт-blue)](https://vasilypolyuhovich.github.io/python-for-swift-developers/)
[![Python](https://img.shields.io/badge/Python-3.13_|_3.14-blue?logo=python&logoColor=white)](https://www.python.org/)

> **📖 Зручніше читати на сайті з пошуком:**
> **https://vasilypolyuhovich.github.io/python-for-swift-developers/**

Курс вивчення Python через порівняння зі Swift. Розрахований на досвідченого
розробника, який вже добре знає Swift (типи, протоколи, дженеріки, `async/await`)
і хоче швидко й *правильно* перейти на Python — без легасі-звичок.

## Ідея

Більшість концепцій Python мапляться на Swift майже один-до-одного. Тому курс
фокусується не на «що таке клас», а на **точках розходження**, де інтуїція зі
Swift підводить: reference semantics за замовчуванням, динамічна типізація,
structural typing (duck typing), mutable default arguments, GIL тощо.

Кожен модуль побудований за єдиною схемою:

1. **Як це у Swift** — твоя відправна точка.
2. **Як це в Python** — ідіоматичний приклад.
3. **⚠️ Пастки** — де семантика відрізняється і де ламається інтуїція.
4. **Best practices + інструменти** — чим це реально вирішують у продакшені.

## Орієнтири

- **Версія:** Python 3.13 / 3.14 (сучасний синтаксис: PEP 695-дженеріки
  `class Stack[T]`, `match`, `X | None` замість `Optional[X]`).
- **Стиль:** type hints скрізь, [PEP 8](https://peps.python.org/pep-0008/),
  [PEP 257](https://peps.python.org/pep-0257/) (docstrings).
- **Джерело структури:** офіційний
  [Python Tutorial](https://docs.python.org/uk/3/tutorial/index.html).

## Програма

| #  | Модуль | Туторіал | Ключовий контраст зі Swift |
|----|--------|----------|----------------------------|
| 00 | [Інструментарій і ментальна модель](00-tooling-and-mental-model.md) | — | Xcode/SwiftPM → uv/ruff/pyright |
| 01 | [Синтаксис і керування потоком](01-syntax-and-control-flow.md) | §3–4 | `switch` → `match`, відступи замість `{}` |
| 02 | [Функції](02-functions.md) | §4.8–4.10 | argument labels → keyword args |
| 03 | [Структури даних](03-data-structures.md) | §5 | `Array/Set/Dict` → `list/set/dict` |
| 04 | [Складні типи та система типів](04-types-and-typing.md) | — | `Optional` → `X \| None`, mypy/pyright |
| 05 | [Класи та ООП](05-classes-and-oop.md) | §9 | `class` → `class`, але reference усюди |
| 06 | [«Структури» та value-типи](06-structs-and-value-types.md) | — | `struct` → `@dataclass`/`NamedTuple` |
| 07 | [Дженеріки](07-generics.md) | — | прямий мапінг, PEP 695 |
| 08 | [Інтерфейси / протоколи](08-protocols-and-interfaces.md) | — | nominal → structural typing |
| 09 | [Ітератори та генератори](09-iterators-and-generators.md) | §9.8–9.10 | `Sequence` → `__iter__`/`yield` |
| 10 | [Помилки та винятки](10-errors-and-exceptions.md) | §8 | `do/try/catch` → `try/except` |
| 11 | [Модулі, пакети, проєкти](11-modules-and-packages.md) | §6, §12 | SwiftPM → pyproject.toml |
| 12 | [Асинхронність](12-async.md) | — | Swift Concurrency → asyncio + GIL |
| 13 | [Стандартна бібліотека та екосистема](13-stdlib-and-ecosystem.md) | §10–11 | Foundation → stdlib + PyPI |

## Як проходити

Модулі впорядковані за наростанням. Якщо хочеш одразу до найцікавіших контрастів —
почни з **08 (протоколи)**, **07 (дженеріки)**, **12 (async)**: там різниця зі
Swift найбільш повчальна.

Курс має дві осі навігації:

- **Послідовно** — за таблицею-програмою вище (модуль за модулем).
- **За задачею** — [**Тематичний індекс**](INDEX.md): «як відсортувати», «як
  сконвертувати тип», «як працювати з рядками» тощо, з прямими посиланнями.

Великі модулі мають **поглиблені під-сторінки** (у теці з тією самою назвою) —
повні довідники з прикладами. Хаб модуля містить огляд і посилання на них. Усі
нетривіальні приклади перевірені реальним запуском на Python 3.14.

## Швидкий старт середовища

```bash
# Встанови uv (єдиний інструмент для версій Python, venv та залежностей)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Створи проєкт
uv init python-playground && cd python-playground
uv add --dev ruff pyright pytest

# Запусти REPL у середовищі проєкту
uv run python
```

Деталі — у [Модулі 00](00-tooling-and-mental-model.md).
