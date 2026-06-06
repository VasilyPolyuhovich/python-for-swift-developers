# Процеси та ОС

[← Курс](../README.md) · [Модуль 13](../13-stdlib-and-ecosystem.md) · **Процеси та ОС**

У Swift ти запускаєш зовнішні команди через `Process` (раніше `NSTask`), читаєш
середовище й аргументи через `ProcessInfo`, а файлову систему чіпаєш через
`FileManager`. У Python ці ролі розкладені по кількох модулях stdlib:
`subprocess` (запуск процесів), `os`/`sys` (середовище, аргументи, платформа) і
`pathlib` (шляхи — окрема [сторінка про файли](files-and-serialization.md)).

---

## 1. `subprocess.run` — сучасний API

`subprocess.run()` — це 95% усіх потреб. Аналог налаштувати `Process`, запустити
й дочекатися завершення, але одним викликом:

```python
import subprocess

r = subprocess.run(
    ["echo", "hello"],          # СПИСОК аргументів, не рядок!
    capture_output=True,        # захопити stdout/stderr
    text=True,                  # bytes → str (декодування), інакше отримаєш bytes
    check=True,                 # ненульовий код → виняток
)
r.stdout        # 'hello\n'
r.stderr        # ''
r.returncode    # 0
```

Об'єкт `CompletedProcess` несе `.stdout`, `.stderr`, `.returncode` та `.args`.
Без `capture_output=True` вивід піде у термінал, а `.stdout` буде `None`.

```swift
// Swift-аналог — помітно багатослівніший
let p = Process()
p.executableURL = URL(filePath: "/bin/echo")
p.arguments = ["hello"]
let pipe = Pipe(); p.standardOutput = pipe
try p.run(); p.waitUntilExit()
let out = String(decoding: pipe.fileHandleForReading.readDataToEndOfFile(), as: UTF8.self)
```

### Чому СПИСОК аргументів, а не рядок

Список `["ls", "-la", path]` передається ядру напряму — без shell, без розбиття
на слова, без підстановок. Це безпечно: `path` не може «вирватися» й виконати
сторонню команду.

> **⚠️ Пастка: `shell=True` і command injection.** Спокусливо написати
> `subprocess.run(f"ls {user_input}", shell=True)`. Але тоді рядок інтерпретує
> shell, і `user_input = "; rm -rf ~"` виконає видалення. Це класична діра
> (як інтерполяція в SQL/shell). Уникай `shell=True`; передавай список аргументів.
> Якщо shell справді потрібен (pipe-и, glob-и) — не клей рядки з вводу користувача.

---

## 2. Помилки: `check=True` та `timeout=`

З `check=True` ненульовий код завершення кидає `CalledProcessError`, який несе
`.returncode`, `.stdout`, `.stderr` (зручно для логів):

```python
try:
    subprocess.run(["ls", "/no/such/path"], capture_output=True, text=True, check=True)
except subprocess.CalledProcessError as e:
    e.returncode      # 1
    e.stderr          # 'ls: /no/such/path: No such file or directory\n'
```

`timeout=` (у секундах) обмежує час; перевищення → `TimeoutExpired`, а процес
вбивається:

```python
try:
    subprocess.run(["sleep", "5"], timeout=0.1)
except subprocess.TimeoutExpired:
    print("надто довго")   # надто довго
```

> **Best practice.** Майже завжди став `check=True` + `text=True` +
> `capture_output=True`, а для будь-чого зовнішнього — `timeout=`. Це робить
> провали гучними (виняток), а не тихими (проігнорований `returncode`).

---

## 3. `input=`, `env=`, `cwd=`

```python
# input= — подати у stdin процесу (з text=True це str)
r = subprocess.run(["cat"], input="line\n", capture_output=True, text=True)
r.stdout                                  # 'line\n'

# env= — ПОВНІСТЮ замінює середовище (а не доповнює!)
r = subprocess.run(["printenv", "GREETING"], capture_output=True, text=True,
                   env={"GREETING": "hi"})
r.stdout                                  # 'hi\n'

# cwd= — робоча тека дочірнього процесу
r = subprocess.run(["pwd"], capture_output=True, text=True, cwd="/tmp")
r.stdout                                  # '/private/tmp\n' (на macOS /tmp → /private/tmp)
```

> **⚠️ Пастка: `env=` замінює, а не доповнює.** Якщо передати `env={"X": "1"}`,
> дочірній процес втратить `PATH` й усе інше — команда може не знайтися. Щоб
> *додати* змінну, копіюй поточне середовище: `env={**os.environ, "X": "1"}`.

---

## 4. Pipe-и та стрімінг: `Popen`

`run()` чекає завершення й віддає весь вивід разом. Для потокового читання
(довгі процеси, читання рядок-за-рядком) є нижчорівневий `Popen`:

```python
import subprocess

with subprocess.Popen(["printf", "a\nb\nc\n"], stdout=subprocess.PIPE, text=True) as proc:
    for line in proc.stdout:              # читаємо в реальному часі
        print("got:", line.rstrip())
# got: a
# got: b
# got: c
```

Для з'єднання команд (pipe) краще не плодити shell, а з'єднати два `Popen`
(`stdout` першого → `stdin` другого) або просто обробити вивід першого в Python.
Але в більшості випадків `run()` достатньо.

---

## 5. `os` та `os.path` — мінімум, решта через `pathlib`

Історично шляхи робили рядками через `os.path`. Сьогодні для шляхів — `pathlib`
(див. [файли та серіалізація](files-and-serialization.md)). З `os` лишається
насправді корисне середовище й системні факти:

```python
import os

os.environ.get("HOME", "/tmp")     # змінна середовища з дефолтом (не KeyError)
os.getenv("MISSING", "fallback")   # 'fallback' — те саме, коротший синтаксис
os.cpu_count()                     # к-сть CPU (для пулів/паралелізму), int або None
```

> **Best practice.** Читай env через `os.environ.get(name, default)` (або
> `os.getenv`), а не `os.environ[name]` — інакше відсутня змінна = `KeyError`.
> Для шляхів — `pathlib.Path`, не `os.path.join`.

---

## 6. `sys` — аргументи, вихід, платформа

`sys` — це приблизно `ProcessInfo` + точка виходу процесу:

```python
import sys

sys.argv          # список аргументів: ['script.py', 'arg1', ...] (argv[0] — ім'я)
sys.exit(1)       # завершити з кодом (0 = успіх; як exit(_:) у C)
sys.platform      # 'darwin' (macOS), 'linux', 'win32'
sys.version_info  # (3, 14, ...) — перевірка версії Python: sys.version_info >= (3, 12)
sys.stdin, sys.stdout, sys.stderr   # потоки (читання pipe-вводу, вивід у stderr)
```

```swift
// Swift-аналоги
CommandLine.arguments          // ~ sys.argv
exit(1)                        // ~ sys.exit(1)
ProcessInfo.processInfo.environment["HOME"]   // ~ os.environ.get
```

> **⚠️ Пастка: `sys.argv[0]` — це ім'я скрипта.** Реальні аргументи починаються з
> `sys.argv[1:]`. Для будь-чого складнішого за один-два аргументи бери `argparse`
> (stdlib) або `Typer` ([Модуль 13](../13-stdlib-and-ecosystem.md)) — не парси `argv` руками.

---

## 7. Розбір командного рядка: `shlex.split`

Коли команда приходить як цілий рядок (з конфігу, від користувача), не діли її
наївним `.split()` — він зламається на лапках і пробілах усередині. `shlex.split`
розбирає за правилами shell:

```python
import shlex

shlex.split('ls -la "my dir"')     # ['ls', '-la', 'my dir']
subprocess.run(shlex.split(cmd))   # потім передаємо як список — безпечно
```

Це безпечніше за `shell=True`: ти отримуєш список аргументів, а не віддаєш рядок
на інтерпретацію shell.

---

## 8. Асинхронний запуск: `asyncio.create_subprocess_exec`

Якщо ти всередині async-коду й не хочеш блокувати цикл подій на час роботи
процесу — є асинхронний аналог (деталі в [Модулі 12](../12-async.md)):

```python
import asyncio

async def main() -> None:
    proc = await asyncio.create_subprocess_exec(
        "echo", "hi",
        stdout=asyncio.subprocess.PIPE,
    )
    out, _ = await proc.communicate()
    print(out.decode())              # hi

asyncio.run(main())
```

Синхронний `subprocess.run` заблокував би весь цикл подій — у async-сервісі це
неприйнятно (як викликати блокуючий `Process.waitUntilExit()` на головній черзі).

---

## Конфігурація: env-змінні правильно

Читати поодинокі змінні через `os.environ.get` — нормально для дрібниць. Але для
*справжньої* конфігурації застосунку (БД, ключі, прапорці) не розкидай
`os.getenv` по коду:

- **`pydantic-settings`** — типізовані налаштування з env/файлів, з валідацією
  (аналог `Codable`-конфігу). Один клас — джерело істини.
- **`python-dotenv`** — підтягнути `.env` у середовище для локальної розробки.

Деталі — [Модуль 04](../04-types-and-typing.md) (типи) та хаб
[Модуля 13](../13-stdlib-and-ecosystem.md) (екосистема). Секрети — ніколи в код,
завжди через середовище.

---

## Шпаргалка / рецепти

```python
import subprocess, shlex, os, sys

# запустити, дочекатися, перевірити, отримати вивід
r = subprocess.run(["git", "status"], capture_output=True, text=True, check=True)
r.stdout; r.returncode

# з таймаутом
subprocess.run(["slow-cmd"], timeout=30, check=True)

# подати stdin / своя робоча тека / додати env (не замінити!)
subprocess.run(["cat"], input="data\n", text=True)
subprocess.run(["make"], cwd="/path/to/proj", env={**os.environ, "CI": "1"})

# рядок-команда → безпечний список
subprocess.run(shlex.split('grep -r "TODO" .'))

# середовище та платформа
os.environ.get("API_URL", "http://localhost")   # з дефолтом, без KeyError
os.cpu_count()                                    # для пулів
sys.argv[1:]                                      # аргументи (без імені скрипта)
sys.exit(1)                                       # код виходу
sys.version_info >= (3, 12)                       # перевірка версії

# НЕ роби так:
subprocess.run(f"rm {x}", shell=True)             # ⚠️ command injection
```

## Див. також

- [Модуль 13 — Стандартна бібліотека та екосистема](../13-stdlib-and-ecosystem.md) — хаб, CLI (`Typer`), конфіги.
- [Файли та серіалізація](files-and-serialization.md) — `pathlib` замість `os.path`, читання/запис.
- [Модуль 12 — Асинхронність](../12-async.md) — `asyncio.create_subprocess_exec`, чому не блокувати цикл.
- [Тематичний індекс](../INDEX.md).
