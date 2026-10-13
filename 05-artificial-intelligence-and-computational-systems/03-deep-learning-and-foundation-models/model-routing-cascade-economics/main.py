"""Demostracion corta: cascada pequeno->grande, umbral conforme con garantia y comparacion con las referencias."""
import pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from routerlab.world import World, DEFAULT_TIERS
from routerlab import policies as PO, conformal as CF

w = World(tiers=[t for t in DEFAULT_TIERS if t.name != "medium"]); cal = w.sample(2000, np.random.default_rng(0)); test = w.sample(50000, np.random.default_rng(1)); eps = 0.03
lam = CF.calibrate_threshold(cal, eps); filas = {"siempre pequeno": PO.always_tier(test, w, "small"), "siempre grande": PO.always_tier(test, w, "large"), f"cascada conforme (eps={eps})": PO.cascade(test, w, [lam]), "oraculo": PO.oracle_router(test, w)}
print(f"umbral conforme {lam:.3f} | perdida de calidad esperada <= {eps} (garantia en muestra finita)\n{'politica':28s} calidad  costo  escalacion")
for n, r in filas.items(): e = PO.evaluate(r); print(f"{n:28s} {e['quality']:.3f}   {e['mean_cost']:5.2f}   {e['escalation_rate']:.0%}")
print(f"perdida de calidad frente al grande (prueba): {CF.losses(test, lam).mean():.4f}")
