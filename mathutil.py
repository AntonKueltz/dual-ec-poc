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


# kronecker is the legendre symbol when b is prime
def kronecker(a, b):
    if b == 0:
        if a == 1 or a == -1:
            return 1
        else:
            return 0

    if a & 1 == 0 and b & 1 == 0:
        return 0

    v = 0

    while b & 1 == 0:
        v += 1
        b /= 2

    if v & 1 == 0:
        k = 1
    else:
        k = (-1) ** ((a * a - 1) / 8)

    if b < 0:
        b = -b

        if a < 0:
            k = -k

    while a != 0:
        v = 0

        while a & 1 == 0:
            v += 1
            a /= 2

        if v & 1 == 1:
            k = (-1) ** ((b * b - 1) / 8) * k

        k = (-1) ** ((a - 1) * (b - 1) / 4) * k
        r = abs(a)
        a = b % r
        b = r

    return 0 if b > 1 else k


def modsqrt(n, p):
    S, q = 0, p - 1

    while q % 2 == 0:
        S += 1
        q /= 2

    Q = (p - 1) / (2 ** S)

    z = randint(1, p)
    while kronecker(z, p) != -1:
        z = randint(1, p)

    c = pow(z, Q, p)
    R = pow(n, (Q + 1) / 2, p)
    t = pow(n, Q, p)
    M = S

    while t != 1:
        i, exp = 1, 2

        while pow(t, exp, p) != 1:
            i += 1
            exp = 2 ** i

        exp = 2 ** (M - i - 1)
        b = pow(c, exp, p)
        R = (R * b) % p
        t = (t * b * b) % p
        c = (b * b) % p
        M = i

    return R
