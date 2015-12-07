
import numpy as np
import unittest
from .. import rotate2 as r

#$Id: test_rotate2.py 28 2013-12-02 04:34:57Z fergalm $
#$URL: svn+ssh://fergalm@svn.code.sf.net/p/keplertwowheel/code/py/test/test_rotate2.py $

class TestSingleRotation(unittest.TestCase):

    def testXAroundZ(self):
        for deg in np.arange(0, 360):
            ct = np.cos( np.radians(deg))
            st = np.sin( np.radians(deg))

            v = np.array([1,0,0])
            exp = np.array([ ct, st, 0])

            Rmat = r.rotateInZMat(deg)
            calc = np.dot(Rmat, v)

            msg = "Angle %.0f: Expect %s, Calc %s" %(deg, exp, calc)
            for i in range(3):
                self.assertAlmostEqual(exp[i], calc[i], 6, msg)


    def testYAroundZ(self):
        for deg in np.arange(0, 360):
            ct = np.cos( np.radians(deg))
            st = np.sin( np.radians(deg))

            v = np.array([0,1,0])
            exp = np.array([ -st, ct, 0])

            Rmat = r.rotateInZMat(deg)
            calc = np.dot(Rmat, v)

            msg = "Angle %.0f: Expect %s, Calc %s" %(deg, exp, calc)
            for i in range(3):
                self.assertAlmostEqual(exp[i], calc[i], 6, msg)


    def testXAroundY(self):
        for deg in np.arange(0, 360):
            ct = np.cos( np.radians(deg))
            st = np.sin( np.radians(deg))

            v = np.array([1,0,0])
            exp = np.array([ ct, 0, -st])

            Rmat = r.rotateInYMat(deg)
            calc = np.dot(Rmat, v)

            msg = "Angle %.0f deg:\n Expect %s, Calc %s" \
                %(deg, exp, calc)
            for i in range(3):
                self.assertAlmostEqual(exp[i], calc[i], 6, msg)


    def testZAroundY(self):
        for deg in np.arange(0, 360):
            ct = np.cos( np.radians(deg))
            st = np.sin( np.radians(deg))

            v = np.array([0,0,1])
            exp = np.array([ st, 0, ct])

            Rmat = r.rotateInYMat(deg)
            calc = np.dot(Rmat, v)

            msg = "Angle %.0f deg:\n Expect %s, Calc %s" \
                %(deg, exp, calc)
            for i in range(3):
                self.assertAlmostEqual(exp[i], calc[i], 6, msg)


class TestRotationOrder(unittest.TestCase):


    def testSmoke(self):
        self.anglePairTestX(30,60)
        self.anglePairTestY(30,60)

    def XtestAll(self):
        for ang1 in range(0, 361, 10):
            for ang2 in range(-90, 91, 10):
                self.anglePairTest(ang1, ang2)


    def anglePairTestX(self, theta_deg, phi_deg):
        ct = np.cos( np.radians(theta_deg))
        st = np.sin( np.radians(theta_deg))

        cp = np.cos( np.radians(phi_deg))
        sp = np.sin( np.radians(phi_deg))


        e1 = ct*cp
        e2 = st
        e3 = -ct*sp

        x = np.array( [1,0,0])
        exp = np.array( [e1, e2, e3] )

        Rz = r.rotateInZMat(theta_deg)
        Ry = r.rotateInYMat(phi_deg)

        rotMat = np.dot(Ry, Rz)
        calc = np.dot(rotMat, x)

        msg = "Angles %.0f %.0f: Expect %s, Calc %s" \
            %(theta_deg, phi_deg, exp, calc)
        for i in range(3):
            self.assertAlmostEqual(exp[i], calc[i], 6, msg)



    def anglePairTestY(self, theta_deg, phi_deg):
        ct = np.cos( np.radians(theta_deg))
        st = np.sin( np.radians(theta_deg))

        cp = np.cos( np.radians(phi_deg))
        sp = np.sin( np.radians(phi_deg))


        e1 = -st*cp
        e2 = ct
        e3 = st*sp

        y = np.array( [0,1,0])
        exp = np.array( [e1, e2, e3] )

        Rz = r.rotateInZMat(theta_deg)
        Ry = r.rotateInYMat(phi_deg)

        rotMat = np.dot(Ry, Rz)
        calc = np.dot(rotMat, y)

        msg = "Angles %.0f %.0f: Expect %s, Calc %s" \
            %(theta_deg, phi_deg, exp, calc)
        for i in range(3):
            self.assertAlmostEqual(exp[i], calc[i], 6, msg)



    def anglePairTestZ(self, theta_deg, phi_deg):
        ct = np.cos( np.radians(theta_deg))
        st = np.sin( np.radians(theta_deg))

        cp = np.cos( np.radians(phi_deg))
        sp = np.sin( np.radians(phi_deg))


        e1 = sp
        e2 = 0
        e3 = cp

        z = np.array( [0,0,1])
        exp = np.array( [e1, e2, e3] )

        Rz = r.rotateInZMat(theta_deg)
        Ry = r.rotateInYMat(phi_deg)

        rotMat = np.dot(Ry, Rz)
        calc = np.dot(rotMat, z)

        msg = "Angles %.0f %.0f: Expect %s, Calc %s" \
            %(theta_deg, phi_deg, exp, calc)
        for i in range(3):
            self.assertAlmostEqual(exp[i], calc[i], 6, msg)




if __name__ == "__main__":
    unittest.main()

