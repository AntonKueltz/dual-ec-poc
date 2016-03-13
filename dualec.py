from random import randint
from sys import argv, stdout

from ecdsa import NIST256p as p256
from ecdsa.ellipticcurve import Point

from mathutil import kronecker, modsqrt, mod_inv

VERBOSE = False


def sanity_check(P, Q, d):
    # we now have P = dQ (the backdoor)
    assert((d * Q).x() == P.x())
    assert((d * Q).y() == P.y())

    i = 0xabadfade
    iQ, iP = i * Q, i * P
    assert((d * iQ).x() == iP.x())


def gen_backdoor():
    P = p256.generator  # dual EC says set P to P256 base point
    d = randint(2, p256.curve.p())  # pick a number that is in the field P256 is over
    e = mod_inv(d, P.order())  # find inverse of the number in the field of the base points order
    Q = P * e  # note that mult operator is overriden, this is multiplication on P256

    if VERBOSE:
        print 'P = ({:x}, {:x})'.format(P.x(), P.y())
        print 'Q = ({:x}, {:x})'.format(Q.x(), Q.y())
        print 'd = {:x}'.format(d)

    sanity_check(P, Q, d)
    return P, Q, d


def find_point_on_p256(x):
    # equation: y^2 = x^3-3x+41058363725152142129326129780047268409114441015993725554835256314039467401291
    y2 = (x * x * x) - (3 * x) + 41058363725152142129326129780047268409114441015993725554835256314039467401291
    y2 = y2 % p256.curve.p()
    has_root = (kronecker(y2, p256.curve.p()) == 1)

    if has_root:
        return True, modsqrt(y2, p256.curve.p())
    else:
        return False, None


def gen_prediction(observed, Q, d):
    checkbits = observed & 0xffff

    for high_bits in range(2**16):
        guess = (high_bits << (8 * 30)) | (observed >> (8 * 2))
        on_curve, y = find_point_on_p256(guess)

        if on_curve:
            # use the backdoor to guess the next 30 bytes
            point = Point(p256.curve, guess, y)
            s = (d * point).x()
            r = (s * Q).x() & (2**(8 * 30) - 1)

            if VERBOSE:
                stdout.write('Checking: %x (%x vs %x)   \r' % (high_bits, checkbits, (r >> (8 * 28))))
                stdout.flush()

            # check the first 2 bytes against the observed bytes
            if checkbits == (r >> (8 * 28)):
                if VERBOSE:
                    stdout.write('\r\n')
                    stdout.flush()

                # if we have a match then we know the next 28 bits
                return r & (2**(8 * 28) - 1)

    return 0


class DualEC():
    def __init__(self, seed, P, Q):
        self.seed = seed
        self.P = P
        self.Q = Q

    def genbits(self):
        t = self.seed
        s = (t * self.P).x()
        self.seed = s
        r = (s * self.Q).x()
        return r & (2**(8 * 30) - 1)  # return 30 bytes


if __name__ == '__main__':
    if len(argv) == 2 and argv[1] == '-v':
        VERBOSE = True

    P, Q, d = gen_backdoor()
    # seed is some random val from /dev/urandom
    dualec = DualEC(0x1fc95c3714652fe2, P, Q)
    bits1 = dualec.genbits()
    bits2 = dualec.genbits()

    observed = (bits1 << (2 * 8)) | (bits2 >> (28 * 8))
    print 'Observed 32 bytes:\n{:x}'.format(observed)

    predicted = gen_prediction(observed, Q, d)
    print 'Predicted 28 bytes:\n{:x}'.format(predicted)

    actual = bits2 & (2**(8 * 28) - 1)
    print 'Actual 28 bytes:\n{:x}'.format(actual)
