#!/usr/bin/env python

from __future__ import print_function
import argparse
from random import randint
from sys import argv, stdout

from fastecdsa.curve import P256
from fastecdsa.point import Point

from mathutil import p256_mod_sqrt, mod_inv

VERBOSE = False


def sanity_check(P, Q, d):
    # we now have P = dQ (the backdoor)
    assert(d * Q == P)


def gen_backdoor():
    P = P256.G  # dual EC says set P to P256 base point
    d = randint(2, P256.q)  # pick a number that is in the field P256 is over
    e = mod_inv(d, P256.q)  # find inverse of the number in the field of the base points order
    Q = e * P  # note that mult operator is overriden, this is multiplication on P256

    if VERBOSE:
        print('P = ({:x}, {:x})'.format(P.x, P.y))
        print('Q = ({:x}, {:x})'.format(Q.x, Q.y))
        print('d = {:x}'.format(d))

    sanity_check(P, Q, d)
    return P, Q, d


def find_point_on_p256(x):
    # equation: y^2 = x^3-ax+b
    y2 = (x * x * x) - (3 * x) + P256.b
    y2 = y2 % P256.p
    y = p256_mod_sqrt(y2)
    return y2 == (y * y) % P256.p, y


def gen_prediction(observed, Q, d):
    checkbits = observed & 0xffff

    for high_bits in range(2**16):
        guess = (high_bits << (8 * 30)) | (observed >> (8 * 2))
        on_curve, y = find_point_on_p256(guess)

        if on_curve:
            # use the backdoor to guess the next 30 bytes
            # point = Point(p256.curve, guess, y)
            point = Point(guess, y, curve=P256)
            s = (d * point).x
            r = (s * Q).x & (2**(8 * 30) - 1)

            if VERBOSE:
                stdout.write('Checking: %x (%x vs %x)   \r' %
                             (high_bits, checkbits, (r >> (8 * 28))))
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
        s = (t * self.P).x
        self.seed = s
        r = (s * self.Q).x
        return r & (2**(8 * 30) - 1)  # return 30 bytes


def main():
    P, Q, d = gen_backdoor()
    # seed is some random val from /dev/urandom
    dualec = DualEC(0x1fc95c3714652fe2, P, Q)
    bits1 = dualec.genbits()
    bits2 = dualec.genbits()

    observed = (bits1 << (2 * 8)) | (bits2 >> (28 * 8))
    print('Observed 32 bytes:\n{:x}'.format(observed))

    predicted = gen_prediction(observed, Q, d)
    print('Predicted 28 bytes:\n{:x}'.format(predicted))

    actual = bits2 & (2**(8 * 28) - 1)
    print('Actual 28 bytes:\n{:x}'.format(actual))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Demonstrates that Dual_EC_DBRG is backdoored.')
    parser.add_argument('-v', '--verbose', action='store_true', help='show verbose logging')

    args = parser.parse_args()
    VERBOSE = args.verbose

    main()
