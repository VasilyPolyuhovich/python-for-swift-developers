# Тематичний індекс — «як зробити X у Python»

[← Курс](README.md)

Вікі-індекс по задачах: знаходь потрібне за дією, а не за модулем. Це доповнення
до [послідовної програми курсу](README.md#програма).

## Рядки й текст

- Розбити рядок / зібрати з частин (`split`/`join`) → [Рядки §4](01-syntax-and-control-flow/strings.md#4-split-і-join--робочі-конячки)
- Обрізати пробіли, прибрати префікс/суфікс (`strip`/`removeprefix`) → [Рядки §5](01-syntax-and-control-flow/strings.md)
- Пошук підрядка, `startswith`/`endswith`/`in` → [Рядки §6](01-syntax-and-control-flow/strings.md)
- Зміна регістру, порівняння без регістру (`casefold`) → [Рядки §7](01-syntax-and-control-flow/strings.md)
- Форматування чисел/виводу (f-string специфікатори) → [Рядки §3](01-syntax-and-control-flow/strings.md#3-f-strings-і-мова-форматування)
- `bytes` ↔ `str` (encode/decode) → [Рядки §10](01-syntax-and-control-flow/strings.md)
- Регулярні вирази → [re](13-stdlib-and-ecosystem/regex.md)

## Числа

- Цілочисельне ділення, остача, округлення → [Модуль 01 §3](01-syntax-and-control-flow.md#3-числа-й-арифметика)
- Гроші / точні дроби (`Decimal`, `Fraction`) → [Модуль 01 §3](01-syntax-and-control-flow.md#3-числа-й-арифметика)
- Бітові операції, системи числення → [Модуль 01 §3](01-syntax-and-control-flow.md) · [Конвертації §4](03-data-structures/conversions.md)

## Колекції: вибір і операції

- Який тип обрати (list/dict/set/tuple) → [Модуль 03](03-data-structures.md)
- Список: зрізи, методи, копіювання → [list](03-data-structures/list.md)
- Словник: `get`/`setdefault`, злиття, ітерація → [dict](03-data-structures/dict.md)
- Множина: унікальність, алгебра множин, O(1)-пошук → [set](03-data-structures/set.md)
- Кортеж: незмінний запис, розпакування, як ключ → [tuple](03-data-structures/tuple.md)
- Черга / стек / підрахунок (`deque`/`Counter`/`defaultdict`) → [Модуль 03 §6](03-data-structures.md#6-спеціалізовані-колекції--collections)
- Іменований запис (`NamedTuple`/`dataclass`) → [Модуль 06](06-structs-and-value-types.md)

## Трансформація, фільтрація, агрегація

- Перетворити/відфільтрувати колекцію (comprehensions) → [comprehensions](03-data-structures/comprehensions.md)
- `map`/`filter`/`sum`/`any`/`all` → [comprehensions](03-data-structures/comprehensions.md) · [Модуль 09 §6](09-iterators-and-generators.md)
- Згрупувати, об'єднати, «вікна», порції (`itertools`) → [Модуль 09 §5](09-iterators-and-generators.md#5-itertools--стандартна-бібліотека-ітерування)
- Ліниві послідовності, генератори (`yield`) → [Модуль 09](09-iterators-and-generators.md)
- Інвертувати словник, унікальні зі збереженням порядку → [comprehensions](03-data-structures/comprehensions.md) · [Конвертації](03-data-structures/conversions.md)

## Сортування

- Відсортувати (`sorted` vs `.sort()`) → [Сортування §1](03-data-structures/sorting.md#1-sorted-vs-sort)
- За ключем/полем (`key=`, `itemgetter`/`attrgetter`) → [Сортування §2](03-data-structures/sorting.md)
- За кількома ключами, змішані напрямки → [Сортування §3](03-data-structures/sorting.md#3-стабільність-і-кілька-ключів)
- Словник за значенням → [Сортування §4](03-data-structures/sorting.md#4-сортування-словників)
- Топ-N без повного сортування (`heapq`) → [Сортування §6](03-data-structures/sorting.md)
- Власний тип як `Comparable` (`__lt__`) → [Сортування §5](03-data-structures/sorting.md) · [dunder](05-classes-and-oop/dunder-methods.md)

## Конвертація типів

- `int`/`float`/`str`/`bool`, парсинг рядків → [Конвертації](03-data-structures/conversions.md)
- Між колекціями (list/set/dict/tuple), дедуплікація → [Конвертації §3](03-data-structures/conversions.md)
- Безпечний парсинг ненадійного вводу → [Конвертації §5](03-data-structures/conversions.md#5-безпечний-парсинг-ненадійного-вводу)
- Валідація зовнішніх даних (`pydantic`) → [Модуль 04](04-types-and-typing.md) · [Модуль 06 §5](06-structs-and-value-types.md)

## Функції

- Аргументи: default, keyword-only, `*args`/`**kwargs` → [Модуль 02](02-functions.md)
- Mutable default (пастка) / late-binding → [Модуль 02 §3](02-functions.md) · [§6](02-functions.md)
- Декоратори (свої, з параметрами, типізація) → [Декоратори](02-functions/decorators.md)
- Перевантаження за типом (`singledispatch`) → [Декоратори §6](02-functions/decorators.md)
- Мемоізація (`cache`/`lru_cache`) → [Декоратори §5](02-functions/decorators.md)

## Типи й перевірка

- Optional (`X | None`), narrowing → [Модуль 04 §2](04-types-and-typing.md)
- Вичерпність як у Swift switch (`assert_never`) → [Модуль 04 §10](04-types-and-typing.md) · [match](01-syntax-and-control-flow/match.md)
- `@override`, `Final`, `cast`, `@overload` → [Модуль 04](04-types-and-typing.md)
- Дженеріки (`class C[T]`, bounds, `ParamSpec`) → [Модуль 07](07-generics.md)
- Інтерфейси: structural (`Protocol`) vs nominal (`ABC`) → [Модуль 08](08-protocols-and-interfaces.md)

## Класи та ООП

- Властивості, `@cached_property`, приватність → [Модуль 05](05-classes-and-oop.md)
- Оператори/dunder (`__eq__`/`__lt__`/`__add__`/...) → [dunder](05-classes-and-oop/dunder-methods.md)
- Спадкування, `super()`, MRO → [Модуль 05 §6](05-classes-and-oop.md) · [MRO](05-classes-and-oop/descriptors-and-metaclasses.md)
- Дескриптори, `__slots__`, метакласи → [Дескриптори/метакласи](05-classes-and-oop/descriptors-and-metaclasses.md)
- `match` по класах (ADT, як Swift enum) → [match](01-syntax-and-control-flow/match.md) · [Модуль 06 §4](06-structs-and-value-types.md)

## Помилки та ресурси

- `try/except/else/finally`, власні винятки → [Модуль 10](10-errors-and-exceptions.md)
- Гарантоване очищення (`with`, контекст-менеджери) → [Модуль 10 §6](10-errors-and-exceptions.md)
- Динамічна кількість ресурсів (`ExitStack`) → [Модуль 10 §6](10-errors-and-exceptions.md)
- Кілька помилок разом (`except*`) → [Модуль 10 §7b](10-errors-and-exceptions.md)
- Ретраї (`tenacity`) → [Модуль 10](10-errors-and-exceptions.md)

## Асинхронність і паралелізм

- `async`/`await`, `asyncio.run` → [Модуль 12](12-async.md)
- Конкурентні задачі (`TaskGroup`, `gather`) → [Модуль 12 §4](12-async.md)
- Обмеження конкурентності, черги (`Semaphore`, `Queue`) → [Модуль 12 §6b](12-async.md)
- CPU-bound паралелізм (процеси) → [Паралелізм](13-stdlib-and-ecosystem/concurrency.md)
- Блокуючий код у async (`to_thread`) → [Модуль 12 §6](12-async.md)

## Файли, дані, IO

- Шляхи, читання/запис файлів (`pathlib`) → [Файли](13-stdlib-and-ecosystem/files-and-serialization.md)
- JSON ↔ об'єкти → [Файли](13-stdlib-and-ecosystem/files-and-serialization.md) · [Модуль 06 §6](06-structs-and-value-types.md)
- Дати, час, таймзони → [Дати](13-stdlib-and-ecosystem/datetime.md)
- SQLite-запити → [SQLite](13-stdlib-and-ecosystem/sqlite.md)
- Зовнішні процеси, env-змінні → [Процеси та ОС](13-stdlib-and-ecosystem/subprocess-and-os.md)
- HTTP-запити (`httpx`) → [Модуль 13](13-stdlib-and-ecosystem.md#http-клієнти)

## Проєкт, інструменти, тести

- Налаштувати середовище (`uv`/`ruff`/`pyright`) → [Модуль 00](00-tooling-and-mental-model.md)
- Структура проєкту, імпорти, пакети → [Модуль 11](11-modules-and-packages.md)
- CLI-команда з пакета (entry points) → [Модуль 11 §9](11-modules-and-packages.md) · [CLI](13-stdlib-and-ecosystem/cli.md)
- Тести (`pytest`, fixtures, parametrize) → [pytest](13-stdlib-and-ecosystem/pytest.md)
- Профілювання, вимірювання → [Модуль 00 §7](00-tooling-and-mental-model.md#7-профілювання-та-вимірювання)

## Пастки, де інтуїція зі Swift підводить

- Reference semantics (`b = a` — спільне посилання) → [Модуль 00 §1](00-tooling-and-mental-model.md) · [list](03-data-structures/list.md)
- Mutable default arguments → [Модуль 02 §3](02-functions.md)
- `is` vs `==`, інтернінг → [Модуль 00 §3](00-tooling-and-mental-model.md#3-модель-обєктів-і-память)
- `match` без вичерпності → [match](01-syntax-and-control-flow/match.md)
- `asyncio` ≠ паралелізм (GIL) → [Модуль 12 §2](12-async.md)
- Винятки не видно в сигнатурі → [Модуль 10 §1](10-errors-and-exceptions.md)
- Генератор одноразовий → [Модуль 09 §6](09-iterators-and-generators.md)
