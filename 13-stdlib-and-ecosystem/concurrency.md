[← Курс](../README.md) · [Модуль 13](../13-stdlib-and-ecosystem.md) · **Паралелізм (threads/processes)**

[Модуль 12](../12-async.md) показав `asyncio` — конкурентність для I/O. Ця сторінка —
про **справжній паралелізм** засобами stdlib: пули потоків і процесів для
блокуючої та CPU-важкої роботи. Якщо `asyncio` — це Swift `Task`/`async`, то тут
ми ближче до `DispatchQueue`/GCD та фонових черг.

## 1. Який інструмент під яку задачу

Три механізми конкурентності в Python — і вони **не взаємозамінні**:

| Задача | Інструмент | Чому |
|--------|-----------|------|
| I/O-bound, є async-бібліотеки (`httpx`, `asyncpg`) | `asyncio` ([Модуль 12](../12-async.md)) | один потік, без оверхеду |
| I/O-bound, лише **синхронні** бібліотеки (`requests`, драйвер БД) | `ThreadPoolExecutor` | потік чекає на I/O — GIL відпускається |
| **CPU-bound** (обчислення, парсинг, стиснення) | `ProcessPoolExecutor` | окремі процеси обходять GIL |

Ключове рішення зводиться до двох питань: *I/O чи CPU?* і *є async-версія
бібліотеки чи лише синхронна?* Деталі цієї таблиці — у
[Модулі 12, §7](../12-async.md).

```swift
// Swift: GCD/DispatchQueue для фонової роботи
DispatchQueue.global(qos: .userInitiated).async {
    let result = heavyWork()           // справжній паралелізм на iOS
    DispatchQueue.main.async { update(result) }
}
```

У Swift будь-яка фонова черга дає реальний паралелізм. У Python — лише процеси
(або потоки для I/O). Причина — GIL.

## 2. GIL: чому потоки не пришвидшують обчислення

CPython має **GIL** (Global Interpreter Lock): у будь-який момент байткод Python
виконує лише один потік (огляд — [Модуль 00](../00-tooling-and-mental-model.md),
[Модуль 12, §2](../12-async.md)). Наслідки:

- **CPU-bound** чистий Python: потоки **не** пришвидшують — вони по черзі тримають
  GIL. Потрібні **процеси**.
- **I/O-bound**: під час блокуючого виклику (`socket.recv`, `time.sleep`, читання
  файлу) потік **відпускає GIL**, тож інші потоки працюють. Тут потоки корисні.

> **⚠️ Пастка.** Прийшов зі Swift, де `DispatchQueue.concurrentPerform` чи
> кілька `Task` завантажують усі ядра? У Python `ThreadPoolExecutor` на
> CPU-важкій задачі дасть **нуль** прискорення (а часто й сповільнення через
> перемикання). Для обчислень — `ProcessPoolExecutor`.

> *Примітка:* у 3.13+ є експериментальний free-threaded білд без GIL
> ([Модуль 12, §9](../12-async.md)). Тут орієнтуємось на стандартний білд із GIL.

## 3. ThreadPoolExecutor — пул потоків для блокуючого I/O

`concurrent.futures` — високорівневий API над потоками й процесами. Майже завжди
бери його замість сирих `Thread`/`Process`.

```python
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def blocking_io(n: int) -> int:
    time.sleep(0.1)            # імітує мережу/диск — потік відпускає GIL
    return n * 2


with ThreadPoolExecutor(max_workers=4) as pool:       # with → коректний shutdown
    # submit → Future (запланувати один виклик)
    fut = pool.submit(blocking_io, 21)
    print("result:", fut.result())                    # result: 42

    # map → результати В ПОРЯДКУ АРГУМЕНТІВ (як list(map(...)), але паралельно)
    print("map:", list(pool.map(blocking_io, [1, 2, 3])))   # map: [2, 4, 6]

    # as_completed → у порядку ЗАВЕРШЕННЯ
    futures = [pool.submit(blocking_io, i) for i in range(4)]
    done = [f.result() for f in as_completed(futures)]
    print("as_completed sorted:", sorted(done))        # [0, 2, 4, 6]
# вихід із with → pool.shutdown(wait=True): чекає на всі задачі
```

`with`-блок гарантує `shutdown(wait=True)` — пул дочекається всіх задач і
звільнить потоки. Не керуй пулом вручну без потреби.

> **Best practice.** `with ThreadPoolExecutor() as pool:` — стандарт. `submit`
> коли треба окремі `Future` (з таймаутами/винятками); `map` — коли просто
> «застосуй функцію до списку паралельно й збери в порядку».

## 4. Future — результат, що ще не готовий

`submit` повертає `Future` — аналог Swift `Task` як значення-«обіцянки»:

```python
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FTimeout


def slow() -> str:
    time.sleep(0.5)
    return "ok"


def boom() -> int:
    raise ValueError("fail")


with ThreadPoolExecutor() as pool:
    f = pool.submit(slow)
    print("done before:", f.done())        # done before: False
    try:
        f.result(timeout=0.1)              # блокує до 0.1с
    except FTimeout:
        print("timed out")                  # timed out
    print("final:", f.result())            # final: ok  (тепер чекає скільки треба)

    fe = pool.submit(boom)
    print("exception:", repr(fe.exception()))   # exception: ValueError('fail')
```

- `f.result(timeout=...)` — забрати результат (або підняти виняток воркера);
  без таймауту блокує до готовності.
- `f.done()` — чи завершено (не блокує).
- `f.exception()` — повертає виняток як **значення** (не піднімає його), або `None`.

> **⚠️ Пастка.** `concurrent.futures.TimeoutError` — це **не** той самий
> `asyncio.TimeoutError` (а в 3.11+ обидва аліаси на `TimeoutError`, але імпортуй
> із правильного модуля). І `Future` тут — **не** `asyncio.Future`: у нього
> блокуючий `.result()`, його не можна `await`. Не змішуй два світи.

> **⚠️ Пастка «проковтнутий виняток».** Якщо викликати `submit` і **не** забрати
> `.result()`/`.exception()`, виняток у воркері зникне мовчки. Завжди споживай
> результат (часто через `as_completed`).

## 5. ProcessPoolExecutor — той самий API, але для CPU

Той самий інтерфейс (`submit`/`map`/`as_completed`), але задачі йдуть у **окремі
процеси** — обходять GIL і дають справжній паралелізм на ядрах.

```python
from concurrent.futures import ProcessPoolExecutor


def count_primes(limit: int) -> int:        # CPU-bound, чистий Python
    count = 0
    for n in range(2, limit):
        is_p = True
        for d in range(2, int(n**0.5) + 1):
            if n % d == 0:
                is_p = False
                break
        if is_p:
            count += 1
    return count


if __name__ == "__main__":                   # ОБОВ'ЯЗКОВО (див. пастку нижче)
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(count_primes, [10_000, 20_000, 30_000]))
    print("primes:", results)                # primes: [1229, 2262, 3245]
```

### Обмеження pickling

Процеси не ділять пам'ять — аргументи й результати **серіалізуються через
`pickle`** і передаються між процесами. Звідси правила:

- **Функція має бути на верхньому рівні модуля** (importable), не лямбда й не
  вкладена функція — інакше `PicklingError`.
- **Аргументи й результати мають бути picklable** (більшість вбудованих типів —
  так; відкриті файли, сокети, лямбди — ні).
- Передача великих об'єктів коштує дорого (серіалізація + копіювання). Процеси
  виграють лише коли обчислення **переважає** оверхед.

> **⚠️ Пастка `if __name__ == "__main__"`.** На macOS/Windows процеси
> створюються методом **spawn**: дочірній процес *заново імпортує* твій модуль.
> Без захисту `if __name__ == "__main__"` навколо коду, що створює пул, кожен
> дочірній процес знову запустить цей код → нескінченне розмноження процесів або
> `RuntimeError`. **Завжди** ховай запуск пулу процесів під цей guard. Тому
> приклади з процесами тут — окремі файли-скрипти, а не рядки в REPL.

> **Best practice.** Профіль навантаження: CPU-bound і функція чиста й
> top-level → `ProcessPoolExecutor`. Якщо дані величезні або погано
> серіалізуються — спершу зваж, чи паралелізм узагалі окупиться.

## 6. threading — низький рівень (коротко)

Сирий `threading` потрібен рідко — здебільшого бери `ThreadPoolExecutor`. Але
варто знати примітиви.

### Race condition і Lock

Кілька потоків, що пишуть у спільний стан без синхронізації, дають **гонку**:

```python
import threading, time

counter = 0


def inc_unsafe() -> None:
    global counter
    for _ in range(100):
        tmp = counter
        time.sleep(0)             # точка перемикання потоків → гонка стає видимою
        counter = tmp + 1


threads = [threading.Thread(target=inc_unsafe) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()                       # чекати завершення (як Swift Task await)
print("unsafe:", counter)          # unsafe: 145  (очікувалось 800; щоразу різне!)
```

`counter += 1` — це **читання → інкремент → запис** (кілька байткод-операцій).
GIL не робить його атомарним: потік може перемкнутися посередині. Виправлення —
`Lock`:

```python
import threading, time

counter = 0
lock = threading.Lock()


def inc_safe() -> None:
    global counter
    for _ in range(100):
        with lock:                 # критична секція — лише один потік усередині
            tmp = counter
            time.sleep(0)
            counter = tmp + 1


threads = [threading.Thread(target=inc_safe) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("safe:", counter)            # safe: 800  (завжди коректно)
```

> **⚠️ Пастка.** «GIL же є — навіщо Lock?» GIL гарантує атомарність окремих
> байткод-операцій, **не** ваших складених операцій (`+=`, read-modify-write).
> Спільний мутабельний стан між потоками **завжди** потребує `Lock` (або краще —
> черги). Це той самий клас багів, що data race у Swift, де рятує `actor`.

### queue.Queue — обмін між потоками

Замість ручних блокувань — потокобезпечна черга (патерн producer/consumer):

```python
import queue, threading

q: queue.Queue[int] = queue.Queue()


def worker() -> None:
    while True:
        item = q.get()             # блокує, поки не з'явиться елемент
        if item is None:
            break
        # ... обробка item ...
        q.task_done()


t = threading.Thread(target=worker)
t.start()
for x in range(10):
    q.put(x)
q.join()                            # чекати, поки всі елементи оброблено
q.put(None)                         # сигнал зупинки
t.join()
```

> **⚠️ Пастка.** `queue.Queue` — **не** `asyncio.Queue` ([Модуль 12, §6b](../12-async.md)).
> Перша блокує потік, друга віддає керування event loop. Не змішуй у межах одного
> механізму.

> **Best practice.** Майже завжди `ThreadPoolExecutor` замість ручних `Thread`.
> Якщо потрібен сирий `threading` — координуй через `queue.Queue`, а спільний
> стан захищай `Lock`.

## 7. multiprocessing — низький рівень для процесів (коротко)

`ProcessPoolExecutor` під капотом використовує `multiprocessing`. Сирий API
потрібен для тонкого контролю; для простих кейсів — executor.

```python
from multiprocessing import Pool


def square(n: int) -> int:
    return n * n


if __name__ == "__main__":                 # той самий guard, що й для ProcessPool
    with Pool(processes=2) as pool:
        print("pool.map:", pool.map(square, [1, 2, 3, 4]))   # [1, 4, 9, 16]
```

### Спільний стан між процесами — складно

Процеси **не** ділять пам'ять, тож `Lock` із `threading` тут не працює. Обмін —
лише через явні механізми:

- `multiprocessing.Queue` / `Pipe` — передача повідомлень.
- `multiprocessing.Manager` — проксі-об'єкти (`list`, `dict`), що синхронізуються
  між процесами (повільно, через серіалізацію).
- `multiprocessing.Value` / `Array` — спільна пам'ять для простих типів.

> **⚠️ Пастка.** Глобальна змінна, змінена в дочірньому процесі, **не** видна в
> батьківському — це окремі адресні простори (на відміну від потоків). Спроба
> «просто записати в спільний `dict`» мовчки нічого не дасть.

> **Best practice.** Не передавай мутабельний спільний стан між процесами. Будуй
> логіку як чисті функції: вхід → обчислення → результат (через `map`/`submit`).
> Якщо обмін неминучий — `Queue`/`Pipe`, а не спільні змінні.

## Шпаргалка / рецепти

```python
# I/O-bound, синхронна бібліотека → потоки
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as pool:
    results = list(pool.map(fetch_sync, urls))     # порядок аргументів

# CPU-bound → процеси (функція top-level + guard)
from concurrent.futures import ProcessPoolExecutor
if __name__ == "__main__":
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(heavy_cpu, items))

# окремі Future з таймаутом і обробкою винятків
from concurrent.futures import as_completed
with ThreadPoolExecutor() as pool:
    futs = [pool.submit(task, x) for x in items]
    for f in as_completed(futs):
        if exc := f.exception():
            log(exc)
        else:
            use(f.result())

# з async-коду викликати блокуючу функцію → у потік
result = await asyncio.to_thread(blocking_fn, arg)   # Модуль 12

# спільний стан між потоками → Lock або queue.Queue
with lock:
    shared += 1
```

Правила великим планом:

- **Executor > сирі Thread/Process.** `concurrent.futures` майже завжди.
- **Вибирай за навантаженням:** async (I/O+async), threads (I/O+sync), processes (CPU).
- **GIL:** потоки не пришвидшують CPU; процеси — так.
- **Процеси:** функція top-level, picklable аргументи, `if __name__ == "__main__"`.
- **Не ділити мутабельний стан** між процесами; між потоками — лише під `Lock`/через чергу.
- `Future.result()` — блокуючий, це не `asyncio.Future`; не плутай два світи.

## Див. також

- [Модуль 12 — Асинхронність](../12-async.md) — `asyncio`, event loop, `to_thread`, таблиця вибору.
- [Модуль 13 — Стандартна бібліотека та екосистема](../13-stdlib-and-ecosystem.md) — карта stdlib.
- [Модуль 00 — Ментальна модель](../00-tooling-and-mental-model.md) — GIL, реалізації CPython, free-threading.
- [Тематичний індекс](../INDEX.md).
