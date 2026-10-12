-- PostgreSQL 15+ | Sandbox for synthetic credit-risk demonstrations only.
-- Never load PII, production exposures, credentials, or decision outcomes here.
BEGIN;

CREATE SCHEMA IF NOT EXISTS credit_risk_sandbox;
SET LOCAL search_path = credit_risk_sandbox, public;

CREATE TABLE dataset_manifest (
  dataset_version text PRIMARY KEY,
  generated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  generator_name text NOT NULL,
  random_seed bigint NOT NULL,
  sha256 char(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
  synthetic boolean NOT NULL DEFAULT true CHECK (synthetic),
  record_count integer NOT NULL CHECK (record_count >= 0),
  notes text NOT NULL DEFAULT ''
);

CREATE TABLE segment (
  segment_code text PRIMARY KEY CHECK (segment_code ~ '^[A-Z0-9_]{2,32}$'),
  display_name text NOT NULL,
  active boolean NOT NULL DEFAULT true
);

CREATE TABLE exposure_snapshot (
  exposure_id uuid NOT NULL,
  as_of_date date NOT NULL,
  dataset_version text NOT NULL REFERENCES dataset_manifest(dataset_version),
  segment_code text NOT NULL REFERENCES segment(segment_code),
  currency_code char(3) NOT NULL DEFAULT 'COP' CHECK (currency_code ~ '^[A-Z]{3}$'),
  ead_cop numeric(20,2) NOT NULL CHECK (ead_cop >= 0),
  days_past_due integer NOT NULL CHECK (days_past_due >= 0),
  origination_date date NOT NULL,
  synthetic boolean NOT NULL DEFAULT true CHECK (synthetic),
  PRIMARY KEY (exposure_id, as_of_date, dataset_version),
  CHECK (origination_date <= as_of_date)
);
CREATE INDEX exposure_snapshot_lookup_idx
  ON exposure_snapshot (dataset_version, as_of_date, segment_code);

CREATE TABLE model_registry (
  model_version text PRIMARY KEY,
  model_name text NOT NULL,
  contract_version text NOT NULL,
  code_sha256 char(64) NOT NULL CHECK (code_sha256 ~ '^[0-9a-f]{64}$'),
  approved_for_production boolean NOT NULL DEFAULT false CHECK (NOT approved_for_production),
  synthetic_only boolean NOT NULL DEFAULT true CHECK (synthetic_only),
  registered_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  UNIQUE (model_name, model_version)
);

CREATE TABLE model_run (
  run_id uuid PRIMARY KEY,
  dataset_version text NOT NULL REFERENCES dataset_manifest(dataset_version),
  model_version text NOT NULL REFERENCES model_registry(model_version),
  horizon_months smallint NOT NULL CHECK (horizon_months BETWEEN 1 AND 360),
  executed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  execution_ref text NOT NULL CHECK (length(execution_ref) BETWEEN 8 AND 200),
  synthetic boolean NOT NULL DEFAULT true CHECK (synthetic),
  run_status text NOT NULL CHECK (run_status IN ('accepted','rejected','quarantined'))
);

CREATE TABLE risk_estimate (
  run_id uuid NOT NULL REFERENCES model_run(run_id),
  exposure_id uuid NOT NULL,
  as_of_date date NOT NULL,
  dataset_version text NOT NULL,
  pd_12m numeric(9,8) NOT NULL CHECK (pd_12m BETWEEN 0 AND 1),
  lgd_downturn numeric(9,8) NOT NULL CHECK (lgd_downturn BETWEEN 0 AND 1),
  ead_cop numeric(20,2) NOT NULL CHECK (ead_cop >= 0),
  expected_loss_cop numeric(20,2) NOT NULL CHECK (expected_loss_cop >= 0),
  PRIMARY KEY (run_id, exposure_id, as_of_date, dataset_version),
  FOREIGN KEY (exposure_id, as_of_date, dataset_version)
    REFERENCES exposure_snapshot(exposure_id, as_of_date, dataset_version),
  CHECK (abs(expected_loss_cop - round(pd_12m * lgd_downturn * ead_cop, 2)) <= 0.01)
);

CREATE TABLE audit_event (
  event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  actor text NOT NULL DEFAULT current_user,
  action text NOT NULL CHECK (action IN ('INSERT','UPDATE','DELETE')),
  entity_name text NOT NULL,
  entity_key jsonb NOT NULL,
  before_state jsonb,
  after_state jsonb,
  synthetic boolean NOT NULL DEFAULT true CHECK (synthetic)
);

CREATE OR REPLACE FUNCTION audit_row_change()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
  key_value jsonb;
BEGIN
  key_value := CASE TG_OP
    WHEN 'DELETE' THEN jsonb_build_object('row', to_jsonb(OLD))
    ELSE jsonb_build_object('row', to_jsonb(NEW))
  END;
  INSERT INTO audit_event(action, entity_name, entity_key, before_state, after_state)
  VALUES (TG_OP, TG_TABLE_NAME, key_value,
          CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE to_jsonb(OLD) END,
          CASE WHEN TG_OP = 'DELETE' THEN NULL ELSE to_jsonb(NEW) END);
  RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER risk_estimate_audit_trg
AFTER INSERT OR UPDATE OR DELETE ON risk_estimate
FOR EACH ROW EXECUTE FUNCTION audit_row_change();

-- Quality and audit views: empty result sets represent no exception.
CREATE OR REPLACE VIEW v_data_quality_exceptions AS
SELECT 'MANIFEST_COUNT_MISMATCH' AS control_name, e.dataset_version,
       count(*)::text AS observed_value
FROM exposure_snapshot e JOIN dataset_manifest m USING (dataset_version)
GROUP BY e.dataset_version
HAVING count(*) <> max(m.record_count)
UNION ALL
SELECT 'ESTIMATE_WITH_NON_ACCEPTED_RUN', r.dataset_version, count(*)::text
FROM risk_estimate r JOIN model_run mr USING (run_id)
WHERE mr.run_status <> 'accepted'
GROUP BY r.dataset_version;

CREATE OR REPLACE VIEW v_run_audit AS
SELECT mr.run_id, mr.executed_at, mr.dataset_version, mr.model_version,
       mr.horizon_months, mr.run_status, count(re.exposure_id) AS estimate_count,
       coalesce(sum(re.expected_loss_cop), 0)::numeric(20,2) AS expected_loss_cop
FROM model_run mr
LEFT JOIN risk_estimate re USING (run_id)
GROUP BY mr.run_id, mr.executed_at, mr.dataset_version, mr.model_version,
         mr.horizon_months, mr.run_status;

COMMENT ON SCHEMA credit_risk_sandbox IS 'Synthetic-only educational credit-risk sandbox.';
COMMENT ON VIEW v_data_quality_exceptions IS 'Exceptions requiring investigation; intended to return zero rows.';
COMMIT;
