def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def mod_inv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


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
