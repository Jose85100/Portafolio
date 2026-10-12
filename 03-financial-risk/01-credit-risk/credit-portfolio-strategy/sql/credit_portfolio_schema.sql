-- PostgreSQL 15+ | Esquema de referencia para una cartera de crédito.
-- No carga datos reales: las claves permiten conservar linaje y fecha de corte.
create schema if not exists credit_risk;

create table if not exists credit_risk.dim_counterparty (
    counterparty_id bigint generated always as identity primary key,
    counterparty_key text not null unique,
    sector_code text not null,
    rating_code text not null,
    valid_from date not null,
    valid_to date,
    check (valid_to is null or valid_to >= valid_from)
);

create table if not exists credit_risk.fact_exposure (
    as_of_date date not null,
    facility_key text not null,
    counterparty_id bigint not null references credit_risk.dim_counterparty(counterparty_id),
    ead numeric(20,2) not null check (ead >= 0),
    pd_annual numeric(9,8) not null check (pd_annual between 0 and 1),
    lgd_downturn numeric(9,8) not null check (lgd_downturn between 0 and 1),
    capital_charge numeric(9,8) not null check (capital_charge >= 0),
    primary key (as_of_date, facility_key)
);

create table if not exists credit_risk.risk_limit (
    limit_id bigint generated always as identity primary key,
    as_of_date date not null,
    metric_name text not null,
    dimension_name text not null,
    dimension_value text not null,
    limit_value numeric(12,8) not null check (limit_value > 0),
    amber_ratio numeric(5,4) not null default 0.85 check (amber_ratio between 0 and 1),
    unique (as_of_date, metric_name, dimension_name, dimension_value)
);

-- Concentración por sector para una fecha de corte parametrizable.
create or replace view credit_risk.v_sector_concentration as
with sector as (
    select e.as_of_date, c.sector_code, sum(e.ead) as ead
    from credit_risk.fact_exposure e join credit_risk.dim_counterparty c using (counterparty_id)
    group by 1, 2
), total as (
    select as_of_date, sum(ead) as ead_total from sector group by 1
)
select s.as_of_date, s.sector_code, s.ead / nullif(t.ead_total, 0) as share,
       sum(power(s.ead / nullif(t.ead_total, 0), 2)) over (partition by s.as_of_date) as hhi_sector
from sector s join total t using (as_of_date);

-- Semáforo trazable. Para producción, sustituir la métrica lateral por una
-- capa de métricas gobernada que cubra cada dimensión y métrica aprobada.
create or replace view credit_risk.v_limit_status as
select l.*, case when m.metric_value / l.limit_value >= 1 then 'ROJO'
                  when m.metric_value / l.limit_value >= l.amber_ratio then 'AMBAR'
                  else 'VERDE' end as status
from credit_risk.risk_limit l
join lateral (
    select case when l.dimension_name = 'sector' then
        (select max(share) from credit_risk.v_sector_concentration v
         where v.as_of_date = l.as_of_date and v.sector_code = l.dimension_value)
    end as metric_value
) m on m.metric_value is not null;
