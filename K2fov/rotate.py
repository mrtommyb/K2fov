"""Coordinate transformations in radec space"""
import numpy as np


def vecFromRaDec(ra_deg, dec_deg):
    v =np.zeros( (3,))

    ra_rad = np.radians(ra_deg)
    dec_rad = np.radians(dec_deg)
    ca = np.cos(ra_rad)
    sa = np.sin(ra_rad)
    cd = np.cos(dec_rad)
    sd = np.sin(dec_rad)

    v[0] = ca*cd
    v[1] = sa*cd
    v[2] = sd

    return v


def raDecFromVec(v):
    """
    Taken from
    http://www.math.montana.edu/frankw/ccp/multiworld/multipleIVP/spherical/learn.htm
    Search for "convert from Cartestion to spherical coordinates"

    Adapted because I'm dealing with declination which is defined
    with 90degrees at zenith
    """

    #Ensure v is a normal vector
    v /= np.linalg.norm(v)

    ra_deg=0    #otherwise not in namespace0
    dec_rad = np.arcsin(v[2])
    s = np.hypot(v[0], v[1])
    if s ==0:
        ra_rad = 0
    else:
        ra_rad = np.arcsin(v[1]/s)
        ra_deg = np.degrees(ra_rad)
        if v[0] >= 0:
            if v[1] >= 0:
                pass
            else:
                ra_deg = 360 + ra_deg
        else:
            if v[1] > 0:
                ra_deg = 180 - ra_deg
            else:
                ra_deg = 180 - ra_deg

    raDec = ra_deg, np.degrees(dec_rad)
    return np.array(raDec)


def getAngleBetweenVectors(a, b, degrees=True):

    cost = np.dot(a, b)
    cost /= np.linalg.norm(a) * np.linalg.norm(b)

    angle   = np.arccos(cost)   #In radians
    if degrees:
        angle *= 180/np.pi
    return angle


def rotateAroundVector(v1, w, theta_deg):
    """Rotate vector v1 by an angle theta around w

    Taken from https://en.wikipedia.org/wiki/Axis%E2%80%93angle_representation
    (see Section "Rotating a vector")

    Notes:
    Rotating the x axis 90 degrees about the y axis gives -z
    Rotating the x axis 90 degrees about the z axis gives +y
    """

    ct = np.cos(np.radians(theta_deg))
    st = np.sin(np.radians(theta_deg))
    term1 = v1*ct
    term2 = np.cross(w, v1) * st
    term3 = np.dot(w, v1)
    term3 = w * term3 * (1-ct)

    return term1 + term2 + term3


def rotateInDeclination(v1, theta_deg):
    """Rotation is chosen so a rotation of 90 degrees from zenith
    ends up at ra=0, dec=0"""
    axis = np.array([0,-1,0])
    return rotateAroundVector(v1, axis, theta_deg)

def rotateInRa(v1, theta_deg):
    axis = np.array([0,0,1])
    return rotateAroundVector(v1, axis, theta_deg)


def declinationRotationMatrix(theta_deg):
    """Construct the rotation matrix for a rotation of the declination
    coords (i.e around the axis of ra=90, dec=0)

    Taken from Section 3.3 of Arfken and Weber (Eqn 3.91)
    Modfied the signs of the sines so that a rotation of the zenith
    vector by 90 degrees ends up at ra, dec = 0,0
    """

    ct = np.cos(np.radians(theta_deg))
    st = np.sin(np.radians(theta_deg))

    mat = np.zeros((3,3))

    mat[0,0] = ct
    mat[0,2] = -st
    mat[1,1] = 1
    mat[2,0] = st
    mat[2,2] = ct

    return mat


def rightAscensionRotationMatrix(theta_deg):
    """Construct the rotation matrix for a rotation of the ra coords
    (i.e around the declination axis)

    Taken from Section 3.3 of Arfken and Weber (Eqn 3.91)
    Modfied the signs of the sines so that a rotation of the
    position (ra, dec) = (0,0) by 90 degrees gives (90, 0)

    """
    ct = np.cos(np.radians(theta_deg))
    st = np.sin(np.radians(theta_deg))

    mat = np.zeros((3,3))

    mat[0,0] = ct
    mat[0,1] = -st
    mat[1,0] = st
    mat[1,1] = ct
    mat[2,2] = 1

    return mat


def rotateAboutVectorMatrix(vec, theta_deg):
    """Construct the matrix that rotates vector a about
    vector vec by an angle of theta_deg degrees

    Taken from
    http://en.wikipedia.org/wiki/Rotation_matrix#Rotation_matrix_from_axis_and_angle

    which is not the same place I got the code for rotateAroundVector()
    and they don't link to each other.
    """

    ct = np.cos(np.radians(theta_deg))
    st = np.sin(np.radians(theta_deg))

    #Ensure vector has normal length
    vec /= np.linalg.norm(vec)
    assert( np.all( np.isfinite(vec)))

    #compute the three terms
    term1 = ct * np.eye(3)

    ucross = np.zeros( (3,3))
    ucross[0] = [0, -vec[2], vec[1]]
    ucross[1] = [vec[2], 0, -vec[0]]
    ucross[2] = [-vec[1], vec[0], 0]

    term2 = st*ucross

    ufunny = np.zeros( (3,3))
    for i in range(0,3):
        for j in range(i,3):
            ufunny[i,j] = vec[i]*vec[j]
            ufunny[j,i] = ufunny[i,j]

    term3 = (1-ct) * ufunny

    return term1 + term2 + term3


def main():
    v1 = vecFromRaDec(0, 0)
    w = vecFromRaDec(0, 90.)

    return v1, w
