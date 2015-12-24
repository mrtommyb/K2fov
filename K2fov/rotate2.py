"""
Construct various rotation matrices.

The documentation strings assume the "3-2-1" convention. A
vector should be rotated about the z-axis first, then the y-axis,
then finally the x-axis.

For ra and dec, rotate in ra first, then declination.

To rotate a vector, premultiply the the matrix returned
by these functions.

R = rotateInZ(angle)
vDash = np.dot(R, v)

To yaw, pitch and roll.
Y = yawLeftMat()
P = pitchUpMAt()
R = rollClockwiseMat()

rotMat = np.dot(R, P)
rotMat = np.dot(rotMat, Y)
vDash = np.dot(rotMat, v)

This is equivalent to vDash = R.P.Y.v

If you want to rotate the coordinate system instead of the vector
then you need to post multiply the matrix
vDash = np.dot(v, R), where vDash is the vector in the rotated
coord system.
"""
import numpy as np


def getAngleBetweenVectors(a, b, degrees=True):
    norm = np.linalg.norm

    cost = np.dot(a, b)
    cost /= norm(a) * norm(b)

    angle = np.arccos(cost)   # In radians
    if degrees:
        angle *= 180/np.pi
    return angle


def declinationRotationMatrix(theta_deg):
    """Rotate a vector in increasing declination

    Input:
    theta_deg   (float) Angle through which vectors should be
                rotated in degrees

    Returns:
    A matrix

    To rotate a vector, premultiply by this matrix.
    To rotate the coord sys underneath the vector, post multiply
    """
    return pitchUpMat(theta_deg)


def rightAscensionRotationMatrix(theta_deg):
    """Rotate a vector in increasing ra

    Input:
    theta_deg   (float) Angle through which vectors should be
                rotated in degrees

    Returns:
    A matrix

    To rotate a vector, premultiply by this matrix.
    To rotate the coord sys underneath the vector, post multiply
    """

    return yawLeftMat(theta_deg)


def yawLeftMat(theta_deg):
    """Thin wrapper to rotateInZ with a human readable name

    Input:
    theta_deg   (float) Angle through which vectors should be
                rotated in degrees

    Returns:
    A matrix

    To rotate a vector, premultiply by this matrix.
    To rotate the coord sys underneath the vector, post multiply
    """
    return rotateInZMat(theta_deg)


def pitchUpMat(theta_deg):
    """Thin wrapper to rotateInY with a human readable name

    Input:
    theta_deg   (float) Angle through which vectors should be
                rotated in degrees

    Returns:
    A matrix

    To rotate a vector, premultiply by this matrix.
    To rotate the coord sys underneath the vector, post multiply
    """
    return rotateInYMat(-theta_deg)


def rollClockwiseMat(theta_deg):
    """Thin wrapper to rotateInX with a human readable name

    Input:
    theta_deg   (float) Angle through which vectors should be
                rotated in degrees

    Returns:
    A matrix

    To rotate a vector, premultiply by this matrix.
    To rotate the coord sys underneath the vector, post multiply
    """
    return rotateInXMat(theta_deg)


def rotateAboutVectorMatrix(vec, theta_deg):
    """Construct the matrix that rotates vector a about
    vector vec by an angle of theta_deg degrees

    Taken from
    http://en.wikipedia.org/wiki/Rotation_matrix#Rotation_matrix_from_axis_and_angle

    Input:
    theta_deg   (float) Angle through which vectors should be
                rotated in degrees

    Returns:
    A matrix

    To rotate a vector, premultiply by this matrix.
    To rotate the coord sys underneath the vector, post multiply

    """
    ct = np.cos(np.radians(theta_deg))
    st = np.sin(np.radians(theta_deg))

    # Ensure vector has normal length
    vec /= np.linalg.norm(vec)
    assert( np.all( np.isfinite(vec)))

    # compute the three terms
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


def rotateInZMat(theta_deg):
    """Rotate a vector theta degrees around the z-axis

    Equivalent to yaw left

    Rotates the vector in the sense that the x-axis is rotated
    towards the y-axis. If looking along the z-axis (which is
    not the way you usually look at it), the vector rotates
    clockwise.

    If sitting on the vector [1,0,0], the rotation is towards the left

    Input:
    theta_deg   (float) Angle through which vectors should be
                rotated in degrees

    Returns:
    A matrix

    To rotate a vector, premultiply by this matrix.
    To rotate the coord sys underneath the vector, post multiply

    """

    ct = np.cos( np.radians(theta_deg))
    st = np.sin( np.radians(theta_deg))
    rMat = np.array([  [ ct, -st, 0],
                       [ st,  ct, 0],
                       [  0,   0, 1],
                    ])

    return rMat


def rotateInYMat(theta_deg):
    """Rotate a vector theta degrees around the y-axis

    Equivelent to pitch *down*

    Rotates the vector in the sense that the x-axis is rotated
    towards the negative y-axis. If looking along the y-axis,
    the vector rotates clockwise.

    If sitting on the vector [1,0,0], the rotation is down
    (towards the  south pole)

    Input:
    theta_deg   (float) Angle through which vectors should be
                rotated in degrees

    Returns:
    A matrix

    To rotate a vector, premultiply by this matrix.
    To rotate the coord sys underneath the vector, post multiply

    """
    ct = np.cos( np.radians(theta_deg))
    st = np.sin( np.radians(theta_deg))

    rMat = np.array([  [ ct,  0,  st],
                       [  0,  1,   0],
                       [-st,  0,  ct],
                    ])
    return rMat


def rotateInXMat(theta_deg):
    """Rotate a vector theta degrees around the x-axis

    Equivelent to rolling around x-axis clockwise

    Rotates the vector in the sense that the y-axis is rotated
    towards the z-axis. If looking along the x-axis,
    the vector rotates clockwise.

    If sitting on the vector [1,0,0] , the rotation is a clockwise
    roll.


    Input:
    theta_deg   (float) Angle through which vectors should be
                rotated in degrees

    Returns:
    A matrix

    To rotate a vector, premultiply by this matrix.
    To rotate the coord sys underneath the vector, post multiply
    """
    ct = np.cos( np.radians(theta_deg))
    st = np.sin( np.radians(theta_deg))

    rMat = np.array([  [  1,   0,  0],
                       [  0,  ct,  -st],
                       [  0, st,  ct],
                    ])
    return rMat


def vecFromRaDec(ra_deg, dec_deg):
    v = np.zeros((3,))

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

    @TODO: Rigourously test this against spice.recrad()
    """
    # Ensure v is a normal vector
    v /= np.linalg.norm(v)

    ra_deg = 0    # otherwise not in namespace0
    dec_rad = np.arcsin(v[2])
    s = np.hypot(v[0], v[1])
    if s == 0:
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
