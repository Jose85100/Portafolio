"""DDL smoke checks in SQLite; not a production database migration test."""
from pathlib import Path
import sqlite3
import unittest

class SchemaContractTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.execute('PRAGMA foreign_keys=ON')
        source=Path(__file__).resolve().parents[1]/'sql/ifrs9_laboratory_schema.sql'
        self.db.executescript(source.read_text())
    def tearDown(self):self.db.close()
    def test_zero_original_pd_and_negative_weight_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('INSERT INTO ifrs9_exposure_snapshot(as_of_date,loan_id,dpd,ead,undrawn,pd_12m,pd_origination,lgd,ccf) VALUES (?,?,?,?,?,?,?,?,?)',
                ('2026-10-18',1,0,100,0,.1,0.,.5,.2))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('INSERT INTO ifrs9_scenario_weight VALUES (?,?,?)',('2026-10-18','base',-1.))
    def test_recovery_reference_and_weight_audit(self):
        self.db.execute('INSERT INTO ifrs9_exposure_snapshot VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            ('2026-10-18',1,95,100,0,1.,.1,.5,.2,100,.1))
        self.db.execute('INSERT INTO ifrs9_scenario_weight VALUES (?,?,?)',('2026-10-18','base',1.))
        self.db.execute('INSERT INTO ifrs9_expected_recovery VALUES (?,?,?,?,?)',('2026-10-18',1,'base',2,60))
        self.assertEqual(self.db.execute('SELECT normalized FROM ifrs9_scenario_weight_audit').fetchone()[0],1)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('INSERT INTO ifrs9_expected_recovery VALUES (?,?,?,?,?)',('2026-10-18',2,'base',2,60))
