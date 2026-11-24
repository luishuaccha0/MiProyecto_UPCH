import unittest
from datos_app import cargar
class DatosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a,cls.p,cls.r,cls.h,cls.s,cls.c,cls.m,cls.raw=cargar()
    def test_historico(self):
        self.assertEqual(self.a.arboles.sum(),1424926)
        self.assertEqual(self.a.anio.nunique(),7)
        self.assertEqual(self.r.distrito.nunique(),42)
    def test_excel(self):
        self.assertEqual(len(self.h),2064)
        self.assertEqual(len(self.s),48)
        self.assertEqual(self.h.distrito.nunique(),43)
        self.assertTrue(self.h.groupby(['anio','mes']).arboles.sum().equals(self.s.set_index(['anio','mes']).arboles))
        self.assertTrue(self.h[self.h.anio==2023].captura.isna().all())
    def test_diferencias(self):
        totals=self.c.groupby('anio')[['csv_programa','excel','csv_distritos']].sum(min_count=1)
        self.assertEqual(totals.loc[2026,'csv_distritos'],231231)
        self.assertEqual(totals.loc[2026,'csv_programa'],231221)
        self.assertEqual(totals.loc[2026,'excel'],216339)
        self.assertEqual(totals.loc[2024,'excel'],102989)
        self.assertEqual(totals.loc[2025,'excel'],581160)
    def test_vacios(self):
        self.assertTrue(self.p[(self.p.anio==2026)&(self.p.mes>=10)].arboles.isna().all())
        self.assertTrue(self.r[(self.r.anio==2026)&(self.r.mes>=10)].arboles.isna().all())
        self.assertEqual(self.s[(self.s.anio==2026)&(self.s.mes==9)].arboles.iloc[0],0)
if __name__=='__main__':unittest.main()
