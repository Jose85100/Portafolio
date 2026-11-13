import numpy as np, importlib.util, sys
spec = importlib.util.spec_from_file_location("s", "sim61_higham_psd.py")
# reutilizamos funciones sin re-ejecutar el script completo: definimos localmente
from scipy import stats
rng = np.random.default_rng(6161)
n=30; M=300_000; q=0.999
b = rng.uniform(0.3, 0.6, n)
C_true = np.outer(b,b); np.fill_diagonal(C_true,1.0)
PD = rng.uniform(0.01,0.05,n); LGD=np.full(n,0.45); EAD=rng.uniform(1,5,n); a=LGD*EAD; thr=stats.norm.ppf(PD)
def lq(C, seed):
    r=np.random.default_rng(seed); w,V=np.linalg.eigh(C); Lf=V*np.sqrt(np.maximum(w,0))
    Z=r.standard_normal((M,n))@Lf.T; return np.quantile((Z<thr)@a,q)
def higham(A,max_iter=500):
    Y=A.copy(); dS=np.zeros_like(A)
    for _ in range(max_iter):
        R=Y-dS; w,V=np.linalg.eigh(R); X_=(V*np.maximum(w,0))@V.T; dS=X_-R; Y=X_.copy(); np.fill_diagonal(Y,1.0)
    return Y
base=np.mean([lq(C_true,s) for s in range(40,44)])
print("q verdadera (media 4 semillas):", round(base,3))
# A) ruido aditivo simetrico de media cero sobre la verdadera, sin muestreo
for sd in [0.0, 0.04, 0.08]:
    vals=[]
    for k in range(3):
        rr=np.random.default_rng(900+k); nz=rr.normal(0,sd,(n,n)); nz=(nz+nz.T)/2; np.fill_diagonal(nz,0)
        C=C_true+nz; np.fill_diagonal(C,1.0)
        Ch=higham(C) if np.linalg.eigvalsh(C).min()<0 else C
        vals.append(np.mean([lq(Ch,s) for s in range(40,42)]))
    print(f"A) ruido sd={sd:.2f} (sin muestreo): q medio={np.mean(vals):.3f}  dif vs verdadera={100*(np.mean(vals)-base)/base:+.2f} %")
# B) error muestral puro, promedio de 5 muestras por T
for T_obs in [60,250,1000]:
    vals=[]
    for k in range(5):
        rr=np.random.default_rng(1000+k+T_obs)
        F=rr.standard_normal((T_obs,1)); X=F@b[None,:]+np.sqrt(1-b**2)[None,:]*rr.standard_normal((T_obs,n))
        Cs=np.corrcoef(X,rowvar=False)
        vals.append(np.mean([lq(Cs,s) for s in range(40,42)]))
    print(f"B) T={T_obs:5d} (muestral, 5 muestras): q medio={np.mean(vals):.3f}  dif={100*(np.mean(vals)-base)/base:+.2f} %  dispersion entre muestras={100*np.std(vals,ddof=1)/base:.2f} %")
