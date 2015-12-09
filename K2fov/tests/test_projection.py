
import unittest
from .. import projection as proj

#$Id: test_projection.py 40 2014-02-18 20:59:31Z fergalm $
#$URL: svn+ssh://fergalm@svn.code.sf.net/p/keplertwowheel/code/py/test/test_projection.py $#


class TestGnomic(unittest.TestCase):
    def testSkyToPixAtOrigin(self):

        """Test that increasing ra causes a decreasing pixel position,
        but that an increasing dec causes an increasing pixel position"""

        arcsec = 1/3600.
        p = proj.Gnomic(0,0)

        x, y = p.skyToPix(0,0)
        msg = "Expected 0,0, got %.3f %.3f" %(x, y)
        self.assertAlmostEqual(0, x[0], 10, msg)
        self.assertAlmostEqual(0, y[0], 10, msg)

        x, y = p.skyToPix(arcsec,0)
        msg = "Expected -,0, got %.6f %.6f" %(x, y)
        self.assertTrue(x[0]<0, msg)
        self.assertAlmostEqual(0, y[0], 10, msg)

        x, y = p.skyToPix(-arcsec,0)
        msg = "Expected +,0, got %.6f %.6f" %(x, y)
        self.assertTrue(x[0]>0, msg)
        self.assertAlmostEqual(0, y[0], 10, msg)

        x, y = p.skyToPix(0, arcsec)
        msg = "Expected 0,+, got %.6f %.6f" %(x, y)
        self.assertAlmostEqual(0, x[0], 10, msg)
        self.assertTrue(y[0]>0, msg)

        x, y = p.skyToPix(0, -arcsec)
        msg = "Expected 0,-, got %.6f %.6f" %(x, y)
        self.assertAlmostEqual(0, x[0], 10, msg)
        self.assertTrue(y[0]<0, msg)

        x, y = p.skyToPix(arcsec, arcsec)
        msg = "Expected -,+, got %.6f %.6f" %(x, y)
        self.assertTrue(x[0]<0, msg)
        self.assertTrue(y[0]>0, msg)

        x, y = p.skyToPix(arcsec, -arcsec)
        msg = "Expected -,-, got %.3e %.3e" %(x, y)
        self.assertTrue(x[0]<0, msg)
        self.assertTrue(y[0]<0, msg)


    def testSkyToPixAtPosition(self):
        arcsec = 1/3600.
        a = 36.
        d = 14.
        p = proj.Gnomic(a, d)

        x, y = p.skyToPix(a,d)
        msg = "Expected 0,0, got %.3f %.3f" %(x, y)
        self.assertAlmostEqual(0, x[0], 10, msg)
        self.assertAlmostEqual(0, y[0], 10, msg)

        x, y = p.skyToPix(a+arcsec,d)
        msg = "Expected +,0, got %.3f %.3f" %(x, y)
        self.assertTrue(x[0]<0, msg)
        self.assertAlmostEqual(0, y[0], 10, msg)

        x, y = p.skyToPix(a+arcsec,d+arcsec)
        msg = "Expected +,0, got %.3f %.3f" %(x, y)
        self.assertTrue(x[0]<0, msg)
        self.assertTrue(y[0]>0, msg)


    def testPixToSkyAtOrigin(self):
        arcsec = 1/3600.
        p = proj.Gnomic(0,0)

        a, d = p.pixToSky(0,0)
        msg = "Expected 0,0, got %.3f %.3f" %(a, d)
        self.assertAlmostEqual(0, a[0], 10, msg)
        self.assertAlmostEqual(0, d[0], 10, msg)

        a, d = p.pixToSky(arcsec,0)
        msg = "Expected +,0, got %.6f %.6f" %(a, d)
        self.assertTrue(a[0]>359, msg)
        self.assertAlmostEqual(0, d[0], 10, msg)

        a, d = p.pixToSky(-arcsec,0)
        msg = "Expected -,0, got %.6f %.6f" %(a, d)
        self.assertTrue(a[0]<1, msg)
        self.assertAlmostEqual(0, d[0], 10, msg)

        a, d = p.pixToSky(0, arcsec)
        msg = "Expected 0,+, got %.6f %.6f" %(a, d)
        self.assertAlmostEqual(0, a[0], 10, msg)
        self.assertTrue(d[0]>0, msg)

        a, d = p.pixToSky(0, -arcsec)
        msg = "Expected 0,-, got %.6f %.6f" %(a, d)
        self.assertAlmostEqual(0, a[0], 10, msg)
        self.assertTrue(d[0]<360, msg)



    def testPixToSkyAtPosition(self):
        a0 = 36
        d0 = 14
        tol = 6
        arcsec = 1/3600.
        p = proj.Gnomic(a0, d0)

        a, d = p.pixToSky(0,0)
        msg = "Expected 0,0, got %.3f %.3f" %(a, d)
        self.assertAlmostEqual(a[0], a0, 10, msg)
        self.assertAlmostEqual(d[0], d0, 10, msg)

        a, d = p.pixToSky(arcsec,0)
        msg = "Expected -,0, got %.9f %.9f" %(a, d)
        self.assertTrue(a[0]<a0, msg)

        a, d = p.pixToSky(-arcsec,0)
        msg = "Expected +,0, got %.9f %.9f" %(a, d)
        self.assertTrue(a[0]>a0, msg)

        a, d = p.pixToSky(0, arcsec)
        msg = "Expected 0,+, got %.9f %.9f" %(a, d)
        self.assertAlmostEqual(a[0], a0, tol, msg)
        self.assertTrue(d[0]>d0, msg)

        a, d = p.pixToSky(0, -arcsec)
        msg = "Expected 0,-, got %.9f %.9f" %(a, d)
        self.assertAlmostEqual(a[0], a0, tol, msg)
        self.assertTrue(d[0]<d0, msg)


    def testUnprojectable(self):
        """Test that unprojectable points are caught"""
        pg = proj.Gnomic(0,0)

        #Not interested in the  value, only that the answer is returned
        for i in range(-89, 90):
            pg.skyToPix(i,0)

        #I couldn't get self.assertRaises to work for me.
        for i in range(-180, -90):
            try:
                pg.skyToPix(i,0)
            except ValueError:
                pass
            else:
                self.assertTrue(False, "skyToPix didn't throw an exception when it should")

        for i in range(91, 180):
            try:
                pg.skyToPix(i,0)
            except ValueError:
                pass
            else:
                self.assertTrue(False, "skyToPix didn't throw an exception when it should")



if __name__ == "__main__":
    unittest.main()


