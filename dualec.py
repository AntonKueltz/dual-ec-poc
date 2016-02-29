from ecdsa import NIST256p as p256
from Crypto.Random.random import randint


def mod_inv(n, mod):
    n = n % mod
    t, newt = 0, 1
    r, newr = mod, n

    while newr != 0:
        q = r / newr
        tmp1, tmp2 = t, r

        t = newt
        newt = tmp1 - q * newt
        r = newr
        newr = tmp2 - q * newr

    if r > 1:
        return 0
    elif t < 0:
        return t + mod
    else:
        return t


def gen_backdoor():
    P = p256.generator  # dual EC says set P to P256 base point
    d = randint(2, p256.curve.p())  # pick a number that is in the field P256 is over
    e = mod_inv(d, P.order())  # find inverse of the number in the field of the base points order
    Q = P * e  # note that mult operator is overriden, this is multiplication on P256

    # we now have P = dQ (the backdoor)
    assert((Q * d).x() == P.x())
    assert((Q * d).y() == P.y())
    return Q, P, d


class DualEC():
    def __init__(self, seed, P, Q):
        self.seed = seed
        self.P = P
        self.Q = Q

    def genbits(self):
        t = self.seed
        s = (self.P * t).x()
        self.seed = s
        r = (self.Q * s).x()
        return r & 0x3fffffff  # return 30 bits


if __name__ == '__main__':
    P, Q, d = gen_backdoor()
    dualec = DualEC(0x0badc0de, P, Q)
    print dualec.genbits()
    print dualec.genbits()
