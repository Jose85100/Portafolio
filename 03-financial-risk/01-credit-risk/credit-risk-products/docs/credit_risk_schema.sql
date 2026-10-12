-- Reference analytical schema for synthetic credit-risk exercises.
-- PostgreSQL 14+; demonstrative only. No customer PII or production policies.

CREATE SCHEMA IF NOT EXISTS credit_risk_lab;
SET search_path TO credit_risk_lab;

CREATE TABLE product_dim (
  product_code text PRIMARY KEY,
  product_name text NOT NULL,
  active_flag boolean NOT NULL DEFAULT true
);

CREATE TABLE vintage_cohort (
  vintage_id text PRIMARY KEY,
  origination_month date NOT NULL,
  CHECK (origination_month = date_trunc('month', origination_month)::date)
);

CREATE TABLE credit_snapshot (
  account_id text NOT NULL,
  as_of_date date NOT NULL,
  snapshot_id text NOT NULL,
  data_version text NOT NULL,
  product_code text NOT NULL REFERENCES product_dim(product_code),
  vintage_id text REFERENCES vintage_cohort(vintage_id),
  monthly_income numeric(18,2),
  utilization numeric(8,6),
  days_past_due integer NOT NULL DEFAULT 0,
  pd_12m numeric(8,6),
  lgd numeric(8,6),
  ead numeric(18,2) NOT NULL,
  PRIMARY KEY (account_id, as_of_date),
  CHECK (monthly_income IS NULL OR monthly_income >= 0),
  CHECK (utilization IS NULL OR utilization BETWEEN 0 AND 1.2),
  CHECK (days_past_due >= 0),
  CHECK (pd_12m IS NULL OR pd_12m BETWEEN 0 AND 1),
  CHECK (lgd IS NULL OR lgd BETWEEN 0 AND 1),
  CHECK (ead >= 0)
);

CREATE TABLE delinquency_transition (
  account_id text NOT NULL,
  observation_month date NOT NULL,
  state_from text NOT NULL CHECK (state_from IN ('al_dia','mora_30','mora_60','mora_90','default')),
  state_to text NOT NULL CHECK (state_to IN ('al_dia','mora_30','mora_60','mora_90','default')),
  PRIMARY KEY (account_id, observation_month),
  CHECK (state_from <> 'default' OR state_to = 'default')
);

CREATE TABLE default_event (
  account_id text PRIMARY KEY,
  default_date date NOT NULL,
  loss_amount numeric(18,2) CHECK (loss_amount IS NULL OR loss_amount >= 0)
);

CREATE INDEX credit_snapshot_as_of_product_idx ON credit_snapshot (as_of_date, product_code);
CREATE INDEX delinquency_transition_month_idx ON delinquency_transition (observation_month, state_from);

-- Example: maximum-likelihood roll-rate counts at a selected month.
-- SELECT state_from, state_to, count(*) AS transitions,
--   count(*)::numeric / sum(count(*)) OVER (PARTITION BY state_from) AS p_hat
-- FROM delinquency_transition
-- WHERE observation_month = DATE '2026-01-01'
-- GROUP BY state_from, state_to;
