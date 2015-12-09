
import unittest
import numpy as np
from .. import rotate as r

#$Id: test_rotate.py 5 2013-10-29 20:27:09Z fergalm $
#$URL: svn+ssh://fergalm@svn.code.sf.net/p/keplertwowheel/code/py/test/test_rotate.py $#


class TestVecFromRaDec(unittest.TestCase):
    def testRa1(self):
        raList = [0, 90, 180, 270, 360]
        eList = [ [1,0,0],
                  [0,1,0],
                  [-1,0,0],
                  [0,-1,0],
                  [1,0,0]
                ]

        for ra, expect in zip(raList, eList):
            calc = r.vecFromRaDec(ra,0)
            msg = "Expected %s, Calculated %s" %(expect, calc)
            for i in range(3):
                self.assertAlmostEqual(expect[i], calc[i], 10, msg)

    def testRa2(self):

        calc = r.vecFromRaDec(45,0)
        v = np.pi/4.
        expect = [np.cos(v),np.sin(v),0]
        msg = "Expected %s, Calculated %s" %(expect, calc)
        for i in range(3):
            self.assertAlmostEqual(expect[i], calc[i], 10, msg)


    def testDec1(self):
        v = np.sqrt(3)/2.
        decList = [-90, -30, 0, 30, 90]
        eList = [ [0,0,-1],
                  [v, 0, -.5] ,
                  [1,0,0],
                  [v, 0, +.5],
                  [0,0,1],
                ]

        for dec, expect in zip(decList, eList):
            calc = r.vecFromRaDec(0, dec)
            msg = "Expected %s, Calculated %s" %(expect, calc)
            for i in range(3):
                self.assertAlmostEqual(expect[i], calc[i], 10, msg)

    def testRaDec1(self):
        calc = r.vecFromRaDec(45, 60)
        a = 1/(2*np.sqrt(2))
        b = np.sqrt(3)/2.
        expect = [a, a, b]

        msg = "Expected %s, Calculated %s" %(expect, calc)
        for i in range(3):
            self.assertAlmostEqual(expect[i], calc[i], 10, msg)

    def testRaDec2(self):
        calc = r.vecFromRaDec(135, 60)
        a = 1/(2*np.sqrt(2))
        b = np.sqrt(3)/2.
        expect = [-a, a, b]

        msg = "Expected %s, Calculated %s" %(expect, calc)
        for i in range(3):
            self.assertAlmostEqual(expect[i], calc[i], 10, msg)


    def testKeplerBoresight(self):
        calc = r.vecFromRaDec(290.666667, 44.5)
        expect = [.2517, -.6674, .7009]

        msg = "Expected %s, Calculated %s" %(expect, calc)
        for i in range(3):
            self.assertAlmostEqual(expect[i], calc[i], 4, msg)



class TestRaDecFromVec(unittest.TestCase):
    def testRa1(self):
        eList = [0, 90, 180, 270]
        vecList = [ [1,0,0],
                    [0,1,0],
                    [-1,0,0],
                    [0,-1,0],
                ]

        for vec, expect in zip(vecList, eList):
            calc = r.raDecFromVec(vec)
            msg = "Expected %s, Calculated %s" %(expect, calc[0])
            self.assertAlmostEqual(expect, calc[0], 10, msg)

    def testRa2(self):
        a = .5
        b = np.sqrt(3)/2.
        eList = [30, 60, 120, 150, 210, 240, 300, 330]
        vecList = [ [b, a, 0],
                    [a, b, 0],
                    [-a, b, 0],
                    [-b, a, 0],
                    [-b, -a, 0],
                    [-a, -b, 0],
                    [a, -b, 0],
                    [b, -a, 0],
                ]

        for vec, expect in zip(vecList, eList):
            calc = r.raDecFromVec(vec)
            msg = "Expected %s, Calculated %s" %(expect, calc[0])
            self.assertAlmostEqual(expect, calc[0], 10, msg)



class TestRotationAboutAxis(unittest.TestCase):
    """Extensive testing of rotateInRa and rotateInDec
    (and by extension rotateAroundVector)
    """

    def testRotateInRa1(self):
        a = np.array([1,0,0])
        b = r.rotateInRa(a, 90)

        expect = [0,1,0]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10)

    def testRotateInRa2(self):
        a = np.array([0,1,0])
        b = r.rotateInRa(a, 90)

        expect = [-1,0,0]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10)

    def testRotateInRa3(self):
        a = np.array([0,0,1])
        b = r.rotateInRa(a, 90)

        expect = [0,0,1]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10, msg)

    def testRotateInRa4(self):
        alpha = 285 * np.pi/180.
        a = np.array([np.cos(alpha), np.sin(alpha),0])
        b = r.rotateInRa(a, -285)

        expect = [1,0,0]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10, msg)

    def testRotateInRa4b(self):
        a = r.vecFromRaDec(285, 0)
        b = r.rotateInRa(a, -285)

        expect = [1,0,0]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10, msg)


    def testRotateInRa5(self):
        a = r.vecFromRaDec(0, 44)
        b = r.rotateInRa(a, 10)

        new = r.raDecFromVec(b)
        expect = [10.,44.]
        msg = "Expected %s, Calculated %s" %(expect, new)
        for i in range(2):
            self.assertAlmostEqual(expect[i], new[i], 10, msg)



    def testRotateInDec1(self):
        a = np.array([1,0,0])
        b = r.rotateInDeclination(a, 90)

        expect = [0,0,+1]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10, msg)


    def testRotateInDec2(self):
        a = np.array([0,1,0])
        b = r.rotateInDeclination(a, 90)

        expect = [0,1,0]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10, msg)


    def testRotateInDec3(self):
        a = np.array([0,0,1])
        b = r.rotateInDeclination(a, -90)

        expect = [1,0,0]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10, msg)


    def testRotateInDec4(self):
        a = r.vecFromRaDec(0, 44)
        b = r.rotateInDeclination(a, -44)
        expect = [1,0,0]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10, msg)

    def testRotateInRaDec(self):
        a = r.vecFromRaDec(285, 44)
        b = r.rotateInRa(a, -285)
        c = r.rotateInDeclination(b, -44)

        expect = [1,0,0]
        msg = "Expected %s, Calculated %s" %(expect, c)
        for i in range(3):
            self.assertAlmostEqual(expect[i], c[i], 10, msg)



class TestRotationMatrix(unittest.TestCase):
    def testRa1(self):
        a = np.array([1,0,0])
        R = r.rightAscensionRotationMatrix(90.)
        b = np.dot(R, a)

        expect = [0,1,0]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10)

    def testRa2(self):
        a = r.vecFromRaDec(285, 0)
        R = r.rightAscensionRotationMatrix(-285)
        b = np.dot(R, a)

        expect = [1,0,0]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10)

    def testRa2(self):
        a = r.vecFromRaDec(0, 45)
        R = r.rightAscensionRotationMatrix(30)
        b = np.dot(R, a)
        new = r.raDecFromVec(b)

        expect = [30, 45]
        msg = "Expected %s, Calculated %s" %(expect, new)
        for i in range(2):
            self.assertAlmostEqual(expect[i], new[i], 10)


    def testDec1(self):
        a = np.array([1,0,0])
        R = r.declinationRotationMatrix(90.)
        b = np.dot(R, a)

        expect = [0,0,1]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10)


    def testDec2(self):
        a = r.vecFromRaDec(0, 45)
        R = r.declinationRotationMatrix(-45)
        b = np.dot(R, a)

        expect = [1,0,0]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10)

    def testRaDec(self):
        a = r.vecFromRaDec(285, 45)
        Ra = r.rightAscensionRotationMatrix(-285)
        Rd = r.declinationRotationMatrix(-45)

        b = np.dot(Rd, np.dot(Ra, a))
        expect = [1,0,0]
        msg = "Expected %s, Calculated %s" %(expect, b)
        for i in range(3):
            self.assertAlmostEqual(expect[i], b[i], 10)




if __name__ == "__main__":
    unittest.main()


