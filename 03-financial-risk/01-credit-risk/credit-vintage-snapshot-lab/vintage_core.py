"""Cohort EVER >30 from account-month observations, with strict completeness.

A snapshot can miss delinquency between cuts; the intended business definition,
population, write-offs, MOB convention and weight must be approved by the owner.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

ACCOUNT = ['id_credito', 'id_comercio']
GROUP = ['corte_origen', *ACCOUNT]
REQUIRED = [*GROUP, 'id_cliente', 'mob', 'dias_mora']


def prepare_panel(panel: pd.DataFrame, *, fecha_asof=None) -> pd.DataFrame:
    missing = set(REQUIRED) - set(panel.columns)
    if missing:
        raise ValueError(f'Faltan columnas obligatorias: {sorted(missing)}')
    data = panel.copy()
    if data.empty:
        return data
    if data[GROUP + ['id_cliente', 'mob']].isna().any().any():
        raise ValueError('Hay llaves, cohorte, cliente o MOB nulos')
    for col in ['mob', 'dias_mora']:
        converted = pd.to_numeric(data[col], errors='coerce')
        if (data[col].notna() & converted.isna()).any():
            raise ValueError(f'{col} contiene valores no numéricos')
        data[col] = converted
    if ((data.mob < 0) | (data.mob % 1 != 0)).any():
        raise ValueError('MOB debe ser entero no negativo')
    if not np.isfinite(data.dias_mora.dropna()).all():
        raise ValueError('DPD no finito: revisar datos')
    if (data.dias_mora.dropna() < 0).any():
        raise ValueError('DPD negativo: revisar datos')
    if fecha_asof is not None:
        if 'fecha_disponibilidad' not in data:
            raise ValueError('Se requiere fecha_disponibilidad para un corte as-of')
        dates = pd.to_datetime(data.fecha_disponibilidad, errors='coerce')
        if dates.isna().any():
            raise ValueError('Fechas de disponibilidad ausentes o inválidas')
        data = data.loc[dates <= pd.Timestamp(fecha_asof)].copy()
    if data.duplicated(GROUP + ['mob']).any():
        raise ValueError('Más de una fila por cuenta, cohorte y MOB; reconciliar antes')
    if (data.groupby(ACCOUNT, dropna=False).corte_origen.nunique(dropna=False) > 1).any():
        raise ValueError('Una cuenta tiene múltiples cohortes')
    if (data.groupby(GROUP, dropna=False).id_cliente.nunique(dropna=False) > 1).any():
        raise ValueError('Una cuenta tiene múltiples clientes en una cohorte')
    return data


def build_vintage(panel: pd.DataFrame, horizonte: int = 3, *, incluir_mob0=False,
                  columna_saldo='saldo_capital_cop', fecha_asof=None):
    """Return (account, client) ledgers, retaining ineligible units.

    Account eligibility requires all monthly snapshots and DPD for MOB 1..h
    (also 0 if requested). Default weight is nonnegative saldo at h. Client
    eligibility requires every represented account in that client/cohort to be
    es_evaluable; a missing account outside the panel cannot be detected here.
    """
    if isinstance(horizonte, bool) or not isinstance(horizonte, int) or horizonte < 1:
        raise ValueError('El horizonte debe ser entero positivo')
    data = prepare_panel(panel, fecha_asof=fecha_asof)
    if columna_saldo not in data:
        raise ValueError(f'Falta columna de saldo: {columna_saldo}')
    if data.empty:
        empty_acc = pd.DataFrame(columns=GROUP + ['id_cliente', 'es_evaluable', 'evento_mora_mayor_30', 'saldo', 'saldo_valido', 'mobs_faltantes'])
        empty_client = pd.DataFrame(columns=['corte_origen', 'id_cliente', 'es_evaluable', 'evento_mora_mayor_30', 'saldo', 'saldo_valido', 'numero_cuentas'])
        return empty_acc, empty_client
    vals = pd.to_numeric(data[columna_saldo], errors='coerce')
    if (data[columna_saldo].notna() & vals.isna()).any():
        raise ValueError('Saldo no numérico: revisar datos')
    data['_balance'] = vals
    required_mobs = sorted(range(0 if incluir_mob0 else 1, horizonte + 1))
    # Vectorizado: una pasada por grupos en lugar de un bucle por cuenta.
    data['_k'] = data.groupby(GROUP, sort=False, dropna=False).ngroup()
    keys = data.drop_duplicates('_k').sort_values('_k')[GROUP + ['id_cliente']].reset_index(drop=True)
    considered = data[data.mob.isin(required_mobs)]
    seen = considered[considered.dias_mora.notna()]
    observed = (pd.crosstab(seen._k, seen.mob.astype(int)).reindex(index=keys.index, columns=required_mobs, fill_value=0) > 0)
    missing = ~observed.to_numpy()
    es_evaluable = ~missing.any(axis=1)
    mobs_faltantes = [','.join(str(m) for m, flag in zip(required_mobs, row) if flag) for row in missing]
    any_event = considered.dias_mora.gt(30).groupby(considered._k).any().reindex(keys.index, fill_value=False).to_numpy()
    at_h = data.loc[data.mob.eq(horizonte)].set_index('_k')._balance
    saldo = at_h.reindex(keys.index).astype(float).to_numpy()
    valid = es_evaluable & np.isfinite(saldo) & (np.nan_to_num(saldo, nan=-1) >= 0)
    accounts = keys.assign(es_evaluable=es_evaluable,
                           evento_mora_mayor_30=pd.Series([bool(e) if ok else pd.NA for e, ok in zip(any_event, es_evaluable)], dtype=object),
                           saldo=saldo, saldo_valido=valid, mobs_faltantes=mobs_faltantes)
    accounts = accounts[GROUP + ['id_cliente', 'es_evaluable', 'evento_mora_mayor_30', 'saldo', 'saldo_valido', 'mobs_faltantes']]
    grouped = accounts.assign(_e=any_event & es_evaluable, _s=np.where(valid, saldo, 0.0)).groupby(
        ['corte_origen', 'id_cliente'], sort=False, dropna=False)
    agg = grouped.agg(numero_cuentas=('es_evaluable', 'size'), es_evaluable=('es_evaluable', 'all'),
                      _all_valid=('saldo_valido', 'all'), _any=('_e', 'any'), _sum=('_s', 'sum')).reset_index()
    agg['es_evaluable'] = agg.es_evaluable.astype(bool)
    agg['evento_mora_mayor_30'] = pd.Series([bool(e) if ok else pd.NA for e, ok in zip(agg._any, agg.es_evaluable)], dtype=object)
    agg['saldo_valido'] = agg.es_evaluable & agg._all_valid.astype(bool)
    agg['saldo'] = np.where(agg.saldo_valido, agg._sum.astype(float), np.nan)
    clients = agg[['corte_origen', 'id_cliente', 'numero_cuentas', 'es_evaluable', 'evento_mora_mayor_30', 'saldo', 'saldo_valido']]
    return accounts, clients


def summarize_vintage(ledger: pd.DataFrame, *, group_columns=('corte_origen',)) -> pd.DataFrame:
    """Compute count and amount rates on separately disclosed denominators."""
    if not set(group_columns).issubset(ledger.columns):
        raise ValueError('No existen las columnas de segmentación solicitadas')
    records = []
    for key, g in ledger.groupby(list(group_columns), sort=True, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        matured = g.loc[g.es_evaluable.astype(bool)]
        weighted = matured.loc[matured.saldo_valido.astype(bool)]
        events = matured.evento_mora_mayor_30.astype("boolean").fillna(False).astype(bool)
        weighted_events = weighted.evento_mora_mayor_30.astype("boolean").fillna(False).astype(bool)
        denominator = float(weighted.saldo.sum())
        event_balance = float(weighted.loc[weighted_events, 'saldo'].sum())
        n = len(matured)
        records.append(dict(zip(group_columns, key)) | {
            'universo': len(g), 'no_evaluables': len(g)-n, 'n_maduros': n,
            'n_eventos': int(events.sum()), 'ever_numero': float(events.mean()) if n else np.nan,
            'n_saldo_valido': len(weighted), 'saldo_denominador': denominator,
            'saldo_eventos': event_balance, 'ever_saldo': event_balance / denominator if denominator > 0 else np.nan})
    return pd.DataFrame(records)
