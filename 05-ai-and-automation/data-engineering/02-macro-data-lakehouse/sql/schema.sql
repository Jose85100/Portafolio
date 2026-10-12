-- PostgreSQL 15+: preserve releases and subsequent revisions.
CREATE SCHEMA IF NOT EXISTS macro;
CREATE TABLE IF NOT EXISTS macro.observations (
 series_id TEXT NOT NULL,
 observation_date DATE NOT NULL,
 released_at TIMESTAMPTZ NOT NULL,
 revision_number INTEGER NOT NULL CHECK (revision_number >= 0),
 value NUMERIC(24, 8) NOT NULL,
 source_url TEXT,
 PRIMARY KEY(series_id, observation_date, released_at, revision_number)
);
CREATE INDEX IF NOT EXISTS macro_vintage_lookup
 ON macro.observations(series_id, observation_date, released_at DESC);
-- Bind :series_id and :as_of_timestamp. Never filter by observation date alone.
-- SELECT observation_date, value FROM (
--   SELECT observation_date, value, ROW_NUMBER() OVER (
--     PARTITION BY observation_date ORDER BY released_at DESC, revision_number DESC
--   ) AS rn
--   FROM macro.observations
--   WHERE series_id = :series_id AND released_at <= :as_of_timestamp
-- ) x WHERE rn = 1 ORDER BY observation_date;
