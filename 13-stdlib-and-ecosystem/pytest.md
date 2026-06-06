# Тестування (pytest)

[← Курс](../README.md) · [Модуль 13](../13-stdlib-and-ecosystem.md) · **Тестування (pytest)**

У Swift ти пишеш тести як методи класу-нащадка `XCTestCase` з `XCTAssert*`, або
вже на `swift-testing` з макросом `#expect`. У Python стандарт де-факто —
**`pytest`**: ані класу, ані спеціальних assert-функцій. Звичайна функція + голий
`assert`. Pytest переписує `assert` під капотом і дає багате повідомлення про
помилку — те, заради чого у XCTest існує ціле сімейство `XCTAssertEqual`/
`XCTAssertTrue`/….

> **Best practice.** У stdlib є `unittest` (порт JUnit, з класами й `setUp`), але
> в нових проєктах беруть `pytest` — менше церемоній, потужні фікстури й
> параметризація. `pytest` уміє запускати й `unittest`-тести, тож міграція м'яка.

Встановлення (Модуль 00): `uv add --dev pytest`, запуск: `uv run pytest`.

---

## 1. Перший тест: функція + `assert`

```python
# test_math.py
def square(n: int) -> int:
    return n * n

def test_square() -> None:        # ім'я починається з test_
    assert square(4) == 16        # звичайний assert, не XCTAssertEqual
```

Для порівняння — той самий тест у Swift:

```swift
// XCTest
func testSquare() { XCTAssertEqual(square(4), 16) }
// swift-testing
@Test func square() { #expect(square(4) == 16) }
```

**Автовиявлення (test discovery).** Pytest сам знаходить тести за угодами:

| Що | Угода |
|----|-------|
| Файли | `test_*.py` або `*_test.py` |
| Функції | `test_*` |
| Класи (опційно) | `Test*` (без `__init__`) |

Класи не потрібні — групуй тести функціями у файлі. Клас лише як необов'язковий
контейнер для логічно пов'язаних тестів.

### Багате повідомлення про помилку

Pytest показує фактичні значення без жодних `XCTAssertEqual`:

```python
def test_square_fail() -> None:
    assert square(3) == 10
```

```text
# $ uv run pytest t/test_basics.py
# t/test_basics.py:10: AssertionError
# >       assert square(3) == 10
# E       assert 9 == 10
# E        +  where 9 = square(3)
# =========== 1 failed, 1 passed in 0.01s ===========
```

> **⚠️ Пастка.** Це працює лише для assert у тестових файлах (їх pytest
> інструментує під час імпорту). Голий `assert` усередині продакшен-коду
> вимикається прапорцем `python -O` — не покладайся на нього для валідації
> (Модуль 10), лише для тестів.

---

## 2. Запуск

```bash
uv run pytest                       # усі тести у проєкті
uv run pytest -v                    # verbose: рядок на кожен тест
uv run pytest -q                    # тихо: лише крапки/підсумок
uv run pytest -x                    # стоп на першій помилці
uv run pytest -k "raises and not slow"   # за виразом по іменах
uv run pytest t/test_features.py    # один файл
uv run pytest t/test_features.py::test_approx          # один тест
uv run pytest t/test_features.py::TestGroup::test_x    # тест у класі
```

`-v` друкує статуси по одному:

```text
# t/test_features.py::test_raises PASSED                  [ 11%]
# t/test_features.py::test_parse_port[http] PASSED        [ 66%]
# t/test_features.py::test_skipped SKIPPED (...)          [ 88%]
# t/test_features.py::test_xfailing XFAIL (known bug)     [100%]
```

`-x` зупиняється відразу:

```text
# FAILED t/test_basics.py::test_square_fail - assert 9 == 10
# !!!!!!!!!! stopping after 1 failures !!!!!!!!!!
# 1 failed, 1 passed in 0.02s
```

---

## 3. Винятки: `pytest.raises`

Аналог `XCTAssertThrowsError` / `#expect(throws:)`. Тіло `with` має кинути
очікуваний виняток (Модуль 10), інакше тест провалиться.

```python
import pytest

def parse_port(s: str) -> int:
    n = int(s)
    if not (0 <= n <= 65535):
        raise ValueError(f"port out of range: {n}")
    return n

def test_raises() -> None:
    with pytest.raises(ValueError):
        parse_port("99999")

def test_raises_match() -> None:                 # match= — regex по тексту
    with pytest.raises(ValueError, match="out of range"):
        parse_port("99999")

def test_raises_attrs() -> None:                 # доступ до самого винятку
    with pytest.raises(ValueError) as exc_info:
        parse_port("99999")
    assert "99999" in str(exc_info.value)        # перевірка атрибутів/тексту
```

```text
# t/test_features.py::test_raises PASSED
# t/test_features.py::test_raises_match PASSED
# t/test_features.py::test_raises_attrs PASSED
```

> **⚠️ Пастка.** `match=` — це **регулярний вираз** (через `re.search`), а не
> підрядок. Спецсимволи (`(`, `.`, `$`, `[`) треба екранувати або обгортати в
> `re.escape(...)`, інакше `re.error` чи хибна відповідність.

---

## 4. Числа з плаваючою комою: `pytest.approx`

`0.1 + 0.2 != 0.3` (бінарне представлення). Як `XCTAssertEqual(_, accuracy:)`:

```python
def test_approx() -> None:
    assert 0.1 + 0.2 == pytest.approx(0.3)
    assert [0.1 + 0.2, 1.0] == pytest.approx([0.3, 1.0])   # і для колекцій
    # точність: pytest.approx(0.3, abs=1e-6) / rel=1e-3
```

---

## 5. Параметризація: `@pytest.mark.parametrize`

Головний DRY-виграш проти XCTest. Замість циклу в одному тесті (де перша
помилка ховає решту) — **табличні** тести: один рядок таблиці = один окремий
тест зі своїм статусом.

```python
@pytest.mark.parametrize(
    "value, expected",
    [
        ("0", 0),
        ("80", 80),
        ("65535", 65535),
    ],
    ids=["zero", "http", "max"],          # читабельні імена в репорті
)
def test_parse_port(value: str, expected: int) -> None:
    assert parse_port(value) == expected
```

```text
# t/test_features.py::test_parse_port[zero] PASSED   [ 55%]
# t/test_features.py::test_parse_port[http] PASSED   [ 66%]
# t/test_features.py::test_parse_port[max] PASSED    [ 77%]
```

Без `ids=` pytest сам згенерує мітки (`[0-0]`, `[80-80]`…). Можна
складати декоратори (декартів добуток наборів) — але не зловживай.

> **Best practice.** `parametrize` замість `for`-циклу всередині тесту: кожен
> випадок видно окремо, помилка одного не приховує інших, а `pytest -k max`
> запустить лише потрібний.

---

## 6. Фікстури: `@pytest.fixture`

Фікстура — це залежність, яку pytest **інжектить за іменем параметра**. Замість
`setUp`/`tearDown` у класі — окремі іменовані фікстури, які беруть лише ті тести,
що їх просять.

```python
import pytest

@pytest.fixture
def sample_user() -> dict[str, object]:
    return {"name": "Alice", "age": 30}

def test_uses_fixture(sample_user: dict) -> None:   # ім'я параметра == ім'я фікстури
    assert sample_user["name"] == "Alice"
```

### `yield`-фікстури: setup/teardown

Те, що до `yield`, — підготовка; що після — прибирання (гарантовано, навіть якщо
тест упав). Це той самий патерн, що й контекст-менеджери з Модуля 10.

```python
@pytest.fixture(scope="module")           # один екземпляр на весь файл
def db_connection():
    print("[setup] open connection")
    conn = {"open": True}
    yield conn                            # ← віддаємо тестам
    print("[teardown] close connection")  # ← після останнього тесту scope
    conn["open"] = False
```

```text
# t/test_fixtures.py::test_module_fixture
# [setup] open connection           ← один раз на модуль
# PASSED
# [teardown] close connection       ← після всіх тестів модуля
# 5 passed in 0.02s
```

**Scope** керує тим, як часто фікстура перестворюється:

| `scope=` | Живе |
|----------|------|
| `"function"` (типово) | окремо для кожного тесту |
| `"class"` | на клас |
| `"module"` | на файл |
| `"session"` | один раз на весь запуск pytest |

> **⚠️ Пастка.** Ширший scope = спільний стан між тестами. Якщо тест мутує
> `module`/`session`-фікстуру, наступні тести побачать зміни — і порядок запуску
> почне впливати на результат. Для змінного стану лишай `function` scope.

### `conftest.py` — спільні фікстури

Фікстури в `conftest.py` автоматично доступні всім тестам у тій теці й нижче — без
імпортів. Туди виносять усе спільне (з'єднання з БД, тестовий клієнт API тощо).

### Вбудовані фікстури

Pytest дає готові фікстури — просто додай як параметр:

```python
import os

def test_tmp_path(tmp_path) -> None:            # унікальна тимчасова тека (pathlib.Path)
    f = tmp_path / "data.txt"
    f.write_text("hello")
    assert f.read_text() == "hello"

def test_capsys(capsys) -> None:                # перехоплення stdout/stderr
    print("Hello, Bob!")
    assert capsys.readouterr().out == "Hello, Bob!\n"

def test_monkeypatch(monkeypatch) -> None:      # тимчасові патчі (відкат автоматичний)
    monkeypatch.setenv("APP_ENV", "test")
    assert os.environ["APP_ENV"] == "test"
```

```text
# t/test_fixtures.py::test_tmp_path PASSED
# t/test_fixtures.py::test_capsys PASSED
# t/test_fixtures.py::test_monkeypatch PASSED
```

---

## 7. Патчинг: `monkeypatch` і `unittest.mock`

`monkeypatch` тимчасово підміняє атрибути/env/cwd і **сам усе відкочує** після
тесту — без ручного teardown:

```python
def test_patch_attr(monkeypatch) -> None:
    monkeypatch.setattr("mymod.now", lambda: "2026-01-01")   # підміна функції
    monkeypatch.setenv("API_KEY", "fake")
    monkeypatch.delenv("HOME", raising=False)
```

Для повноцінних моків (call count, `assert_called_with`, side effects) — stdlib
`unittest.mock`:

```python
from unittest.mock import Mock, patch

def test_mock() -> None:
    client = Mock()
    client.get.return_value = {"id": 1}
    assert client.get("/x") == {"id": 1}
    client.get.assert_called_once_with("/x")

@patch("mymod.httpx.get")                  # декоратор-патч на час тесту
def test_patched(mock_get) -> None:
    mock_get.return_value.json.return_value = {"ok": True}
    ...
```

> **Best practice.** Патч `monkeypatch`/`patch` цілься у місце **використання**, а
> не оголошення: патч `mymod.httpx.get`, бо саме `mymod` викликає `get`. Це
> класична пастка «patch where it's looked up».

---

## 8. Маркери: skip / skipif / xfail

```python
@pytest.mark.skip(reason="not implemented yet")
def test_skipped() -> None: ...

@pytest.mark.skipif(sys.platform == "win32", reason="POSIX only")
def test_posix() -> None: ...

@pytest.mark.xfail(reason="known bug")      # очікуємо провал; пройде → XPASS
def test_xfailing() -> None:
    assert parse_port("-1") == -1
```

```text
# t/test_features.py::test_skipped  SKIPPED (not implemented yet)
# t/test_features.py::test_xfailing XFAIL (known bug)
# 6 passed, 1 skipped, 1 xfailed in 0.02s
```

`xfail` (на відміну від `skip`) усе одно запускає тест: якщо він раптом
**проходить**, це видно як `XPASS` — сигнал «баг полагоджено, прибери маркер».

---

## 9. Best practices

- **Arrange–Act–Assert**: підготуй дані → виклич → перевір. Три візуальні блоки.
- **Один логічний фокус на тест**: одна перевірена поведінка (assert-ів може бути
  кілька, але про одне). Ім'я тесту описує сценарій.
- **Фікстури замість `setUp`**: інжекція за параметром явніша й композується.
- **`parametrize` замість циклів**: окремий статус на випадок (див. §5).
- **`pytest-cov`** — покриття: `uv add --dev pytest-cov`, `uv run pytest --cov=mypkg`.
- **`hypothesis`** — property-based тести: описуєш властивість, бібліотека генерує
  й мінімізує контрприклади (Модуль 13, аналог SwiftCheck).

---

## Шпаргалка / рецепти

```python
def test_x() -> None: assert f() == expected      # голий assert, без класу
with pytest.raises(ValueError, match="regex"): ... # очікуваний виняток
assert got == pytest.approx(0.3, rel=1e-3)         # порівняння float

@pytest.mark.parametrize("a, b", [(1, 2), (3, 4)], ids=["lo", "hi"])  # табличні

@pytest.fixture                                    # function-scope залежність
def conn(): yield make()                           # setup / teardown через yield
@pytest.fixture(scope="session") ...               # на весь запуск

def test_io(tmp_path, capsys, monkeypatch): ...    # вбудовані фікстури
@pytest.mark.skipif(cond, reason="..."); @pytest.mark.xfail
```

```bash
uv run pytest -v                  # докладно
uv run pytest -x                  # стоп на першій помилці
uv run pytest -k "name expr"      # фільтр за іменем
uv run pytest path::test_name     # один тест
uv run pytest --cov=mypkg         # покриття (pytest-cov)
```

## Див. також

- [Модуль 13 — Стандартна бібліотека та екосистема](../13-stdlib-and-ecosystem.md) — місце pytest в екосистемі, `hypothesis`, `coverage`.
- [Модуль 10 — Помилки й винятки](../10-errors-and-exceptions.md) — `raise`, контекст-менеджери (`with`/`yield`).
- [Модуль 00 — Інструментарій](../00-tooling-and-mental-model.md) — `uv add --dev`, запуск інструментів через `uv run`.
- [Тематичний індекс](../INDEX.md).
