
import numpy as np
import unittest
import os

from .. import fov

#$Id: test_fov.py 49 2014-02-26 17:52:04Z fergalm $
#$URL: svn+ssh://fergalm@svn.code.sf.net/p/keplertwowheel/code/py/test/test_fov.py $




class TestFov(unittest.TestCase):

    def testOrigin(self):
        """Test orientation of FOV in null position"""

        f = fov.KeplerFov(0,0,0)
        #Ch 43 is 13.3, near centre
        a,d = f.getRaDecForChannelColRow(43, 1000, 1000)
        self.assertTrue( np.fabs(a) < .2)
        self.assertTrue( np.fabs(d) < .2)

        #Check that mod 3 is north of mod 8
        a3, d3 = f.getRaDecForChannelColRow(5,0,0)
        a8, d8 = f.getRaDecForChannelColRow(21,0,0)
        self.assertTrue( d3>d8)

        #Check that mod 11's ra is greater than mod 13
        a13, d13 = f.getRaDecForChannelColRow(43,0,0)
        a11, d11 = f.getRaDecForChannelColRow(33,0,0)
        self.assertTrue( a11 > a13)

        #Check that mod 20's ra is less than mod 13
        a13, d13 = f.getRaDecForChannelColRow(43,0,0)
        a20, d20 = f.getRaDecForChannelColRow(69,0,0)
        self.assertTrue(a20 > 350)
        self.assertTrue( a20-360 < a13)


    def testRotateClockwise(self):
        """Test orientation of FOV in null position"""

        f = fov.KeplerFov(0,0,90)
        #Ch 43 is 13.3, near centre
        a,d = f.getRaDecForChannelColRow(43, 1000, 1000)
        self.assertTrue( np.fabs(a-360) < .2)
        self.assertTrue( np.fabs(d) < .2)

        #Check that mod 3's ra less than mod 8
        a3, d3 = f.getRaDecForChannelColRow(5,0,0)
        a8, d8 = f.getRaDecForChannelColRow(21,0,0)
        self.assertTrue(a3 > 350)
        self.assertTrue(a3 < a8)

        #Check that mod 11 is north of mod 13
        a13, d13 = f.getRaDecForChannelColRow(43,0,0)
        a11, d11 = f.getRaDecForChannelColRow(33,0,0)
        self.assertTrue( d11 >  d13)

        #Check that mod 20's dec is less than mod 13
        a13, d13 = f.getRaDecForChannelColRow(43,0,0)
        a20, d20 = f.getRaDecForChannelColRow(69,0,0)
        self.assertTrue( d20 < d13)


    def testQuarter1(self):
        """Test that my code gets the mod-out right for a set of
        stars in Q1.

        This ensures I have the order of the  modouts correct and I didn't
        get anything flipped."""

        #Recreate Kepler pointing in Q1. The source of the 33 degrees
        #for the rotation to get the FOV correct is lost in the mists
        #of time. The 90 just rotates the FOV to the correct angle.
        #For reference, the first light image has the same orientation
        #as Q1.
        a0, d0 = 290.66666667, 44.5
        kf = fov.KeplerFov(a0, d0, 33+90)

        #Find path to the test file
        path = os.path.dirname(os.path.abspath(__file__))
        data = np.loadtxt(os.path.join(path, "data", "Q1_obj_position.txt"))

        for row in data:
            #import pdb; pdb.set_trace()
            ra, dec = row[1:3]
            expectedCh = int(row[5])

            msg = "Uh Oh"
            calcCh = int(kf.pickAChannel(ra, dec))
            self.assertEqual(expectedCh, calcCh, msg)


    def testGitHubBug1(self):
        #Approx coords of field 1
        a0, d0, rho0 = 174., 1.422, 260.6
        kf = fov.KeplerFov(a0, d0, rho0)

        #I'm just checking that the code returns a legal value
        #I don't care about the input.
        ch, col, row = kf.getChannelColRow(+181.946541, 2.740250)

        self.assertRaises(ValueError, kf.getChannelColRow, +1.946541, 2.740250)
        self.assertRaises(ValueError, kf.getChannelColRow, -1.946541, 2.740250)


    def testGitHubBug2(self):
        """Check that -ve ra and dec handled correctly"""
        a0, d0, rho0 = 0., 0, 0
        kf = fov.KeplerFov(a0, d0, rho0)

        #I'm just checking that the code returns a legal value
        #I don't care about the input.
        ch, col, row = kf.getChannelColRow(+1, 0)
        self.assertEqual(ch, 43)

        ch, col, row = kf.getChannelColRow(-1, 0)
        self.assertEqual(ch, 42)

if __name__ == "__main__":
    unittest.main()

