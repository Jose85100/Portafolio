-- PostgreSQL reference queries: adapt table names / indexes to approved schemas.
-- No customer data. Example conceptual tables:
-- loan_snapshot(loan_id, as_of_date, balance, snapshot_ingested_at)
-- default_event(loan_id, default_date, event_recorded_at)
-- model_score(loan_id, score_as_of_date, pd, model_version)
-- WARNING: label maturity, right censoring and late-arriving data must be handled explicitly.

-- Point-in-time loan features. Never use snapshots recorded after the scoring date.
WITH dated AS (
    SELECT s.loan_id, s.as_of_date, s.balance, s.snapshot_ingested_at,
           ROW_NUMBER() OVER (
               PARTITION BY s.loan_id
               ORDER BY s.as_of_date DESC, s.snapshot_ingested_at DESC
           ) AS rn
    FROM loan_snapshot s
    WHERE s.as_of_date <= :scoring_date
      AND s.snapshot_ingested_at <= :scoring_timestamp
)
SELECT loan_id, as_of_date, balance
FROM dated WHERE rn = 1;

-- Performance cohort after the target fully matures (12 months).
-- A subsequent data-quality check must flag censored or incomplete cohorts.
SELECT model_version, date_trunc('month', score_as_of_date) AS vintage,
       COUNT(*) AS count_scored,
       AVG(pd) AS mean_pd
FROM model_score
WHERE score_as_of_date <= :last_fully_matured_scoring_date
GROUP BY model_version, date_trunc('month', score_as_of_date)
ORDER BY model_version, vintage;
