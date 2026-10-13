import unittest
import numpy as np
import pandas as pd
import _path  # noqa: F401
from dataplatform.contracts import Field, Contract, validate

C = Contract("t", 1, (Field("id", "int"), Field("name", "str", nullable=True), Field("score", "float", min=0, max=100), Field("kind", "str", allowed=("a", "b")),
                      Field("code", "str", pattern=r"[A-Z]{2}"), Field("ts", "timestamp")), primary_key=("id",), freshness_field="ts", freshness_max_age=pd.Timedelta(days=2))


def base(n=5):
    return pd.DataFrame({"id": range(n), "name": ["x"] * n, "score": [10.0] * n, "kind": ["a"] * n, "code": ["AB"] * n, "ts": ["2024-01-01T00:00:00Z"] * n})


class TestValidate(unittest.TestCase):
    def test_datos_limpios(self):
        r = validate(base(), C); self.assertTrue(r.ok); self.assertEqual(len(r.valid_rows), 5); self.assertTrue(r.quarantine.empty)

    def test_no_muta_la_entrada(self):
        d = base(); d.loc[0, "score"] = 500; copia = d.copy(deep=True); validate(d, C); pd.testing.assert_frame_equal(d, copia)

    def _una(self, col, val, regla):
        d = base(); d[col] = d[col].astype(object); d.loc[2, col] = val; r = validate(d, C); self.assertEqual(len(r.quarantine), 1, (col, val)); self.assertEqual(r.quarantine["_reason"].iloc[0], regla); self.assertEqual(len(r.valid_rows), 4)

    def test_reglas_una_por_una(self):
        self._una("score", 101, "max:score"); self._una("score", -1, "min:score"); self._una("kind", "z", "allowed:kind"); self._una("code", "abc", "pattern:code")
        self._una("score", "no_numero", "type:score"); self._una("id", 1.5, "type:id"); self._una("ts", "no_fecha", "type:ts"); self._una("id", None, "null:id")

    def test_nulo_permitido_en_campo_anulable(self):
        d = base(); d.loc[1, "name"] = None; self.assertTrue(validate(d, C).ok)

    def test_columna_faltante(self):
        r = validate(base().drop(columns=["score"]), C); self.assertFalse(r.ok); self.assertEqual(len(r.valid_rows), 0); self.assertIn(("missing_column:score", 5), r.violations)

    def test_pk_duplicada_conserva_la_primera(self):
        d = base(); d.loc[3, "id"] = 1; r = validate(d, C); self.assertEqual(r.quarantine["_reason"].tolist(), ["duplicate_pk"]); self.assertEqual(r.quarantine.index.tolist(), [3]); self.assertIn(1, r.valid_rows["id"].tolist())

    def test_default_rellena_nulos(self):
        c2 = Contract("d", 1, (Field("a", "int"), Field("b", "float", default=0.0)), primary_key=("a",)); r = validate(pd.DataFrame({"a": [1, 2], "b": [None, 3.0]}), c2); self.assertTrue(r.ok); self.assertEqual(r.valid_rows["b"].tolist(), [0.0, 3.0])

    def test_frescura(self):
        now = pd.Timestamp("2024-01-02", tz="UTC"); self.assertFalse(validate(base(), C, now).stale)
        r = validate(base(), C, pd.Timestamp("2024-02-01", tz="UTC")); self.assertTrue(r.stale); self.assertFalse(r.ok)

    def test_booleanos_y_enteros_como_texto(self):
        c = Contract("b", 1, (Field("f", "bool"), Field("n", "int")), ()); r = validate(pd.DataFrame({"f": ["true", 0, "x"], "n": ["3", 4, 5]}), c); self.assertEqual(len(r.valid_rows), 2); self.assertEqual(r.quarantine["_reason"].iloc[0], "type:f")

    def test_dtype_invalido(self):
        with self.assertRaises(ValueError): Field("x", "decimal")

    def test_primera_regla_que_falla_gana(self):
        d = base(); d.loc[0, "score"] = 500; d.loc[0, "kind"] = "z"; r = validate(d, C); self.assertEqual(r.quarantine["_reason"].iloc[0], "max:score")

    def test_conteo_de_violaciones(self):
        d = base(8); d.loc[[1, 2, 3], "score"] = 999; r = validate(d, C); self.assertIn(("max:score", 3), r.violations); self.assertEqual(len(r.quarantine), 3)


if __name__ == "__main__":
    unittest.main()
