import unittest
from dataclasses import replace
import numpy as np
import _path  # noqa: F401
from dataplatform.contracts import Field, Contract
from dataplatform.evolution import compatibility, reference_check, sample_rows, _lee

V1 = Contract("c", 1, (Field("id", "int"), Field("amount", "float", min=0, max=100), Field("cat", "str", allowed=("A", "B")), Field("note", "str", nullable=True)), ("id",))


def con(*fields, pk=("id",)): return Contract("c", 2, tuple(fields), pk)


class TestTabla(unittest.TestCase):
    def test_identico_es_full(self):
        r = compatibility(V1, V1); self.assertTrue(r.full); self.assertEqual(r.breaking_changes, [])

    def test_agregar_campo_anulable_o_con_default_es_full(self):
        n = replace(V1, fields=V1.fields + (Field("extra", "str", nullable=True),)); r = compatibility(V1, n); self.assertTrue(r.full)
        n2 = replace(V1, fields=V1.fields + (Field("extra", "int", default=0),)); self.assertTrue(compatibility(V1, n2).full)

    def test_agregar_campo_requerido_rompe_hacia_atras(self):
        n = replace(V1, fields=V1.fields + (Field("req", "int"),)); r = compatibility(V1, n); self.assertFalse(r.backward); self.assertTrue(r.forward)

    def test_quitar_campo_requerido_rompe_hacia_adelante(self):
        n = replace(V1, fields=tuple(f for f in V1.fields if f.name != "cat")); r = compatibility(V1, n); self.assertTrue(r.backward); self.assertFalse(r.forward)

    def test_ampliar_tipo_int_a_float(self):
        v = con(Field("id", "int"), Field("x", "int")); n = con(Field("id", "int"), Field("x", "float")); r = compatibility(v, n); self.assertTrue(r.backward); self.assertFalse(r.forward)

    def test_cambio_de_tipo_incompatible(self):
        v = con(Field("id", "int"), Field("x", "str")); n = con(Field("id", "int"), Field("x", "int")); r = compatibility(v, n); self.assertFalse(r.backward); self.assertFalse(r.forward)

    def test_endurecer_rango_rompe_hacia_atras_y_relajar_hacia_adelante(self):
        n = replace(V1, fields=(V1.fields[0], Field("amount", "float", min=10, max=100)) + V1.fields[2:]); r = compatibility(V1, n); self.assertFalse(r.backward); self.assertTrue(r.forward)
        r2 = compatibility(n, V1); self.assertTrue(r2.backward); self.assertFalse(r2.forward)

    def test_anulable_a_requerido(self):
        n = replace(V1, fields=V1.fields[:3] + (Field("note", "str", nullable=False),)); r = compatibility(V1, n); self.assertFalse(r.backward); self.assertTrue(r.forward)

    def test_allowed(self):
        n = replace(V1, fields=(V1.fields[0], V1.fields[1], Field("cat", "str", allowed=("A", "B", "C")), V1.fields[3])); r = compatibility(V1, n); self.assertTrue(r.backward); self.assertFalse(r.forward)
        n2 = replace(V1, fields=(V1.fields[0], V1.fields[1], Field("cat", "str", allowed=("A",)), V1.fields[3])); self.assertFalse(compatibility(V1, n2).backward)

    def test_llave_primaria_distinta(self):
        n = replace(V1, primary_key=("id", "cat")); r = compatibility(V1, n); self.assertFalse(r.backward or r.forward); self.assertTrue(any("llave" in m for m in r.breaking_changes))

    def test_simetria_backward_forward(self):
        n = replace(V1, fields=V1.fields + (Field("req", "int"),)); a, b = compatibility(V1, n), compatibility(n, V1); self.assertEqual((a.backward, a.forward), (b.forward, b.backward))

    def test_reflexiva_y_transitividad_de_lectura(self):
        a = V1; b = replace(V1, fields=V1.fields + (Field("e1", "int", nullable=True),)); c = replace(b, fields=b.fields + (Field("e2", "str", nullable=True),))
        self.assertEqual(_lee(a, a), []); self.assertEqual(_lee(a, b), []); self.assertEqual(_lee(b, c), []); self.assertEqual(_lee(a, c), [])


def aleatorio(rg, n_campos=4):
    nombres = ["id"] + [f"f{i}" for i in range(n_campos)]; campos = [Field("id", "int")]
    for nm in nombres[1:]:
        t = rg.choice(["int", "float", "str"]); kw = {"nullable": bool(rg.random() < 0.4)}
        if t in ("int", "float") and rg.random() < 0.6: lo = float(rg.integers(-5, 5)); kw.update(min=lo, max=lo + float(rg.integers(1, 20)))
        if t == "str" and rg.random() < 0.5: kw["allowed"] = tuple(rg.choice(list("ABCDE"), int(rg.integers(1, 5)), replace=False))
        campos.append(Field(nm, str(t), **kw))
    return Contract("r", 1, tuple(campos), ("id",))


def mutar(c, rg):
    campos = list(c.fields); i = int(rg.integers(1, len(campos))); f = campos[i]; op = int(rg.integers(0, 6))
    if op == 0: campos[i] = replace(f, nullable=not f.nullable)
    elif op == 1 and f.dtype in ("int", "float") and f.min is not None: campos[i] = replace(f, min=f.min + float(rg.integers(-3, 4)), max=f.max + float(rg.integers(-3, 4)))
    elif op == 2 and f.allowed is not None: campos[i] = replace(f, allowed=tuple(sorted(set(f.allowed) ^ {str(rg.choice(list("ABCDE")))})) or f.allowed)
    elif op == 3: campos[i] = replace(f, dtype="float" if f.dtype == "int" else f.dtype)
    elif op == 4: campos.append(Field(f"n{len(campos)}", "int", nullable=bool(rg.random() < 0.5), default=0 if rg.random() < 0.3 else None))
    elif op == 5 and len(campos) > 2: campos.pop(i)
    return replace(c, fields=tuple(campos))


class TestVerificacionPorFuerzaBruta(unittest.TestCase):
    def test_la_tabla_es_correcta_respecto_de_la_muestra(self):
        """Solidez: si la regla dice 'el lector puede leer al escritor', ningun registro generado debe fallar."""
        rg = np.random.default_rng(0); pares = 0; compat = 0
        for k in range(300):
            w = aleatorio(rg); r = mutar(w, rg)
            for esc, lec in ((w, r), (r, w)):
                pares += 1
                if not _lee(esc, lec): compat += 1; self.assertTrue(reference_check(esc, lec, 200, seed=k), (esc, lec))
        self.assertGreater(compat, 100)

    def test_cuando_la_regla_dice_incompatible_la_muestra_casi_siempre_lo_confirma(self):
        rg = np.random.default_rng(1); inc = 0; confirma = 0
        for k in range(400):
            w = aleatorio(rg); r = mutar(w, rg)
            for esc, lec in ((w, r), (r, w)):
                m = _lee(esc, lec)
                if m and not any("llave" in x for x in m): inc += 1; confirma += (not reference_check(esc, lec, 400, seed=k))
        self.assertGreater(inc, 100); self.assertGreater(confirma / inc, 0.85)          # no es 1.0: ciertas rupturas (p. ej. patrones iguales) necesitan una muestra que las exhiba

    def test_sample_rows_cumple_el_contrato(self):
        from dataplatform.contracts import validate
        rg = np.random.default_rng(2)
        for _ in range(50):
            c = aleatorio(rg); rows = sample_rows(c, 100, rg); rows["id"] = range(len(rows)); self.assertTrue(validate(rows, c).quarantine.empty)


if __name__ == "__main__":
    unittest.main()
