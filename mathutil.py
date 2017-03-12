from random import randint


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


def p256_mod_sqrt(c):
    # only works for field P256 is over
    p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    t1 = pow(c, 2, p)
    t1 = (t1 * c) % p
    t2 = pow(t1, 2**2, p)
    t2 = (t2 * t1) % p
    t3 = pow(t2, 2**4, p)
    t3 = (t3 * t2) % p
    t4 = pow(t3, 2**8, p)
    t4 = (t4 * t3) % p
    r = pow(t4, 2**16, p)
    r = (r * t4) % p
    r = pow(r, 2**32, p)
    r = (r * c) % p
    r = pow(r, 2**96, p)
    r = (r * c) % p
    return pow(r, 2**94, p)
