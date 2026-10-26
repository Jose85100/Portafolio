"""Idea 6.1: proyeccion de una correlacion indefinida al cono PSD (Higham 2002, Frobenius)
y efecto sobre el cuantil 99,9 % de perdida de cartera (copula gaussiana). Semilla fija."""
import numpy as np
from scipy import stats
rng = np.random.default_rng(6161)
n = 30; M = 300_000; q = 0.999

# Correlacion "verdadera" de un factor: rho_ij = b_i b_j, con b_i en [0.3,0.6]
b = rng.uniform(0.3, 0.6, n)
C_true = np.outer(b, b); np.fill_diagonal(C_true, 1.0)

# Estimacion pairwise con ventana corta: ruido en cada entrada -> puede ser indefinida
T = 60
F = rng.standard_normal((T, 1))
X = F @ b[None, :] + np.sqrt(1 - b**2)[None, :] * rng.standard_normal((T, n))
C_pair = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        xi, xj = X[:, i], X[:, j]
        C_pair[i, j] = np.corrcoef(xi, xj)[0, 1] if i != j else 1.0
# Ruido pairwise adicional (tipico con ventanas cortas y pares con datos faltantes)
noise = rng.normal(0, 0.12, (n, n)); noise = (noise + noise.T) / 2; np.fill_diagonal(noise, 0)
C_raw = C_pair + noise
np.fill_diagonal(C_raw, 1.0)
print("min autovalor C_raw:", round(np.linalg.eigvalsh(C_raw).min(), 4))

def higham_nearest_corr(A, tol=1e-10, max_iter=500):
    """Proyeccion alternada (Higham 2002) sobre PSD y diagonal unitaria, norma de Frobenius."""
    Y = A.copy(); dS = np.zeros_like(A)
    for _ in range(max_iter):
        R = Y - dS
        w, V = np.linalg.eigh(R)
        X_ = (V * np.maximum(w, 0)) @ V.T
        dS = X_ - R
        Y = X_.copy(); np.fill_diagonal(Y, 1.0)
        if np.linalg.eigvalsh(Y).min() > -tol and np.abs(Y - X_).max() < tol:
            break
    return Y

def eig_clip(A):
    w, V = np.linalg.eigh(A); w = np.maximum(w, 1e-10)
    Y = (V * w) @ V.T; d = np.sqrt(np.diag(Y)); return Y / np.outer(d, d)

C_h = higham_nearest_corr(C_raw); C_e = eig_clip(C_raw)
print("min autovalor C_higham:", f"{np.linalg.eigvalsh(C_h).min():.2e}")
print("dist Frobenius Higham vs crudo:", round(np.linalg.norm(C_h - C_raw), 4))
print("dist Frobenius Higham vs verdadera:", round(np.linalg.norm(C_h - C_true), 4))
print("dist Frobenius eig-clip vs crudo:", round(np.linalg.norm(C_e - C_raw), 4))

# Cartera: PD, LGD y EAD heterogeneos
PD = rng.uniform(0.01, 0.05, n); LGD = np.full(n, 0.45); EAD = rng.uniform(1, 5, n)
a = LGD * EAD
thr = stats.norm.ppf(PD)

def loss_quantile(C, M=M, seed=1):
    r = np.random.default_rng(seed)
    w, V = np.linalg.eigh(C)
    Lf = V * np.sqrt(np.maximum(w, 0))  # factor espectral: valido para PSD singular
    Z = r.standard_normal((M, n)) @ Lf.T
    D = Z < thr
    loss = D @ a
    return np.quantile(loss, q), loss.mean()

for name, C in [("verdadera (referencia)", C_true), ("Higham", C_h), ("eig-clip", C_e)]:
    qv, mu = loss_quantile(C)
    print(f"{name:25s} E[L]={mu:8.4f}  q99.9={qv:8.4f}")
qH,_ = loss_quantile(C_h); qE,_ = loss_quantile(C_e); qT,_ = loss_quantile(C_true)
print(f"Diferencia cuantil Higham vs verdadera: {100*(qH-qT)/qT:+.2f} %")
print(f"Diferencia cuantil eig-clip vs Higham: {100*(qE-qH)/qH:+.2f} %")

# --- Iteracion: error de Monte Carlo y sensibilidad al nivel de ruido ---
print("\n# Error de Monte Carlo (5 semillas, M=300k)")
qs_true = [loss_quantile(C_true, seed=s)[0] for s in range(10, 15)]
qs_H = [loss_quantile(C_h, seed=s)[0] for s in range(10, 15)]
print(f"verdadera: media={np.mean(qs_true):.3f} sd={np.std(qs_true, ddof=1):.3f}")
print(f"Higham:    media={np.mean(qs_H):.3f} sd={np.std(qs_H, ddof=1):.3f}")
print(f"Diferencia relativa media Higham vs verdadera: {100*(np.mean(qs_H)-np.mean(qs_true))/np.mean(qs_true):+.2f} %")

print("\n# Sensibilidad al nivel de ruido pairwise")
for sd in [0.04, 0.08, 0.12]:
    rng2 = np.random.default_rng(777)
    nz = rng2.normal(0, sd, (n, n)); nz = (nz + nz.T) / 2; np.fill_diagonal(nz, 0)
    Cr = C_pair + nz; np.fill_diagonal(Cr, 1.0)
    neg = np.linalg.eigvalsh(Cr).min()
    Ch = higham_nearest_corr(Cr)
    qT = loss_quantile(C_true, seed=21)[0]; qH = loss_quantile(Ch, seed=21)[0]
    print(f"ruido sd={sd:.2f}  min_eig_crudo={neg:+.3f}  dist_F(Higham,crudo)={np.linalg.norm(Ch-Cr):.3f}  q99.9 Higham vs verdadera={100*(qH-qT)/qT:+.2f} %")

print("\n# Diagnostico: la distorsion viene del muestreo de la correlacion (T=60), no de la proyeccion")
print("min autovalor C_pair (muestral sin ruido):", f"{np.linalg.eigvalsh(C_pair).min():.2e}")
for T_obs in [60, 250, 1000]:
    Fo = rng.standard_normal((T_obs, 1))
    Xo = Fo @ b[None, :] + np.sqrt(1 - b**2)[None, :] * rng.standard_normal((T_obs, n))
    Cs = np.corrcoef(Xo, rowvar=False)
    qs = loss_quantile(Cs, seed=31)[0]; qT = loss_quantile(C_true, seed=31)[0]
    print(f"T={T_obs:5d}  min_eig={np.linalg.eigvalsh(Cs).min():+.3f}  q99.9 muestral vs verdadera={100*(qs-qT)/qT:+.2f} %")
