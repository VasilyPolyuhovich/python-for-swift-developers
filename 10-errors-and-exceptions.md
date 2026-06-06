# Модуль 10. Помилки та винятки

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 10**

Туторіал: [§8 Помилки та винятки](https://docs.python.org/uk/3/tutorial/errors.html).

Обробка помилок — велика різниця зі Swift. Swift використовує *типізовані*
помилки з явним `throws` у сигнатурі та `try` на місці виклику. Python використовує
**нетипізовані винятки**, які поширюються неявно (як у більшості мов із
exceptions). Це вимагає іншої дисципліни.

## 1. Базова модель

### Swift
```swift
enum NetworkError: Error { case timeout, notFound }

func fetch() throws -> Data {           // throws у сигнатурі
    throw NetworkError.timeout
}

do {
    let data = try fetch()              // try на місці виклику ОБОВ'ЯЗКОВИЙ
} catch NetworkError.timeout {
    ...
} catch {
    ...
}
```

### Python
```python
class NetworkError(Exception): ...
class TimeoutError(NetworkError): ...

def fetch() -> bytes:                   # НЕ видно з сигнатури, що кидає!
    raise TimeoutError("took too long")

try:
    data = fetch()                      # БЕЗ try-маркера на виклику
except TimeoutError:
    ...
except NetworkError:
    ...
```

> **⚠️ Пастка №1 (найважливіша).** У Python **сигнатура функції НЕ показує**, які
> винятки вона кидає. Немає `throws`, немає `try` на місці виклику. Будь-який
> рядок може кинути будь-що, і це поширюється вгору неявно. Це втрата
> compile-time гарантій, до яких ти звик у Swift.
>
> Компенсація: документуй винятки в docstring (`Raises:`), і для очікуваних
> помилок керування потоком розглядай патерн `Result` (див. §7).

## 2. try / except / else / finally

```python
try:
    risky()
except ValueError as e:              # конкретний тип + доступ до об'єкта
    print(f"bad value: {e}")
except (KeyError, IndexError) as e:  # кілька типів разом
    print(f"lookup failed: {e}")
except Exception as e:               # загальний (як `catch` без патерна)
    print(f"unexpected: {e}")
else:
    print("ran if NO exception")     # виконається, якщо try пройшов без помилки
finally:
    cleanup()                        # завжди (як defer, але блок)
```

- `except X as e` — спіймати тип `X`, прив'язати об'єкт до `e`.
- `else` — виконується лише якщо винятку не було (рідко, але корисно).
- `finally` — завжди, аналог `defer`/гарантованого очищення.

> **⚠️ Пастка №2.** Не пиши «голий» `except:` (без типу) — він ловить *усе*,
> включно з `KeyboardInterrupt` і `SystemExit`. Якщо треба зловити «майже все» —
> `except Exception:`. `ruff` (E722) попередить про голий except.

### Bare `raise` — повторне підняття

`raise` без аргументу всередині `except` піднімає **той самий** виняток далі,
зберігаючи оригінальний трейсбек — типовий патерн «залогувати й пропустити вгору»:

```python
try:
    risky()
except ValueError:
    logger.exception("failed during risky()")   # залогували з трейсбеком
    raise                                        # ← пропускаємо той самий виняток вище
```

> **⚠️ Пастка.** `raise e` (з іменем) теж працює, але «обрізає» частину
> трейсбеку. Для чистого повторного підняття пиши голий `raise`.

## 3. Ієрархія винятків

Усі винятки успадковують від `BaseException`; майже всі — від `Exception`.

```
BaseException
├── SystemExit, KeyboardInterrupt   ← НЕ лови випадково
└── Exception                       ← лови це
    ├── ValueError, TypeError, KeyError, IndexError
    ├── OSError (FileNotFoundError, PermissionError, ...)
    ├── RuntimeError
    └── ... твої власні
```

> **Best practice.** Лови **найконкретніший** тип, який можеш обробити. Не лови
> те, що не вмієш обробити — хай поширюється. Ловити `Exception` — лише на межах
> (top-level handler, логування, межа запиту в сервері).

## 4. Створення власних винятків

```python
class AppError(Exception):
    """Базовий виняток застосунку."""

class ValidationError(AppError):
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(f"{field}: {message}")

raise ValidationError("email", "invalid format")
```

> **Best practice.** Створи один базовий виняток застосунку (`AppError`) і успадковуй
> від нього. Тоді споживачі можуть зловити всі твої помилки одним `except AppError`.
> Це аналог одного `enum MyError: Error` зі Swift.

## 5. Exception chaining — збереження причини

```python
try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    raise ConfigError("invalid config") from e    # зберігає першопричину
```

`raise ... from e` зв'язує новий виняток із оригінальним (видно в трейсбеку як
«The above exception was the direct cause...»). Аналог обгортання помилок.

## 6. Context managers — `with` (аналог defer + RAII)

Найкращий механізм керування ресурсами. Гарантує очищення навіть при винятку —
як `defer`, але прив'язаний до ресурсу.

```python
with open("data.txt") as f:          # __enter__ при вході
    content = f.read()
# файл ГАРАНТОВАНО закрито тут — __exit__, навіть якщо була помилка
```

Кілька ресурсів:

```python
with open("in.txt") as src, open("out.txt", "w") as dst:
    dst.write(src.read())
```

Власний context manager — найпростіше через `contextlib`:

```python
from contextlib import contextmanager
from collections.abc import Iterator
import time

@contextmanager
def timer(label: str) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield                         # тут виконується тіло with-блоку
    finally:
        print(f"{label}: {time.perf_counter() - start:.3f}s")

with timer("processing"):
    heavy_work()
```

Класова форма (через dunder-методи):

```python
class Transaction:
    def __enter__(self) -> "Transaction":
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()           # відкат при винятку
        return False                  # False = не глушити виняток
```

> **Best practice.** Будь-який ресурс (файл, з'єднання, лок, транзакція) бери
> через `with`. Це Pythonic-еквівалент `defer`/RAII і гарантує очищення.

### `ExitStack` — динамічна кількість ресурсів

Коли кількість ресурсів невідома наперед (відкрити N файлів зі списку),
`contextlib.ExitStack` керує ними динамічно — усі закриються у зворотному порядку:

```python
from contextlib import ExitStack

with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]
    # усі файли відкриті; вийдемо — усі закриються (LIFO), навіть при винятку
    process(files)
```

> Семантика `__exit__`: поверни `True`, щоб **проковтнути** виняток, `False`
> (або нічого) — щоб пропустити далі. `@contextmanager` робить це через
> `try/except` навколо `yield` ([Модуль 09](09-iterators-and-generators.md)).

## 7. Result-патерн — типізовані помилки (опціонально)

Якщо тобі бракує типізованих помилок зі Swift (`Result<T, Error>`), для
*очікуваних* помилок (керування потоком, а не виняткових ситуацій) можна явно
повертати результат:

```python
@dataclass(frozen=True)
class Ok[T]:
    value: T

@dataclass(frozen=True)
class Err[E]:
    error: E

type Result[T, E] = Ok[T] | Err[E]

def parse_age(raw: str) -> Result[int, str]:
    if not raw.isdigit():
        return Err("not a number")
    return Ok(int(raw))

match parse_age("40"):
    case Ok(value=age):
        print(age)
    case Err(error=msg):
        print(msg)
```

> **Коли що.** Винятки — для *виняткових* ситуацій (баги, недоступні ресурси).
> `Result`/значення-повернення — для *очікуваних* помилок як частини логіки
> (валідація вводу, парсинг). Це та сама межа, що й у Swift між `throws` і
> поверненням `Optional`/`Result`. Готова бібліотека — `returns` (нижче).

## 7b. Exception groups — `except*` (3.11+)

Коли операція може породити **кілька** помилок одночасно (паралельні задачі —
[Модуль 12](12-async.md)), їх збирають у `ExceptionGroup` і обробляють новим
синтаксисом `except*` (кожен `except*` ловить *свою підмножину*):

```python
def run_all():
    raise ExceptionGroup("multiple failures", [ValueError("a"), TypeError("b")])

try:
    run_all()
except* ValueError as eg:
    print("ValueErrors:", [str(e) for e in eg.exceptions])
except* TypeError as eg:
    print("TypeErrors:", [str(e) for e in eg.exceptions])
```

Це основа обробки помилок у `asyncio.TaskGroup` ([Модуль 12](12-async.md)) — якщо
кілька задач впали, отримаєш `ExceptionGroup` з усіма.

## 7c. `assert` — перевірки інваріантів (не валідація!)

```python
def withdraw(balance: int, amount: int) -> int:
    assert amount > 0, "amount must be positive"   # інваріант розробника
    return balance - amount
```

> **⚠️ Пастка.** `assert` **вимикається** прапором `python -O` (оптимізація). Тому
> `assert` — лише для перевірки інваріантів/багів під час розробки, **ніколи** для
> валідації вводу чи безпеки (інакше в проді перевірки зникнуть). Для валідації —
> явний `if ... raise` або `pydantic` ([Модуль 04](04-types-and-typing.md)).

## 8. EAFP vs LBYL — філософія Python

Python заохочує **EAFP** (Easier to Ask Forgiveness than Permission) — спробуй і
лови, замість перевіряти заздалегідь:

```python
# EAFP — Pythonic
try:
    value = config["key"]
except KeyError:
    value = default

# LBYL — менш Pythonic (і має гонку станів)
if "key" in config:
    value = config["key"]
else:
    value = default
```

Це відрізняється від оборонного стилю, типового для Swift (де `guard`/`if let`
заохочують LBYL). У Python винятки дешеві й ідіоматичні для цього.

## Інструменти та бібліотеки

- **`contextlib`** (stdlib) — `@contextmanager`, `suppress`, `ExitStack`,
  `closing`. `suppress` — елегантне ігнорування:
  ```python
  from contextlib import suppress
  with suppress(FileNotFoundError):
      os.remove("maybe.txt")
  ```
- **`logging`** (stdlib) — логуй винятки з трейсбеком: `logger.exception("msg")`.
- **`traceback`** (stdlib) — програмний доступ до трейсбеку:
  `traceback.format_exc()` повертає рядок із повним стеком (для логів/звітів).
- **`warnings`** (stdlib) — попередження без зупинки програми
  (`warnings.warn("deprecated", DeprecationWarning)`); керується фільтрами,
  на відміну від винятків.
- **`returns`** (PyPI) — повноцінні `Result`/`Maybe`/`IO` монади, якщо хочеш
  функціональний стиль обробки помилок ближче до Swift `Result`.
- **`tenacity`** (PyPI) — ретраї з backoff для збійних операцій.

## Best practices модуля

- Лови найконкретніший тип; не глуши те, що не вмієш обробити.
- Ніколи не «голий» `except:`; на межах — `except Exception:`.
- Один базовий `AppError` для свого застосунку.
- `raise ... from e` для збереження причини.
- Ресурси — через `with` (Pythonic `defer`/RAII).
- Документуй винятки в docstring (`Raises:`), бо сигнатура їх не показує.
- EAFP (try/except) ідіоматичніший за оборонні перевірки.
- Для очікуваних помилок керування потоком — розглянь `Result`-патерн.
- `raise` (голий) для повторного підняття; `assert` лише для інваріантів, не валідації.
- `ExitStack` для динамічних ресурсів; `except*` для груп помилок.

## Див. також

- [Модуль 06 — Value-типи](06-structs-and-value-types.md) — `Result` через ADT, `assert_never`.
- [Модуль 09 — Ітератори](09-iterators-and-generators.md) — `@contextmanager` на генераторах.
- [Модуль 12 — Async](12-async.md) — `TaskGroup`, `ExceptionGroup`, `CancelledError`.
- [Модуль 03 · Конвертації](03-data-structures/conversions.md) — EAFP при парсингу.
- [Модуль 13 — Stdlib](13-stdlib-and-ecosystem.md) — `logging`, `contextlib`, `tenacity`.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 11 — Модулі, пакети, проєкти](11-modules-and-packages.md)
