# Дати та час

[← Курс](../README.md) · [Модуль 13](../13-stdlib-and-ecosystem.md) · **Дати та час**

У Swift роботою з часом займаються `Date` (момент часу, по суті — кількість
секунд від reference date), `Calendar` + `DateComponents` (розклад на рік/місяць/
день у конкретному календарі та таймзоні) і `DateFormatter`/`ISO8601DateFormatter`
для розбору й форматування. У Python усе це — модуль `datetime` зі stdlib плюс
`zoneinfo` для таймзон. Філософія схожа, але назви типів і пастки інші.

---

## 1. Чотири типи: `date`, `time`, `datetime`, `timedelta`

```python
from datetime import date, time, datetime, timedelta

date(2024, 1, 2)          # лише календарна дата (рік-місяць-день)
time(10, 30)              # лише час доби (без дати), 10:30:00
datetime(2024, 1, 2, 10, 30)   # дата + час разом
timedelta(days=1, hours=3)     # ТРИВАЛІСТЬ (різниця), не момент
```

- `date` / `time` — окремі «половинки»; рідко потрібні самі по собі.
- `datetime` — головний робочий тип (аналог `Date` + `DateComponents` в одному).
- `timedelta` — це не момент, а **проміжок** (як `TimeInterval`/`DateComponents`
  для арифметики).

```swift
// Swift
let now = Date()
let later = now.addingTimeInterval(3600)        // +1 година
let comps = Calendar.current.dateComponents([.year, .month, .day], from: now)
```

### Aware vs naive — головна пастка

`datetime` буває **aware** (знає свою таймзону, поле `tzinfo` заповнене) або
**naive** (без таймзони, `tzinfo is None`). Naive — це джерело багів: незрозуміло,
чи це UTC, чи локальний час, чи щось третє.

```python
from datetime import datetime, UTC

datetime.now(UTC).tzinfo      # UTC          — aware ✅
datetime.now().tzinfo         # None         — naive ⚠️ (локальний, але без позначки)
```

> **⚠️ Пастка.** `datetime.now()` без аргументу повертає **naive** datetime у
> локальному часі машини. Це міна сповільненої дії: на сервері в іншій таймзоні
> або при порівнянні з UTC ти отримаєш зсув або `TypeError`. Завжди пиши
> `datetime.now(UTC)`.

> **Best practice.** Завжди працюй із **aware** datetime, зберігай і передавай у
> **UTC**, конвертуй у локальну таймзону лише на межі з користувачем (відображення).
> Це той самий принцип, що й у Swift: `Date` — момент в абсолютному часі, а
> локалізація — на рівні `DateFormatter`.

---

## 2. Таймзони — `zoneinfo`

`zoneinfo.ZoneInfo` (stdlib з 3.9) бере зони з бази IANA (ті самі
`"Europe/Kyiv"`, `"America/New_York"`, що й у Swift `TimeZone(identifier:)`).
`UTC` — готова константа з `datetime`.

```python
from datetime import datetime, UTC
from zoneinfo import ZoneInfo

dt = datetime(2024, 1, 2, 10, 30, tzinfo=UTC)
dt.isoformat()                                   # '2024-01-02T10:30:00+00:00'

# astimezone — переводить ТОЙ САМИЙ момент в іншу зону (не змінює момент)
kyiv = dt.astimezone(ZoneInfo("Europe/Kyiv"))
kyiv.isoformat()                                 # '2024-01-02T12:30:00+02:00'
```

`astimezone` — аналог конвертації через `Calendar`/`TimeZone` у Swift: змінюється
лише представлення (стінний годинник), а абсолютний момент той самий.

---

## 3. Конструювання

```python
from datetime import datetime, date, UTC
from zoneinfo import ZoneInfo

datetime(2024, 1, 2, 10, 30, tzinfo=UTC)              # явний момент в UTC
datetime(2024, 1, 2, 10, 30, tzinfo=ZoneInfo("Europe/Kyiv"))

date.today()                  # сьогоднішня дата (локальна), тип date
datetime.now(UTC)             # поточний момент, aware
```

`date.today()` дає naive `date` (у дат таймзони немає сенсу) — це нормально, бо
це календарна дата, а не момент.

---

## 4. Арифметика з `timedelta`

```python
from datetime import datetime, timedelta, UTC

now = datetime(2024, 1, 2, 10, 30, tzinfo=UTC)

later = now + timedelta(days=1, hours=3)
later.isoformat()             # '2024-01-03T13:30:00+00:00'

# різниця двох datetime → timedelta
diff = later - now            # datetime.timedelta(days=1, seconds=10800)
str(diff)                     # '1 day, 3:00:00'
diff.total_seconds()          # 97200.0  — уся тривалість у секундах (float)
```

- `datetime ± timedelta → datetime`
- `datetime − datetime → timedelta`
- `.total_seconds()` — повна тривалість у секундах (а не «залишок секунд»;
  поле `.seconds` навпаки повертає лише залишок у межах доби — легко переплутати).

```swift
// Swift-аналог
let later = now.addingTimeInterval(86400 + 3 * 3600)
let diff = later.timeIntervalSince(now)          // 97200.0
```

---

## 5. Форматування та парсинг

### Форматування: `strftime` і `isoformat`

```python
from datetime import datetime, UTC

dt = datetime(2024, 1, 2, 10, 30, tzinfo=UTC)

dt.isoformat()                              # '2024-01-02T10:30:00+00:00'  — ISO 8601
dt.strftime("%Y-%m-%d %H:%M:%S %A %B")      # '2024-01-02 10:30:00 Tuesday January'
```

Найуживаніші коди `strftime`/`strptime`:

| Код | Значення | Приклад |
|-----|----------|---------|
| `%Y` | рік, 4 цифри | `2024` |
| `%m` | місяць, 01–12 | `01` |
| `%d` | день, 01–31 | `02` |
| `%H` | години, 00–23 | `10` |
| `%M` | хвилини | `30` |
| `%S` | секунди | `00` |
| `%A` | день тижня, повна назва | `Tuesday` |
| `%B` | місяць, повна назва | `January` |

Назви днів/місяців за замовчуванням англійською (локаль процесу); це аналог
`dateFormat` в `DateFormatter`, а не локалізований `.dateStyle`.

### Парсинг: `fromisoformat` (швидкий шлях) і `strptime`

```python
from datetime import datetime

# fromisoformat — для ISO 8601; швидкий і простий, віддавай йому перевагу
datetime.fromisoformat("2024-01-02T10:30:00+00:00")     # aware, з +00:00

# strptime — за явним форматом-шаблоном
datetime.strptime("2024-01-02 10:30", "%Y-%m-%d %H:%M")  # naive (формат без зони)
```

> **⚠️ Пастка.** `strptime` **строгий** до формату: рядок має точно збігатися з
> шаблоном, інакше `ValueError`.
>
> ```python
> datetime.strptime("2024-01-02", "%Y-%m-%d %H:%M")
> # ValueError: time data '2024-01-02' does not match format '%Y-%m-%d %H:%M'
> ```
>
> Якщо вхід — ISO 8601, не складай шаблон вручну, бери `fromisoformat`: швидше і
> без помилок у `%`-кодах.

---

## 6. Unix timestamps

```python
from datetime import datetime, UTC

dt = datetime(2024, 1, 2, 10, 30, tzinfo=UTC)

dt.timestamp()                              # 1704191400.0  — секунди від епохи (float)
datetime.fromtimestamp(1704191400.0, UTC)   # назад у aware datetime (UTC)
```

> **⚠️ Пастка.** `datetime.fromtimestamp(ts)` без таймзони дасть **naive** у
> локальному часі. Завжди передавай `UTC` другим аргументом, як вище. Аналог
> `Date(timeIntervalSince1970:)` у Swift, але там абсолютність гарантована типом.

---

## 7. Порівняння та сортування

Aware datetime порівнюються й сортуються коректно — Python зводить їх до спільного
моменту, навіть якщо таймзони різні. Це працює зі звичайним `sorted()` і `key=`
([Сортування](../03-data-structures/sorting.md)):

```python
from datetime import datetime, UTC

events = [
    datetime(2024, 3, 1, tzinfo=UTC),
    datetime(2024, 1, 1, tzinfo=UTC),
    datetime(2024, 2, 1, tzinfo=UTC),
]
[d.month for d in sorted(events)]       # [1, 2, 3]
```

> **⚠️ Пастка.** Не можна порівнювати aware з naive — це `TypeError`:
>
> ```python
> datetime(2024, 1, 2, 10, 30) < datetime(2024, 1, 2, 10, 30, tzinfo=UTC)
> # TypeError: can't compare offset-naive and offset-aware datetimes
> ```
>
> Ще одна причина тримати ВСЕ aware: змішування типів у списку для сортування
> впаде на першому ж порівнянні різнорідних елементів.

---

## 8. Вимірювання тривалості — `time`, не `datetime`

Для замірів «скільки тривав код» **не** використовуй `datetime.now()`: системний
годинник може стрибнути (NTP-синхронізація, перехід на літній час) і дати
від'ємний або викривлений інтервал. Бери монотонний годинник із `time`:

```python
import time

t0 = time.perf_counter()        # монотонний, висока роздільність — для бенчмарків
# ... робота ...
elapsed = time.perf_counter() - t0      # float-секунди, завжди ≥ 0

time.monotonic()                # монотонний; не йде назад (для таймаутів)
time.sleep(0.5)                 # пауза на 0.5 с (блокує; в async — asyncio.sleep)
```

Це паралель до `Date()`-замірів проти `DispatchTime`/`ContinuousClock` у Swift:
для тривалостей — монотонний годинник, для «котра година» — календарний.

---

## 9. Сторонні бібліотеки (коротко)

Stdlib повністю достатньо. Але якщо API `datetime` здається незручним, є
дружніші обгортки на PyPI:

- **`whenever`** — сучасна, типобезпечна, явно розділяє aware/naive на рівні типів
  (найближче до духу Swift `Date`).
- **`pendulum`** — зручні зсуви, періоди, людиночитані різниці.
- **`arrow`** — простий ергономічний API навколо `datetime`.

> **Best practice.** Для більшості задач — голий `datetime` + `zoneinfo`. Тягни
> сторонню бібліотеку лише коли реально багато роботи з таймзонами/періодами і
> ергономіка stdlib заважає.

---

## Шпаргалка / рецепти

```python
from datetime import datetime, date, timedelta, UTC
from zoneinfo import ZoneInfo
import time

datetime.now(UTC)                              # поточний момент, aware ✅
datetime(2024, 1, 2, 10, 30, tzinfo=UTC)       # явний момент в UTC
date.today()                                   # сьогоднішня календарна дата

dt.astimezone(ZoneInfo("Europe/Kyiv"))         # той самий момент в іншій зоні
dt + timedelta(days=1, hours=3)                # арифметика
(b - a).total_seconds()                        # різниця у секундах

dt.isoformat()                                 # → ISO 8601 рядок
datetime.fromisoformat("2024-01-02T10:30:00+00:00")   # ISO → datetime (швидкий шлях)
dt.strftime("%Y-%m-%d %H:%M")                  # власний формат
datetime.strptime(s, "%Y-%m-%d %H:%M")         # парсинг за шаблоном (строгий!)

dt.timestamp()                                 # → Unix-секунди (float)
datetime.fromtimestamp(ts, UTC)                # Unix → aware datetime

sorted(events)                                 # aware сортуються нормально
time.perf_counter()                            # вимір тривалості (НЕ datetime)
```

## Див. також

- [Модуль 13 — Стандартна бібліотека](../13-stdlib-and-ecosystem.md) — мапінг Foundation → Python.
- [Файли та серіалізація](files-and-serialization.md) — збереження дат (ISO 8601 у JSON).
- [Сортування](../03-data-structures/sorting.md) — `sorted()`, `key=`, стабільність.
- [Тематичний індекс](../INDEX.md).
