import unittest
from src.partial_audit import partial_audit
from src.splitter import Record


def partitions(n):
    """Independent restricted-growth-string enumeration, Bell(n) states."""
    if n == 0:
        yield ()
        return

    def grow(labels):
        if len(labels) == n:
            yield tuple(labels)
        else:
            for label in range(max(labels) + 2):
                yield from grow(labels + [label])

    yield from grow([0])


def exposed(labels, sides):
    return sum(
        len({sides[j] for j in range(len(labels)) if labels[j] == g}) == 2
        for g in labels
    )


class PartialTests(unittest.TestCase):
    def test_empty_adjudication_abstains(self):
        o = [Record(str(i), (str(i),)) for i in range(4)]
        a = partial_audit(
            o, [], {str(i): "train" if i < 2 else "test" for i in range(4)}
        )
        self.assertEqual(
            (a.lower_exposed_rows, a.upper_exposed_rows, a.decision), (0, 4, "abstain")
        )

    def test_complete_exact(self):
        o = [Record(str(i), (str(i),)) for i in range(4)]
        k = [Record(str(i), (str(i // 2),)) for i in range(4)]
        a = partial_audit(
            o, k, {str(i): "train" if i % 2 else "test" for i in range(4)}
        )
        self.assertEqual(
            (a.lower_exposed_rows, a.upper_exposed_rows, a.decision), (4, 4, "detected")
        )

    def test_sharper_than_universe(self):
        o = [Record(str(i), (str(i),)) for i in range(6)]
        k = [Record(str(i), (str(i),)) for i in range(5)]
        a = partial_audit(
            o, k, {str(i): "train" if i < 3 else "test" for i in range(6)}
        )
        self.assertEqual((a.lower_exposed_rows, a.upper_exposed_rows), (0, 2))

    def test_all_one_side(self):
        o = [Record("a", ("a",)), Record("b", ("b",))]
        a = partial_audit(o, [], {"a": "train", "b": "train"})
        self.assertEqual((a.upper_exposed_rows, a.decision), (0, "conditional-zero"))

    def test_validation(self):
        o = [Record("a", ("x",))]
        for bad in [[], [Record("b", ("x",))]]:
            with self.assertRaises(ValueError):
                partial_audit(o, bad, {})
        with self.assertRaises(ValueError):
            partial_audit([], [], {})
        with self.assertRaises(ValueError):
            partial_audit(o, [Record("a", ("x",)), Record("a", ("y",))], {"a": "train"})

    def test_sharpness_exhaustive_completions(self):
        # Every true partition n<=6, every prefix coverage, and three split regimes.
        cases = 0
        for n in range(1, 7):
            ps = list(partitions(n))
            o = [Record(str(i), (f"o{i}",)) for i in range(n)]
            for p in ps:
                for k in range(n + 1):
                    known = [Record(str(i), (f"t{p[i]}",)) for i in range(k)]
                    completions = [
                        q
                        for q in ps
                        if all(
                            (p[i] == p[j]) == (q[i] == q[j])
                            for i in range(k)
                            for j in range(i)
                        )
                    ]
                    for sides in [
                        tuple("train" if i % 2 else "test" for i in range(n)),
                        tuple("train" if i < n // 2 else "test" for i in range(n)),
                        ("train",) * n,
                    ]:
                        a = partial_audit(
                            o, known, {str(i): sides[i] for i in range(n)}
                        )
                        values = [exposed(q, sides) for q in completions]
                        self.assertEqual(
                            (a.lower_exposed_rows, a.upper_exposed_rows),
                            (min(values), max(values)),
                            (p, k, sides),
                        )
                        self.assertEqual(
                            a,
                            partial_audit(
                                list(reversed(o)),
                                list(reversed(known)),
                                {str(i): sides[i] for i in range(n)},
                            ),
                        )
                        cases += 1
        self.assertEqual(cases, 5508)

    def test_full_distinct_zero(self):
        o = [Record("a", ("a",)), Record("b", ("b",))]
        a = partial_audit(o, o, {"a": "train", "b": "test"})
        self.assertEqual(
            (a.lower_exposed_rows, a.upper_exposed_rows, a.decision),
            (0, 0, "conditional-zero"),
        )

    def test_wrong_adjudication_not_detectable(self):
        # Outside assumptions: complete labels falsely declare two distinct people.
        o = [Record("a", ("a",)), Record("b", ("b",))]
        a = partial_audit(o, o, {"a": "train", "b": "test"})
        self.assertEqual(a.decision, "conditional-zero")
        # If reality is one person, both rows leak. API cannot infer that truth.
        self.assertEqual(exposed((0, 0), ("train", "test")), 2)
