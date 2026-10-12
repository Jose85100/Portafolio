-- PostgreSQL 15+: point-in-time feature registry and forward targets.
CREATE SCHEMA IF NOT EXISTS quant;
CREATE TABLE IF NOT EXISTS quant.prices (
 asset_id TEXT NOT NULL,
 trading_date DATE NOT NULL,
 available_at TIMESTAMPTZ NOT NULL,
 close_price NUMERIC(22, 8) NOT NULL CHECK(close_price > 0),
 PRIMARY KEY(asset_id, trading_date, available_at)
);
CREATE TABLE IF NOT EXISTS quant.feature_snapshots (
 experiment_id TEXT NOT NULL,
 asset_id TEXT NOT NULL,
 feature_date DATE NOT NULL,
 feature_cutoff TIMESTAMPTZ NOT NULL,
 momentum_5 NUMERIC(20, 12),
 forward_return_1 NUMERIC(20, 12),
 label_end_date DATE,
 PRIMARY KEY(experiment_id, asset_id, feature_date),
 CHECK(label_end_date IS NULL OR label_end_date > feature_date)
);
-- For any feature date T, input rows must satisfy available_at <= feature_cutoff.
-- Targets are only usable after label_end_date and their actual release time.
CREATE INDEX IF NOT EXISTS price_pit_idx
 ON quant.prices(asset_id, trading_date, available_at DESC);
