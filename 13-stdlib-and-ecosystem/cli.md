[← Курс](../README.md) · [Модуль 13](../13-stdlib-and-ecosystem.md) · **CLI-застосунки**

Туторіал: [`argparse`](https://docs.python.org/uk/3/library/argparse.html) ·
[Typer](https://typer.tiangolo.com/) · [Rich](https://rich.readthedocs.io/).

У Swift для command-line tool ти береш `swift-argument-parser`: оголошуєш
`struct` із `@Argument`/`@Option`, а бібліотека з типів робить парсинг і `--help`.
У Python та сама ідея вирішується кількома рівнями:

- **`argparse`** — у stdlib, нуль залежностей. Для скриптів і CI-утиліт.
- **Typer** — за духом найближчий до `swift-argument-parser`: типи функції →
  CLI. Рекомендований для «справжніх» застосунків.
- **Rich** — гарний вивід (кольори, таблиці, прогрес-бари, трейсбеки).
- **Click** — низькорівнева основа, на якій збудований Typer.

> **Усі приклади на цій сторінці реально запущені** (Python 3.14, Typer 0.26,
> Rich 15) — окрім позначених як ілюстративні. Вивід наведено в `#`-коментарях.

## 1. `argparse` — стандарт без залежностей

Базовий цикл: створити `ArgumentParser`, додати аргументи, викликати
`parse_args()`. Результат — об'єкт `Namespace` із полями за іменами аргументів.

```python
import argparse

parser = argparse.ArgumentParser(prog="greet", description="Привітати когось")
parser.add_argument("name", help="ім'я")                       # позиційний
parser.add_argument("-c", "--count", type=int, default=1,      # опція з типом
                    help="скільки разів")
parser.add_argument("--shout", action="store_true",            # прапорець → bool
                    help="ВЕЛИКИМИ")
parser.add_argument("--lang", choices=["en", "uk"], default="en")
parser.add_argument("--tags", nargs="*", default=[])           # 0+ значень

args = parser.parse_args()             # реальний CLI: читає sys.argv
print(args.name, args.count, args.shout)
```

### Перевірка без реального терміналу

`parse_args()` приймає список рядків — зручно для тестів і щоб побачити
результат без запуску бінарника:

```python
args = parser.parse_args(["Vasyl", "-c", "2", "--shout", "--lang", "uk",
                          "--tags", "a", "b"])
print(args)
# Namespace(name='Vasyl', count=2, shout=True, lang='uk', tags=['a', 'b'])
```

Ключові опції `add_argument`:

| Параметр | Призначення | Swift-аналог |
|----------|-------------|--------------|
| позиційний `"name"` | обов'язковий аргумент | `@Argument` |
| `"-c", "--count"` | опція (короткий + довгий) | `@Option` |
| `type=int` | конвертація рядка (і валідація) | тип властивості |
| `default=...` | значення за замовчуванням | default value |
| `choices=[...]` | допустимі значення | `ExpressibleByArgument` enum |
| `nargs="*"` / `"+"` / `2` | 0+ / 1+ / рівно N значень | масив-аргумент |
| `action="store_true"` | прапорець → `bool` | `@Flag` |
| `required=True` | зробити опцію обов'язковою | — |
| `help="..."` | текст у `--help` | `help:` |

`argparse` сам генерує `--help`, повідомлення про помилки й завершує процес із
кодом `2` при невалідному вводі.

> **⚠️ Пастка.** `parse_args()` при помилці чи `--help` викликає `sys.exit()`,
> а не повертає значення й не кидає виняток, який ти ловиш. Це навмисно для CLI,
> але якщо парсиш аргументи всередині бібліотеки/тесту — будь готовий до
> `SystemExit` (його можна перехопити: `except SystemExit`).

### Sub-commands (`add_subparsers`)

Як `git add` / `git commit` — кожна підкоманда має власний набір аргументів.
У `swift-argument-parser` це `CommandConfiguration(subcommands:)`.

```python
import argparse

parser = argparse.ArgumentParser(prog="tool")
sub = parser.add_subparsers(dest="command", required=True)

p_add = sub.add_parser("add", help="додати")
p_add.add_argument("item")

p_list = sub.add_parser("list", help="показати")
p_list.add_argument("--all", action="store_true")

print(parser.parse_args(["add", "milk"]))     # Namespace(command='add', item='milk')
print(parser.parse_args(["list", "--all"]))   # Namespace(command='list', all=True)
```

`dest="command"` кладе ім'я обраної підкоманди в `args.command` — далі
диспетчеризуєш через `match`/`if`.

> **Best practice.** `argparse` — правильний вибір, коли важлива нуль-залежність:
> скрипти в репозиторії, CI, внутрішні утиліти. Не тягни сторонній пакет заради
> розбору двох прапорців.

## 2. Typer — CLI з type hints (рекомендовано)

Typer (від автора FastAPI, поверх Click) робить те саме, що
`swift-argument-parser`, але декларація — це **звичайна функція з анотаціями**.

```swift
// Swift — swift-argument-parser
struct Greet: ParsableCommand {
    @Argument var name: String
    @Option var count: Int = 1
    @Flag var shout = false
    func run() { /* ... */ }
}
```

```python
import typer

def main(name: str, count: int = 1, shout: bool = False) -> None:
    """Привітати когось."""
    text = f"Hello {name}"
    if shout:
        text = text.upper()
    for _ in range(count):
        print(text)

if __name__ == "__main__":
    typer.run(main)            # типи → аргументи + --help автоматично
```

Тип параметра визначає поведінку: параметр **без default** → позиційний
(`@Argument`), **з default** → опція (`--count`), `bool` → парний прапорець
(`--shout` / `--no-shout`). Docstring стає описом у `--help`:

```text
$ python greet.py --help
 Usage: greet.py [OPTIONS] NAME

 Привітати когось.

╭─ Arguments ──────────────────────────────────╮
│ *    name      TEXT  [required]              │
╰──────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────╮
│ --count          INTEGER  [default: 1]       │
│ --shout  --no-shout       [default: no-shout]│
│ --help                    Show this message  │
╰──────────────────────────────────────────────╯

$ python greet.py Vasyl --count 2 --shout
HELLO VASYL
HELLO VASYL
```

### `typer.Argument` / `typer.Option` через `Annotated`

Для help-текстів і тонкого налаштування — анотуй тип через `Annotated`
(аналог пояснень у пропертях `@Option(help:)`):

```python
import typer
from typing import Annotated

app = typer.Typer(help="Менеджер завдань.")

@app.command()                                          # підкоманда `add`
def add(
    title: Annotated[str, typer.Argument(help="назва задачі")],
    priority: Annotated[int, typer.Option(help="пріоритет")] = 1,
) -> None:
    """Додати задачу."""
    print(f"added {title!r} (p={priority})")

@app.command()                                          # підкоманда `ls`
def ls(all: Annotated[bool, typer.Option(help="показати всі")] = False) -> None:
    """Показати задачі."""
    print(f"list all={all}")

if __name__ == "__main__":
    app()
```

```text
$ python tasks.py add "buy milk" --priority 3
added 'buy milk' (p=3)

$ python tasks.py ls --all
list all=True
```

`@app.command()` реєструє кожну функцію як sub-command — це Typer-аналог
`add_subparsers`, але без ручної маршрутизації.

### Встановити як справжню команду

Щоб після `uv sync` з'явилася команда в терміналі (як виконуваний продукт
SwiftPM), оголоси entry point у `pyproject.toml` — деталі в
[Модулі 11 · Console scripts](../11-modules-and-packages.md):

```toml
[project.scripts]
tasks = "my_project.cli:app"     # команда `tasks` → Typer-app з cli.py
```

> **Best practice.** Для CLI, який ти **поширюєш** (внутрішня тула, утиліта на
> PyPI), бери Typer + `[project.scripts]`. Менше шаблону, безкоштовний `--help`,
> автодоповнення в shell, чудові помилки. `argparse` лиши для самодостатніх
> скриптів без залежностей.

## 3. Rich — гарний вивід у терміналі

Rich дає кольори, стилі, таблиці, прогрес-бари й читабельні трейсбеки. Typer уже
тягне Rich як залежність, тож вивід підкоманд автоматично оформлений.

```python
from rich.console import Console
from rich.table import Table

console = Console()
console.print("[bold green]OK[/] готово, [red]помилка[/] тут")

table = Table(title="Задачі")
table.add_column("ID", justify="right")
table.add_column("Назва")
table.add_column("Статус")
table.add_row("1", "buy milk", "[green]done[/]")
table.add_row("2", "write CLI", "[yellow]wip[/]")
console.print(table)
```

```text
          Задачі
┏━━━━┳━━━━━━━━━━━┳━━━━━━━━┓
┃ ID ┃ Назва     ┃ Статус ┃
┡━━━━╇━━━━━━━━━━━╇━━━━━━━━┩
│  1 │ buy milk  │ done   │
│  2 │ write CLI │ wip    │
└────┴───────────┴────────┘
```

Прогрес-бар і кращі трейсбеки (ілюстративно — не друкуються одним рядком):

```python
import time
from rich.progress import track
from rich.traceback import install

install(show_locals=True)          # гарні трейсбеки на весь процес

for _ in track(range(100), description="обробка..."):
    time.sleep(0.01)               # автоматичний прогрес-бар у терміналі
```

> **Best practice.** `print` — для машинно-читаного stdout (його парсять інші
> інструменти, пайплайни). Rich-оформлення — для людини; перевіряй
> `Console().is_terminal`, щоб не засмічувати вивід ESC-кодами в пайпі.

## 4. Click — основа під Typer

[Click](https://click.palletsprojects.com/) — зріла бібліотека на декораторах
(`@click.command`, `@click.option`). Typer збудований поверх неї й покриває
більшість потреб декларативніше. Бери Click напряму лише коли потрібні складні
сценарії, яких Typer не покриває (нестандартні групи, кастомні типи параметрів).

```python
import click                       # ілюстративно

@click.command()
@click.argument("name")
@click.option("--count", default=1)
def main(name: str, count: int) -> None:
    for _ in range(count):
        click.echo(f"Hello {name}")
```

## Шпаргалка / рецепти

| Завдання | Рецепт |
|----------|--------|
| Зеро-залежний скрипт | `argparse.ArgumentParser()` → `parse_args()` |
| Позиційний аргумент | `add_argument("name")` |
| Опція з типом/default | `add_argument("--count", type=int, default=1)` |
| Прапорець-bool | `add_argument("--shout", action="store_true")` |
| Обмежені значення | `add_argument("--lang", choices=["en", "uk"])` |
| Кілька значень | `add_argument("--tags", nargs="*")` |
| Підкоманди (argparse) | `p.add_subparsers(dest="command", required=True)` |
| Тест парсера | `parser.parse_args(["...", "..."])` (без `sys.argv`) |
| Сучасний CLI | `typer.run(main)` або `app = typer.Typer()` + `@app.command()` |
| Help із docstring | Typer бере опис із docstring функції автоматично |
| Help-текст аргумента | `Annotated[str, typer.Option(help="...")]` |
| Підкоманди (Typer) | кілька `@app.command()` |
| Команда в терміналі | `[project.scripts]` у `pyproject.toml` (Модуль 11) |
| Кольори/таблиці | `rich.console.Console().print(...)`, `rich.table.Table` |
| Прогрес-бар | `rich.progress.track(iterable)` |
| Кращі трейсбеки | `rich.traceback.install()` |

**Правило вибору:** `argparse` — нуль залежностей (скрипти, CI); **Typer** —
справжні CLI-застосунки; **Rich** — оформлення виводу; **Click** — основа Typer,
лише для крайових випадків.

## Див. також

- [Модуль 13 — Стандартна бібліотека та екосистема](../13-stdlib-and-ecosystem.md) — повна карта екосистеми.
- [Запуск процесів та ОС](subprocess-and-os.md) — `subprocess`, `os`, `sys.argv`.
- [Модуль 11 — Модулі та пакети](../11-modules-and-packages.md) — `[project.scripts]` / console scripts для поширення CLI як команди.
- [Тематичний індекс](../INDEX.md).
