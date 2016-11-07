from random import randint
from sys import argv, stdout

from fastecdsa.curve import P256

from mathutil import kronecker, modsqrt, mod_inv

VERBOSE = False


def sanity_check(P, Q, d):
    # we now have P = dQ (the backdoor)
    assert(P256.point_mul(Q, d) == P)


def gen_backdoor():
    P = P256.G  # dual EC says set P to P256 base point
    d = randint(2, P256.p)  # pick a number that is in the field P256 is over
    e = mod_inv(d, P256.q)  # find inverse of the number in the field of the base points order
    Q = P256.point_mul(P, e)  # note that mult operator is overriden, this is multiplication on P256

    if VERBOSE:
        print 'P = ({:x}, {:x})'.format(P[0], P[1])
        print 'Q = ({:x}, {:x})'.format(Q[0], Q[1])
        print 'd = {:x}'.format(d)

    sanity_check(P, Q, d)
    return P, Q, d


def find_point_on_p256(x):
    # equation: y^2 = x^3-3x+41058363725152142129326129780047268409114441015993725554835256314039467401291
    y2 = (x * x * x) - (3 * x) + P256.b
    y2 = y2 % P256.p
    has_root = (kronecker(y2, P256.p) == 1)

    if has_root:
        return True, modsqrt(y2, P256.p)
    else:
        return False, None


def gen_prediction(observed, Q, d):
    checkbits = observed & 0xffff

    for high_bits in range(2**16):
        guess = (high_bits << (8 * 30)) | (observed >> (8 * 2))
        on_curve, y = find_point_on_p256(guess)

        if on_curve:
            # use the backdoor to guess the next 30 bytes
            # point = Point(p256.curve, guess, y)
            point = (guess, y)
            s = P256.point_mul(point, d)[0]
            r = (P256.point_mul(Q, s)[0]) & (2**(8 * 30) - 1)

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
        s = P256.point_mul(self.P, t)[0]
        self.seed = s
        r = P256.point_mul(self.Q, s)[0]
        return r & (2**(8 * 30) - 1)  # return 30 bytes


def main():
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


if __name__ == '__main__':
    if len(argv) == 2 and argv[1] == '-v':
        VERBOSE = True

    main()
    '''
    Q = (
        0xd19761748936051e5fb436f5c383a2ca6fbd1e61f227a3d70f44d73311781b32,
        0xdc4c729f6de383957f62d1318197757cd2015ae6f27066ef9990fcf6d4319d82
    )
    d = 0x561021d34971c6b5da29dbefb21413a469a751356392133a4a78981fb51f3a01
    observed = 0x8fc4b1d886a3ac3d3ae3c13722bc5eead9d1dd5eda876ca59b8c33ebeb6e2616
    print'Prediction: {:x}'.format(gen_prediction(observed, Q, d))
    '''
