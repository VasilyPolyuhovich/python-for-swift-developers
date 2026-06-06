"""Курований набір прогоновних прикладів із курсу.

Це НЕ повне витягування всіх код-блоків (більшість сніпетів у курсі —
навмисні фрагменти). Тут зібрані ключові документовані факти у вигляді
assert-ів, щоб CI ловив, якщо поведінка Python зміниться і приклади «протухнуть».

Запуск:  uv run pytest   (або: python -m pytest)
"""

# --- Модуль 01: рядки та числа ---

def test_string_methods() -> None:
    assert "a,b,,c".split(",") == ["a", "b", "", "c"]
    assert "a b   c".split() == ["a", "b", "c"]
    assert "-".join(["2024", "01", "02"]) == "2024-01-02"
    assert "Hello".replace("l", "L", 1) == "HeLlo"
    assert "file.py".endswith((".py", ".pyi"))
    assert "test_file.py".removesuffix(".py") == "test_file"
    assert "café".casefold() == "CAFÉ".casefold()
    assert "archive.tar.gz".partition(".") == ("archive", ".", "tar.gz")


def test_numbers() -> None:
    assert 7 / 2 == 3.5
    assert 7 // 2 == 3
    assert -7 // 2 == -4          # floor division
    assert -7 % 2 == 1
    assert round(2.5) == 2        # banker's rounding
    assert round(3.5) == 4
    assert divmod(17, 5) == (3, 2)
    assert 2**1000 > 10**300      # arbitrary precision


def test_fstring_format() -> None:
    assert f"{1234567:,}" == "1,234,567"
    assert f"{255:#x}" == "0xff"
    assert f"{0.1234:.1%}" == "12.3%"
    assert f"{'hi':>8}" == "      hi"


# --- Модуль 03: колекції, сортування, конвертації ---

def test_sorting_stability_multikey() -> None:
    from operator import itemgetter

    people = [("Bob", 30), ("Alice", 30), ("Carol", 25)]
    by_age = sorted(people, key=itemgetter(1))
    assert [p[0] for p in by_age] == ["Carol", "Bob", "Alice"]
    # стабільність: вторинний ключ спершу, тоді головний
    s = sorted(people, key=itemgetter(0))
    s = sorted(s, key=itemgetter(1), reverse=True)
    assert [p[0] for p in s] == ["Alice", "Bob", "Carol"]


def test_sort_in_place_returns_none() -> None:
    x = [3, 1, 2]
    assert x.sort() is None
    assert x == [1, 2, 3]


def test_dict_sort_by_value() -> None:
    scores = {"math": 90, "art": 85, "cs": 95}
    assert max(scores, key=lambda k: scores[k]) == "cs"
    assert list(dict(sorted(scores.items(), key=lambda kv: kv[1]))) == ["art", "math", "cs"]


def test_conversions() -> None:
    assert int("FF", 16) == 255
    assert int(3.99) == 3            # truncates toward zero
    assert list("abc") == ["a", "b", "c"]
    assert set([1, 1, 2, 3]) == {1, 2, 3}
    assert dict(zip(["x", "y"], [1, 2])) == {"x": 1, "y": 2}
    assert list(dict.fromkeys([3, 1, 3, 2, 1])) == [3, 1, 2]   # unique, order kept


def test_comprehensions() -> None:
    assert [x * x for x in range(5)] == [0, 1, 4, 9, 16]
    assert {k: ord(k) for k in "ab"} == {"a": 97, "b": 98}
    matrix = [[1, 2, 3], [4, 5, 6]]
    assert [n for row in matrix for n in row] == [1, 2, 3, 4, 5, 6]


# --- Модуль 06: dataclass ---

def test_dataclass_field_and_post_init() -> None:
    from dataclasses import dataclass, field, InitVar

    @dataclass
    class Account:
        balance: float
        discount: InitVar[float] = 0.0
        net: float = field(init=False, default=0.0)

        def __post_init__(self, discount: float) -> None:
            self.net = self.balance * (1 - discount)

    a = Account(100.0, discount=0.1)
    assert a.net == 90.0


def test_dataclass_compare_false() -> None:
    from dataclasses import dataclass, field

    @dataclass
    class User:
        name: str
        id: int = field(compare=False)

    assert User("Vasyl", 1) == User("Vasyl", 2)
    assert User("Vasyl", 1) != User("Olha", 1)


def test_enum_flag() -> None:
    from enum import Flag, auto

    class Perm(Flag):
        READ = auto()
        WRITE = auto()
        EXEC = auto()

    p = Perm.READ | Perm.WRITE
    assert Perm.READ in p
    assert Perm.EXEC not in p


# --- Модуль 07: дженеріки (type erasure) ---

def test_generic_type_erasure() -> None:
    class Box[T]:
        def __init__(self, v: T) -> None:
            self.v = v

    b = Box[int](5)
    assert type(b).__name__ == "Box"
    assert isinstance(b, Box)


# --- Модуль 09: ітератори / itertools ---

def test_itertools() -> None:
    import itertools as it

    assert list(it.pairwise([1, 2, 3, 4])) == [(1, 2), (2, 3), (3, 4)]
    assert [list(b) for b in it.batched(range(7), 3)] == [[0, 1, 2], [3, 4, 5], [6]]
    assert list(it.chain.from_iterable([[1, 2], [3]])) == [1, 2, 3]


def test_reusable_iterable() -> None:
    class Squares:
        def __init__(self, n: int) -> None:
            self.n = n

        def __iter__(self):
            return (i * i for i in range(self.n))

    sq = Squares(3)
    assert list(sq) == [0, 1, 4]
    assert list(sq) == [0, 1, 4]   # повторюваність


# --- Модуль 10: винятки ---

def test_exception_group() -> None:
    caught: list[str] = []
    try:
        raise ExceptionGroup("multi", [ValueError("a"), TypeError("b")])
    except* ValueError as eg:
        caught.extend(str(e) for e in eg.exceptions)
    except* TypeError as eg:
        caught.extend(str(e) for e in eg.exceptions)
    assert sorted(caught) == ["a", "b"]


# --- Модуль 01: match ---

def test_match_patterns() -> None:
    def describe(x: object) -> str:
        match x:
            case 0:
                return "zero"
            case [a, b, *rest]:
                return f"list {a},{b} +{len(rest)}"
            case {"type": t}:
                return f"dict {t}"
            case _:
                return "other"

    assert describe(0) == "zero"
    assert describe([1, 2, 3, 4]) == "list 1,2 +2"
    assert describe({"type": "circle"}) == "dict circle"
    assert describe("x") == "other"
