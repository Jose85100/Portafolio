-- Esquema mínimo de laboratorio: sintético, sin PII y no apto para producción.
CREATE TABLE ifrs9_exposure_snapshot (
  as_of_date date NOT NULL, loan_id bigint NOT NULL, dpd integer NOT NULL CHECK (dpd >= 0),
  ead numeric(18,2) NOT NULL CHECK (ead >= 0), undrawn numeric(18,2) NOT NULL CHECK (undrawn >= 0),
  pd_12m numeric(8,6) NOT NULL CHECK (pd_12m BETWEEN 0 AND 1),
  pd_origination numeric(8,6) NOT NULL CHECK (pd_origination BETWEEN 0 AND 1),
  lgd numeric(8,6) NOT NULL CHECK (lgd BETWEEN 0 AND 1), PRIMARY KEY (as_of_date, loan_id)
);
CREATE TABLE ifrs9_scenario_weight (as_of_date date NOT NULL, scenario text NOT NULL CHECK (scenario IN ('base','adverso','severo')), weight numeric(6,5) NOT NULL CHECK (weight BETWEEN 0 AND 1), PRIMARY KEY (as_of_date, scenario));
CREATE VIEW ifrs9_stage_audit AS
SELECT as_of_date, loan_id, CASE WHEN dpd >= 90 THEN 3 WHEN dpd >= 30 OR pd_12m / NULLIF(pd_origination, 0) >= 2 THEN 2 ELSE 1 END AS stage
FROM ifrs9_exposure_snapshot;
