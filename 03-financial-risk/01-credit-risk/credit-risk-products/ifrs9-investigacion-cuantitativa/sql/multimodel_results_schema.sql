-- Reference persistence design; Python returns DataFrames, not a live SQL adapter.
PRAGMA foreign_keys = ON;
CREATE TABLE model_version (
    model_id TEXT NOT NULL,
    version TEXT NOT NULL,
    component TEXT NOT NULL CHECK (component IN ('PD','LGD','EAD','POLICY')),
    code_sha256 TEXT NOT NULL CHECK (length(code_sha256)=64),
    parameters_json TEXT NOT NULL,
    PRIMARY KEY (model_id,version)
);
CREATE TABLE ecl_run (
    run_id TEXT PRIMARY KEY,
    reporting_date TEXT NOT NULL,
    data_version TEXT NOT NULL,
    pd_id TEXT NOT NULL, pd_version TEXT NOT NULL,
    lgd_id TEXT NOT NULL, lgd_version TEXT NOT NULL,
    ead_id TEXT NOT NULL, ead_version TEXT NOT NULL,
    policy_id TEXT NOT NULL, policy_version TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('research','validated','approved','retired')),
    FOREIGN KEY(pd_id,pd_version) REFERENCES model_version(model_id,version),
    FOREIGN KEY(lgd_id,lgd_version) REFERENCES model_version(model_id,version),
    FOREIGN KEY(ead_id,ead_version) REFERENCES model_version(model_id,version),
    FOREIGN KEY(policy_id,policy_version) REFERENCES model_version(model_id,version)
);
CREATE TABLE ecl_scenario (
    run_id TEXT NOT NULL REFERENCES ecl_run(run_id),
    scenario_id TEXT NOT NULL,
    weight REAL NOT NULL CHECK (weight >= 0 AND weight <= 1),
    PRIMARY KEY(run_id,scenario_id)
);
CREATE TABLE ecl_result (
    run_id TEXT NOT NULL,
    loan_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    stage INTEGER NOT NULL CHECK (stage IN (1,2,3)),
    basis TEXT NOT NULL CHECK(basis IN ('monthly_components','funded_recovery_cashflows')),
    ecl REAL NOT NULL CHECK(ecl >= 0),
    PRIMARY KEY(run_id,loan_id,scenario_id),
    CHECK((stage=3 AND basis='funded_recovery_cashflows') OR (stage IN (1,2) AND basis='monthly_components')),
    FOREIGN KEY(run_id,scenario_id) REFERENCES ecl_scenario(run_id,scenario_id)
);
-- Multirow sum constraints require a publish-time transaction check, not a CHECK.
CREATE VIEW scenario_weight_audit AS
SELECT run_id,SUM(weight) AS weight_sum,ABS(SUM(weight)-1.0)<=1e-12 AS valid
FROM ecl_scenario GROUP BY run_id;
-- Component type matches and numeric finiteness also require adapter validation;
-- this DDL alone does not authorize approval or prevent every malformed import.
