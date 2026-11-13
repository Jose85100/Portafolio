"""Ejemplo didáctico ficticio; no es cartera ni representa desempeño real."""
import pandas as pd


def demo_panel():
    samples = [
        ('A', 'C01', '2024-01', [0, 31, 0], [100, 110, 120]),
        ('B', 'C02', '2024-01', [0, 30, 0], [100, 80, 80]),
        ('C', 'C03', '2024-01', [0, None, 0], [90, 90, 90]),
        ('D', 'C04', '2024-02', [0, 0, 45], [150, 140, 130]),
        ('E', 'C05', '2024-02', [0, 0, 0], [80, 75, 70]),
        ('F', 'C06', '2024-02', [0, 0, 0], [40, 45, None]),
    ]
    rows = []
    for loan, client, cohort, dpds, balances in samples:
        start = pd.Period(cohort, freq='M')
        for mob, (dias_mora, bal) in enumerate(zip(dpds, balances), 1):
            date = (start + mob).end_time.normalize()
            rows.append({'id_credito': loan, 'id_comercio': 'M1', 'id_cliente': client,
                         'corte_origen': cohort, 'mob': mob, 'dias_mora': dias_mora,
                         'saldo_capital_cop': bal, 'fecha_corte': date,
                         'fecha_disponibilidad': date})
    return pd.DataFrame(rows)
