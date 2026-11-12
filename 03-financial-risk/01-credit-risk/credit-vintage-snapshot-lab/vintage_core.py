"""Cohort EVER >30 from account-month observations, with strict completeness.

A snapshot can miss delinquency between cuts; the intended business definition,
population, write-offs, MOB convention and weight must be approved by the owner.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

ACCOUNT = ['loan_key', 'merchant_key']
GROUP = ['corte_origen', *ACCOUNT]
REQUIRED = [*GROUP, 'client_id', 'mob', 'dpd']


def prepare_panel(panel: pd.DataFrame, *, as_of=None) -> pd.DataFrame:
    missing = set(REQUIRED) - set(panel.columns)
    if missing:
        raise ValueError(f'Faltan columnas obligatorias: {sorted(missing)}')
    data = panel.copy()
    if data.empty:
        return data
    if data[GROUP + ['client_id', 'mob']].isna().any().any():
        raise ValueError('Hay llaves, cohorte, cliente o MOB nulos')
    for col in ['mob', 'dpd']:
        converted = pd.to_numeric(data[col], errors='coerce')
        if (data[col].notna() & converted.isna()).any():
            raise ValueError(f'{col} contiene valores no numéricos')
        data[col] = converted
    if ((data.mob < 0) | (data.mob % 1 != 0)).any():
        raise ValueError('MOB debe ser entero no negativo')
    if not np.isfinite(data.dpd.dropna()).all():
        raise ValueError('DPD no finito: revisar datos')
    if (data.dpd.dropna() < 0).any():
        raise ValueError('DPD negativo: revisar datos')
    if as_of is not None:
        if 'fecha_disponibilidad' not in data:
            raise ValueError('Se requiere fecha_disponibilidad para un corte as-of')
        dates = pd.to_datetime(data.fecha_disponibilidad, errors='coerce')
        if dates.isna().any():
            raise ValueError('Fechas de disponibilidad ausentes o inválidas')
        data = data.loc[dates <= pd.Timestamp(as_of)].copy()
    if data.duplicated(GROUP + ['mob']).any():
        raise ValueError('Más de una fila por cuenta, cohorte y MOB; reconciliar antes')
    if (data.groupby(ACCOUNT, dropna=False).corte_origen.nunique(dropna=False) > 1).any():
        raise ValueError('Una cuenta tiene múltiples cohortes')
    if (data.groupby(GROUP, dropna=False).client_id.nunique(dropna=False) > 1).any():
        raise ValueError('Una cuenta tiene múltiples clientes en una cohorte')
    return data


def build_vintage(panel: pd.DataFrame, horizon: int = 3, *, include_mob0=False,
                  balance_column='saldo_capital_cop', as_of=None):
    """Return (account, client) ledgers, retaining ineligible units.

    Account eligibility requires all monthly snapshots and DPD for MOB 1..h
    (also 0 if requested). Default weight is nonnegative balance at h. Client
    eligibility requires every represented account in that client/cohort to be
    eligible; a missing account outside the panel cannot be detected here.
    """
    if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon < 1:
        raise ValueError('El horizonte debe ser entero positivo')
    data = prepare_panel(panel, as_of=as_of)
    if balance_column not in data:
        raise ValueError(f'Falta columna de saldo: {balance_column}')
    if data.empty:
        empty_acc = pd.DataFrame(columns=GROUP + ['client_id', 'eligible', 'ever30', 'balance', 'balance_valid', 'missing_mobs'])
        empty_client = pd.DataFrame(columns=['corte_origen', 'client_id', 'eligible', 'ever30', 'balance', 'balance_valid', 'n_accounts'])
        return empty_acc, empty_client
    vals = pd.to_numeric(data[balance_column], errors='coerce')
    if (data[balance_column].notna() & vals.isna()).any():
        raise ValueError('Saldo no numérico: revisar datos')
    data['_balance'] = vals
    required_mobs = set(range(0 if include_mob0 else 1, horizon + 1))
    rows = []
    for key, g in data.groupby(GROUP, sort=False, dropna=False):
        considered = g[g.mob.isin(required_mobs)]
        observed = set(considered.loc[considered.dpd.notna(), 'mob'].astype(int))
        missing_mobs = sorted(required_mobs - observed)
        eligible = not missing_mobs
        h = g.loc[g.mob.eq(horizon), '_balance']
        balance = float(h.iloc[0]) if len(h) and pd.notna(h.iloc[0]) else np.nan
        valid = eligible and np.isfinite(balance) and balance >= 0
        event = bool((considered.dpd > 30).any()) if eligible else pd.NA
        rows.append(dict(zip(GROUP, key)) | {'client_id': g.client_id.iloc[0], 'eligible': eligible,
                     'ever30': event, 'balance': balance, 'balance_valid': valid,
                     'missing_mobs': ','.join(map(str, missing_mobs))})
    accounts = pd.DataFrame(rows)
    clients = []
    for (cohort, client), g in accounts.groupby(['corte_origen', 'client_id'], dropna=False, sort=False):
        eligible = bool(g.eligible.all())
        valid = eligible and bool(g.balance_valid.all())
        clients.append({'corte_origen': cohort, 'client_id': client, 'n_accounts': len(g),
                        'eligible': eligible, 'ever30': bool(g.ever30.any()) if eligible else pd.NA,
                        'balance': float(g.balance.sum()) if valid else np.nan, 'balance_valid': valid})
    return accounts, pd.DataFrame(clients)


def summarize_vintage(ledger: pd.DataFrame, *, group_columns=('corte_origen',)) -> pd.DataFrame:
    """Compute count and amount rates on separately disclosed denominators."""
    if not set(group_columns).issubset(ledger.columns):
        raise ValueError('No existen las columnas de segmentación solicitadas')
    records = []
    for key, g in ledger.groupby(list(group_columns), sort=True, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        matured = g.loc[g.eligible.astype(bool)]
        weighted = matured.loc[matured.balance_valid.astype(bool)]
        events = matured.ever30.astype("boolean").fillna(False).astype(bool)
        weighted_events = weighted.ever30.astype("boolean").fillna(False).astype(bool)
        denominator = float(weighted.balance.sum())
        event_balance = float(weighted.loc[weighted_events, 'balance'].sum())
        n = len(matured)
        records.append(dict(zip(group_columns, key)) | {
            'universo': len(g), 'no_evaluables': len(g)-n, 'n_maduros': n,
            'n_eventos': int(events.sum()), 'ever_numero': float(events.mean()) if n else np.nan,
            'n_saldo_valido': len(weighted), 'saldo_denominador': denominator,
            'saldo_eventos': event_balance, 'ever_saldo': event_balance / denominator if denominator > 0 else np.nan})
    return pd.DataFrame(records)
