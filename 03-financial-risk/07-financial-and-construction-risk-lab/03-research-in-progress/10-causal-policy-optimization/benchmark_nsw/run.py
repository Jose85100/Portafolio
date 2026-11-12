"""Benchmark didáctico de selección de política con datos NSW experimentales."""
import hashlib
import random
import subprocess

BASE = 'https://users.nber.org/~rdehejia/data/'
FILES = {
    'nswre74_treated.txt': (185, 'e7b742fe0ff07a0f45e129b4ff108bb9611cd83d53604732c48a8a0a3e20eda3'),
    'nswre74_control.txt': (260, 'a1364cea459d953dc691a667d99194b4ad335d6d550354fe23a5d2dc58d729b5'),
}
rows = []
for name, (count, digest) in FILES.items():
    raw = subprocess.run(["curl", "-fsSL", "--max-time", "30", BASE + name], check=True, capture_output=True).stdout
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError(f'Fuente cambió: {name}; revisar procedencia')
    part = [list(map(float, line.split())) for line in raw.decode().splitlines() if line.strip()]
    if len(part) != count or any(len(row) != 10 for row in part):
        raise ValueError(f'Esquema inesperado: {name}')
    rows.extend(part)

rng = random.Random(42)
train, test = [], []
for treatment in (0, 1):
    group = [r for r in rows if r[0] == treatment]
    rng.shuffle(group)
    cut = int(len(group) * .7)
    train.extend(group[:cut]); test.extend(group[cut:])
# Probabilidad de asignación aproximada por la proporción experimental de entrenamiento.
p = sum(r[0] for r in train) / len(train)
policies = {'nunca': lambda r: 0, 'siempre': lambda r: 1,
            're75_menor_5000': lambda r: int(r[8] < 5000),
            'sin_ingresos_1975': lambda r: int(r[8] == 0)}
def value(data, policy):
    return sum(r[9] * (r[0] == policy(r)) / (p if r[0] else 1-p) for r in data) / len(data)
chosen = max(policies, key=lambda name: value(train, policies[name]))
print(f'n={len(rows)} train={len(train)} test={len(test)} p_estimado={p:.4f}')
print(f'política elegida en entrenamiento: {chosen}')
for name in (chosen, 'nunca', 'siempre'):
    print(f'{name}: valor IPW en prueba = {value(test, policies[name]):.2f} USD de ingresos 1978')
