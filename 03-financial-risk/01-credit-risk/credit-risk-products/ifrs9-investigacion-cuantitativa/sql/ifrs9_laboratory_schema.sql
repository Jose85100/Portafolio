-- Esquema mínimo de laboratorio: sintético, sin PII y no apto para producción.
CREATE TABLE ifrs9_exposure_snapshot (
  as_of_date date NOT NULL, loan_id bigint NOT NULL, dpd integer NOT NULL CHECK (dpd >= 0),
  ead numeric(18,2) NOT NULL CHECK (ead >= 0), undrawn numeric(18,2) NOT NULL CHECK (undrawn >= 0),
  pd_12m numeric(8,6) NOT NULL CHECK (pd_12m BETWEEN 0 AND 1),
  pd_origination numeric(8,6) NOT NULL CHECK (pd_origination > 0 AND pd_origination <= 1),
  lgd numeric(8,6) NOT NULL CHECK (lgd BETWEEN 0 AND 1),
  ccf numeric(8,6) NOT NULL CHECK (ccf BETWEEN 0 AND 1),
  gross_carrying_amount numeric(18,2) CHECK (gross_carrying_amount >= 0),
  effective_interest_rate numeric(12,8) CHECK (effective_interest_rate > -1),
  CHECK (pd_12m < 1 OR dpd >= 90), PRIMARY KEY (as_of_date, loan_id)
);
CREATE TABLE ifrs9_scenario_weight (as_of_date date NOT NULL, scenario text NOT NULL CHECK (scenario IN ('base','adverso','severo')), weight numeric(6,5) NOT NULL CHECK (weight BETWEEN 0 AND 1), PRIMARY KEY (as_of_date, scenario));
CREATE VIEW ifrs9_stage_audit AS
SELECT as_of_date, loan_id, CASE WHEN dpd >= 90 THEN 3 WHEN dpd >= 30 OR pd_12m / NULLIF(pd_origination, 0) >= 2 THEN 2 ELSE 1 END AS stage
FROM ifrs9_exposure_snapshot;


-- These normalized tables document the interface; the Python demo does not read SQL.
-- Supplied expected net recovery flows, for funded non-POCI examples only.
CREATE TABLE ifrs9_expected_recovery (
  as_of_date date NOT NULL, loan_id bigint NOT NULL,
  scenario text NOT NULL CHECK (scenario IN ('base','adverso','severo')),
  recovery_years numeric(10,6) NOT NULL CHECK (recovery_years >= 0),
  expected_net_recovery numeric(18,2) NOT NULL CHECK (expected_net_recovery >= 0),
  PRIMARY KEY (as_of_date,loan_id,scenario,recovery_years),
  FOREIGN KEY (as_of_date,loan_id) REFERENCES ifrs9_exposure_snapshot(as_of_date,loan_id),
  FOREIGN KEY (as_of_date,scenario) REFERENCES ifrs9_scenario_weight(as_of_date,scenario)
);
-- Aggregate weight and missing recovery coverage require validation beyond row CHECKs.
CREATE VIEW ifrs9_scenario_weight_audit AS
SELECT as_of_date, SUM(weight) AS total_weight,
       CASE WHEN ABS(SUM(weight)-1) <= 0.000000000001 THEN 1 ELSE 0 END AS normalized
FROM ifrs9_scenario_weight GROUP BY as_of_date;
