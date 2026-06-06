# Модуль 12. Асинхронність

[← Курс](README.md) · [Тематичний індекс](INDEX.md) · **Модуль 12**

Цей модуль — про `asyncio` та `async/await`. Синтаксис майже ідентичний Swift
Concurrency, але **модель виконання кардинально інша**. Розуміння цих відмінностей
рятує від багатьох помилок.

## 1. Синтаксис: майже як у Swift

### Swift
```swift
func fetchUser(id: Int) async throws -> User {
    let data = try await network.get("/users/\(id)")
    return try decode(data)
}

let user = try await fetchUser(id: 1)
```

### Python
```python
async def fetch_user(user_id: int) -> User:
    data = await network.get(f"/users/{user_id}")
    return decode(data)

user = await fetch_user(1)        # лише всередині async-функції!
```

`async def` оголошує корутину, `await` призупиняє до завершення. Виглядає
знайомо. Але далі — відмінності.

## 2. ⚠️ Найбільша різниця: модель виконання

| | Swift Concurrency | Python asyncio |
|--|-------------------|----------------|
| Паралелізм | справжній (кілька потоків/ядер) | **немає** (один потік, GIL) |
| Конкурентність | так | так |
| Планувальник | runtime, work-stealing | один event loop |
| Захист стану | actors (компілятор) | немає вбудованого |
| CPU-bound користь | так | **ні** (не пришвидшить) |

### GIL — Global Interpreter Lock

CPython має **GIL**: у будь-який момент байткод Python виконує лише один потік.
Тому `asyncio` дає **конкурентність, але не паралелізм**. Це чудово для
I/O-bound задач (мережа, диск, БД — де потік усе одно чекає), але **не пришвидшує
CPU-bound** обчислення.

> **⚠️ Пастка №1.** Якщо прийшов зі Swift, де `async` + кілька ядер = реальний
> паралелізм — у Python це не так. `asyncio` корисний, коли програма **чекає на
> I/O**. Для CPU-важких задач він не допоможе; потрібні процеси (див. §7).
>
> *Примітка:* у Python 3.13 з'явився експериментальний «free-threaded» режим без
> GIL, але це поки не мейнстрім. Орієнтуйся на модель із GIL.

## 3. Запуск async-коду

`await` працює лише всередині `async def`. Точка входу в async-світ — `asyncio.run`:

```python
import asyncio

async def main() -> None:
    user = await fetch_user(1)
    print(user)

asyncio.run(main())            # створює event loop, виконує, закриває
```

> **⚠️ Пастка №2.** Не можна викликати `await` на верхньому рівні скрипта
> (поза `async def`). Усе починається з одного `asyncio.run(main())`. У Swift
> `@main` + `async main` робить це за тебе.

## 4. Конкурентне виконання — TaskGroup

Просто `await a(); await b()` — це **послідовно**. Для конкурентності:

### Swift
```swift
async let a = fetchA()
async let b = fetchB()
let (ra, rb) = try await (a, b)         // паралельно
```

або
```swift
try await withTaskGroup(of: Data.self) { group in
    for url in urls { group.addTask { try await fetch(url) } }
}
```

### Python — TaskGroup (3.11+, рекомендовано)
```python
async def fetch_all(urls: list[str]) -> list[bytes]:
    async with asyncio.TaskGroup() as tg:        # ~ withTaskGroup
        tasks = [tg.create_task(fetch(url)) for url in urls]
    return [t.result() for t in tasks]            # усі завершені після виходу з with
```

`TaskGroup` — структурована конкурентність: гарантує, що всі задачі завершаться
(або скасуються при помилці) до виходу з блоку. Це прямий аналог Swift
`withTaskGroup` і **рекомендований** сучасний підхід.

Старіший спосіб — `asyncio.gather` (досі поширений):

```python
results = await asyncio.gather(fetch(u1), fetch(u2), fetch(u3))

# не падати на першій помилці, а зібрати все (помилки повертаються як значення):
results = await asyncio.gather(*coros, return_exceptions=True)
# results: [<результат>, ValueError(...), <результат>, ...]
```

> **Best practice.** Для нового коду — `TaskGroup` (структуровано, коректно
> скасовує при помилках; кілька помилок → `ExceptionGroup`,
> [Модуль 10](10-errors-and-exceptions.md)). `gather` — коли треба зібрати
> результати й не проти ручного керування помилками (`return_exceptions=True`).

### `create_task`, `as_completed`, `wait`

```python
# create_task — запустити корутину «у фоні» вже зараз (не чекати)
task = asyncio.create_task(work())     # планується негайно
...                                     # робимо щось інше
result = await task                     # забрати результат пізніше

# as_completed — обробляти результати В ПОРЯДКУ ЗАВЕРШЕННЯ (не запуску)
for coro in asyncio.as_completed([f(3), f(1), f(2)]):
    print(await coro)                   # надрукує 1, 2, 3 — хто перший готовий

# wait — тонкий контроль (напр., зупинитись на першій помилці/завершенні)
done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
```

> **⚠️ Пастка «загублена задача».** `asyncio.create_task()` повертає `Task`, на
> який треба **тримати посилання**. Якщо результат не зберегти
> (`asyncio.create_task(work())` без присвоєння), GC може зібрати задачу до
> завершення — вона мовчки «зникне». Зберігай у змінній/множині, або
> використовуй `TaskGroup` (він тримає посилання сам).

`asyncio.ensure_future` — старіший родич `create_task`; у новому коді бери
`create_task` (для корутин) або `TaskGroup`.

## 5. Таймаути та скасування

```python
async with asyncio.timeout(5.0):         # 3.11+  ~ Task.withTimeout
    await slow_operation()
# піднесе TimeoutError, якщо не вклалося в 5с
```

Скасування — через `CancelledError` (як Swift `Task.cancel()` + `checkCancellation`):

```python
task = asyncio.create_task(work())
task.cancel()                            # запит на скасування
try:
    await task
except asyncio.CancelledError:
    ...
```

> **⚠️ Пастка №3.** `asyncio.CancelledError` (3.8+) успадковує від `BaseException`,
> **не** `Exception`. Тому `except Exception:` його **не** зловить — і це
> навмисно: не можна випадково «проковтнути» скасування. Якщо ловиш — перекидай далі.

## 6. ⚠️ Не блокуй event loop

Один event loop означає: будь-який **синхронний блокуючий виклик** заморожує всю
програму. Це найпідступніша пастка.

```python
async def bad() -> None:
    time.sleep(5)             # ❌ БЛОКУЄ весь loop на 5с — нічого інше не виконається
    requests.get(url)         # ❌ синхронний HTTP теж блокує

async def good() -> None:
    await asyncio.sleep(5)    # ✅ віддає керування loop
    await client.get(url)     # ✅ async HTTP (httpx)
```

Якщо мусиш викликати синхронний/CPU-важкий код — винеси в окремий потік/процес:

```python
result = await asyncio.to_thread(blocking_function, arg)    # 3.9+, у потік
```

> **Best practice.** В async-функції використовуй лише async-бібліотеки
> (`httpx`, `asyncpg`, `aiofiles`). Один синхронний блокуючий виклик зводить
> нанівець усю асинхронність. У Swift така помилка менш катастрофічна; тут —
> критична.

## 6b. Примітиви синхронізації

Навіть без паралелізму конкурентні задачі ділять стан і потребують координації.
`asyncio` має async-версії звичних примітивів (await-ні, не блокуючі):

```python
import asyncio

lock = asyncio.Lock()
async with lock:                 # критична секція — лише одна задача всередині
    shared_state.append(x)

sem = asyncio.Semaphore(10)      # обмежити конкурентність (напр., ≤10 запитів разом)
async with sem:
    await fetch(url)

event = asyncio.Event()          # сигнал між задачами
await event.wait()               # чекати, поки інша задача викличе event.set()
```

> **Best practice.** `Semaphore` — найкорисніший: ним обмежують кількість
> одночасних з'єднань/запитів (rate limiting), щоб не «задушити» сервіс тисячами
> паралельних корутин.

### `asyncio.Queue` — патерн producer/consumer

Черга — найчистіший спосіб розподілити роботу між кількома воркерами:

```python
async def worker(q: asyncio.Queue, out: list) -> None:
    while True:
        item = await q.get()
        try:
            out.append(item * 2)         # обробка
        finally:
            q.task_done()                # позначити елемент завершеним

async def main() -> None:
    q: asyncio.Queue[int] = asyncio.Queue()
    workers = [asyncio.create_task(worker(q, out := [])) for _ in range(3)]
    for x in range(10):
        await q.put(x)
    await q.join()                       # чекати, поки всі елементи оброблено
    for w in workers:
        w.cancel()                       # зупинити воркерів
```

> `asyncio.Lock`/`Queue` — **не** те саме, що `threading.Lock`/`queue.Queue`: ці
> async-версії не блокують потік, а віддають керування event loop. Не змішуй.

## 7. Справжній паралелізм — процеси й потоки

Оскільки GIL блокує паралелізм у межах процесу:

```python
# CPU-bound → процеси (обходять GIL, але є оверхед серіалізації)
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor() as pool:
    results = list(pool.map(heavy_cpu_task, items))

# I/O-bound без async-бібліотек → потоки
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as pool:
    results = list(pool.map(blocking_io_task, items))
```

| Задача | Інструмент |
|--------|-----------|
| I/O-bound, є async-бібліотеки | `asyncio` |
| I/O-bound, лише синхронні бібліотеки | `ThreadPoolExecutor` / `asyncio.to_thread` |
| CPU-bound | `ProcessPoolExecutor` / `multiprocessing` |

## 8. Async-ітератори та контекст-менеджери

Прямі аналоги Swift `AsyncSequence` і async-ресурсів:

```python
from collections.abc import AsyncIterator

async def stream_lines(url: str) -> AsyncIterator[str]:
    async with client.stream("GET", url) as resp:    # async context manager
        async for line in resp.aiter_lines():          # async for ~ for await in
            yield line

async for line in stream_lines(url):
    print(line)
```

```swift
for try await line in url.lines { print(line) }   // Swift-аналог
```

## 9. Debug-режим і free-threading

### Налагодження async

```bash
PYTHONASYNCIODEBUG=1 uv run python app.py     # або asyncio.run(main(), debug=True)
```

Debug-режим попереджає про класичні помилки: корутину забули `await`, задачу
кинули незавершеною, колбек виконувався надто довго (блокував loop). Вмикай при
загадковій поведінці.

> **⚠️ Пастка.** «Coroutine was never awaited» — найчастіше попередження: ти
> викликав `async def`, але забув `await`. Виклик корутини **нічого не виконує** —
> лише створює об'єкт-корутину; робота починається з `await`/`create_task`.

### Free-threading (3.13+)

Python 3.13 ввів експериментальний **free-threaded** білд (без GIL,
[PEP 703](https://peps.python.org/pep-0703/)) — у ньому потоки виконують байткод
*справді паралельно*, як у Swift. Це поки експеримент (окремий білд, не дефолт,
частина C-розширень несумісна). Орієнтуйся на модель із GIL, але знай: напрям
руху — до справжнього паралелізму потоків.

## Інструменти та бібліотеки

- **`asyncio`** (stdlib) — основа: event loop, `TaskGroup`, `timeout`, `to_thread`,
  `Queue`, `Lock`, `Semaphore`, `Event`.
- **`httpx`** — async (і sync) HTTP-клієнт. Сучасна заміна `requests` для async.
- **`aiofiles`** — async файлові операції.
- **`asyncpg`** / **`psycopg`** (async) — async-драйвери PostgreSQL.
- **`anyio`** — абстракція над asyncio й trio; структурована конкурентність,
  ближча за духом до Swift. Її використовує FastAPI.
- **`uvloop`** — швидша заміна стандартного event loop (на базі libuv).
- **`concurrent.futures`** (stdlib) — пули потоків/процесів для паралелізму.

## Best practices модуля

- `async`/`await` синтаксично як у Swift, але це **конкурентність без
  паралелізму** (GIL). Корисно для I/O, не для CPU.
- Усе починається з одного `asyncio.run(main())`.
- Конкурентність — через `TaskGroup` (структуровано), не послідовні `await`.
- **Ніколи** не викликай блокуючий синхронний код у loop; виноси в `to_thread`.
- В async-коді — лише async-бібліотеки (`httpx`, не `requests`).
- CPU-bound — у `ProcessPoolExecutor`, а не `asyncio`.
- `CancelledError` не лови випадково (`except Exception` його не ловить — і добре).
- Тримай посилання на `create_task`; `Semaphore` для обмеження конкурентності.
- Не плутай `asyncio.Queue`/`Lock` із `threading`/`queue` версіями.

## Див. також

- [Модуль 00 — Ментальна модель](00-tooling-and-mental-model.md) — GIL, реалізації, free-threading.
- [Модуль 09 — Ітератори](09-iterators-and-generators.md) — `async`-генератори, `async for`.
- [Модуль 10 — Помилки](10-errors-and-exceptions.md) — `ExceptionGroup`/`except*`, `CancelledError`.
- [Модуль 13 — Stdlib](13-stdlib-and-ecosystem.md) — `httpx`, `anyio`, `concurrent.futures`, `multiprocessing`.
- [Тематичний індекс](INDEX.md).

**Далі:** [Модуль 13 — Стандартна бібліотека та екосистема](13-stdlib-and-ecosystem.md)
