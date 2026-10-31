import itertools
import random
import unittest
from src.balancing import balanced_split, fixture
from src.graph_audit import audit_graph
from src.splitter import Record


class GraphAuditTests(unittest.TestCase):
    def test_perfect(self):
        rows = fixture([2, 3, 4])
        a = audit_graph(rows, rows, balanced_split(rows))
        self.assertEqual(
            (a.declared_cuts, a.adjudicated_cuts, a.exposed_rows), (0, 0, 0)
        )
        self.assertEqual((a.false_positive_pairs, a.false_negative_pairs), (0, 0))

    def test_missing_links_counterexample(self):
        truth = [Record(str(i), ("all",)) for i in range(4)]
        observed = [Record(str(i), (str(i // 2),)) for i in range(4)]
        a = audit_graph(observed, truth, balanced_split(observed))
        self.assertEqual(
            (a.declared_cuts, a.adjudicated_cuts, a.exposed_rows), (0, 1, 4)
        )
        self.assertEqual((a.true_positive_pairs, a.false_negative_pairs), (2, 4))

    def test_overmerge_is_not_missing_link(self):
        obs = [Record(str(i), ("all",)) for i in range(4)]
        truth = [Record(str(i), (str(i // 2),)) for i in range(4)]
        a = audit_graph(obs, truth, dict.fromkeys(map(str, range(4)), "train"))
        self.assertEqual((a.false_positive_pairs, a.false_negative_pairs), (4, 0))

    def test_incomplete_truth_abstains(self):
        rows = fixture([2, 2])
        with self.assertRaises(ValueError):
            audit_graph(rows, rows[:-1], balanced_split(rows))
        with self.assertRaises(ValueError):
            audit_graph([], [], {})

    def test_invalid_assignment(self):
        rows = fixture([1, 1])
        for assignment in [{}, {"g000-r000": "invalid", "g001-r000": "test"}]:
            with self.assertRaises(ValueError):
                audit_graph(rows, rows, assignment)

    def test_random_partitions_against_pair_oracle(self):
        # Seeded property-style testing, not a Hypothesis coverage claim.
        rng = random.Random(310)
        for n in range(1, 25):
            for _ in range(8):
                o, t = (
                    [rng.randrange(5) for _ in range(n)],
                    [rng.randrange(5) for _ in range(n)],
                )
                observed = [Record(str(i), (f"o{o[i]}",)) for i in range(n)]
                truth = [Record(str(i), (f"t{t[i]}",)) for i in range(n)]
                assignment = {
                    str(i): "train" if rng.randrange(2) else "test" for i in range(n)
                }
                a = audit_graph(observed, truth, assignment)
                pairs = list(itertools.combinations(range(n), 2))
                self.assertEqual(
                    a.true_positive_pairs,
                    sum(o[i] == o[j] and t[i] == t[j] for i, j in pairs),
                )
                self.assertEqual(
                    a.false_positive_pairs,
                    sum(o[i] == o[j] and t[i] != t[j] for i, j in pairs),
                )
                self.assertEqual(
                    a.false_negative_pairs,
                    sum(o[i] != o[j] and t[i] == t[j] for i, j in pairs),
                )
                self.assertEqual(
                    sum(
                        [
                            a.true_positive_pairs,
                            a.false_positive_pairs,
                            a.false_negative_pairs,
                            a.true_negative_pairs,
                        ]
                    ),
                    n * (n - 1) // 2,
                )
                self.assertEqual(
                    a,
                    audit_graph(
                        list(reversed(observed)), list(reversed(truth)), assignment
                    ),
                )

    def test_singleton_no_pairs(self):
        row = [Record("a", ("x",))]
        a = audit_graph(row, row, {"a": "test"})
        self.assertEqual((a.rows, a.true_negative_pairs, a.exposed_rows), (1, 0, 0))
