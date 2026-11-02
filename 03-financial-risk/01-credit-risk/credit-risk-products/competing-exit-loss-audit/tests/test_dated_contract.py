import unittest
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta, timezone

from src.dated_contract import (
    DatedInterval,
    SourceStamp,
    convert_rate,
    denominator,
    project_dated,
)
from src.term_structure import project_term_structure


class DatedTests(unittest.TestCase):
    def setUp(self):
        self.valuation=datetime(2024,2,28,12,tzinfo=UTC)
        self.sources=[SourceStamp(role,'synthetic-v1','synthetic://scenario',self.valuation)
                      for role in ('ead','hazards','discount')]
        self.items=[DatedInterval(date(2024,2,28),date(2024,3,1),.24,1.2,100.,100.,.06),
                    DatedInterval(date(2024,3,1),date(2025,2,28),.24,1.2,20.,20.,.06)]

    def test_leap_and_direct_oracle(self):
        r=project_dated(self.items,self.sources,self.valuation,'ACT/365F')
        direct=project_term_structure([2/365,364/365],[.24]*2,[1.2]*2,[100.,20.],[100.,20.],[.06]*2)
        self.assertAlmostEqual(r.exact_loss,direct.exact_loss,places=14)

    def test_unit_conversion_invariance(self):
        self.assertAlmostEqual(convert_rate(1e306,'ACT/365F','ACT/360')/1e306,360/365)
        with self.assertRaises(ValueError):convert_rate(1.7976931348623157e308,'ACT/360','ACT/365F')
        a=project_dated(self.items,self.sources,self.valuation,'ACT/365F')
        scale=lambda v:convert_rate(v,'ACT/365F','ACT/360')
        adjusted=[replace(i,default_hazard=scale(i.default_hazard),prepay_hazard=scale(i.prepay_hazard),discount_force=scale(i.discount_force)) for i in self.items]
        b=project_dated(adjusted,self.sources,self.valuation,'ACT/360')
        self.assertAlmostEqual(a.exact_loss,b.exact_loss,places=13)
        naive=project_dated(self.items,self.sources,self.valuation,'ACT/360')
        self.assertGreater(abs(naive.exact_loss-a.exact_loss),.001)

    def test_future_availability_not_future_forecast(self):
        project_dated(self.items,self.sources,self.valuation,'ACT/365F')
        future=[replace(self.sources[0],available_at=self.valuation+timedelta(microseconds=1)),*self.sources[1:]]
        with self.assertRaisesRegex(ValueError,'not available'):
            project_dated(self.items,future,self.valuation,'ACT/365F')
        offset=timezone(timedelta(hours=-5))
        same=[replace(i,available_at=self.valuation.astimezone(offset)) for i in self.sources]
        self.assertEqual(project_dated(self.items,same,self.valuation,'ACT/365F'),project_dated(self.items,self.sources,self.valuation,'ACT/365F'))

    def test_invalid_provenance(self):
        for rate in (-1.,float('inf'),float('nan')):
            with self.assertRaises(ValueError):convert_rate(rate,'ACT/365F','ACT/360')
        variants=[self.sources[:2],[self.sources[0]]*3,
                  [replace(self.sources[0],uri=''),*self.sources[1:]],
                  [replace(self.sources[0],available_at=datetime(2024,2,28)),*self.sources[1:]]]
        for sources in variants:
            with self.assertRaises(ValueError):project_dated(self.items,sources,self.valuation,'ACT/365F')
        with self.assertRaises(ValueError):project_dated(self.items,self.sources,datetime(2024,2,28),'ACT/365F')

    def test_invalid_calendar(self):
        variants=[[],[replace(self.items[0],end=self.items[0].start)],
                  [self.items[0],replace(self.items[1],start=date(2024,3,2))],
                  [replace(self.items[0],start=date(2024,2,27))],
                  [replace(self.items[0],end=datetime(2024,3,1))]]
        for items in variants:
            with self.assertRaises(ValueError):project_dated(items,self.sources,self.valuation,'ACT/365F')
        with self.assertRaises(ValueError):denominator('ACT/ACT')
