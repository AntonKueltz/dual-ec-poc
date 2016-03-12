## Intro
Proof of concept code exploiting the backdoor in [Dual_EC_DBRG](http://csrc.nist.gov/publications/nistpubs/800-90A/SP800-90A.pdf)
written in python. The code is based on [this blog post](https://blog.0xbadc0de.be/archives/155)
as well as [this paper](http://dualec.org/DualECTLS.pdf).

## Usage
### Requirements
This code requires the `ecdsa` package - `$ pip install ecdsa`.

### Run
To run do `python dualec.py`. For verbose output `python dualec.py -v`

## Structure
### `dualec.py`
*Forthcoming...*

### `mathutil.py`
##### `mod_inv(n, mod)`
Compute the modular inverse of n % mod, in other words, find m such that
1 = (m * n) % mod.

##### `kronecker(a, b)`
Compute the Kronecker symbol of a % b. If b is prime this is the Legendre symbol
of a % b, and will return 1 if a is a quadratic residue.

##### `modsqrt(n, p)`
Compute the square root of n % p, in other words, find m such that m * m % p =
n % p.

## Performance
This code is currently not super fast. This is the result of having to brute force
the 2 highest order bytes of the observed output (since Dual_EC discards them).
This gives us 2^16 possible x coordinates to brute force. Substituting these x
values into the P256 equation, we can check if y^2 is a quadratic residue (i.e.
if the (x, y) pair lies on P256). If it does we have to perform two point
multiplications on P256 in order to check our back door. Point multiplication is
outsourced to the [ecdsa](https://github.com/warner/python-ecdsa/tree/master/ecdsa)
package and is the most computationally intensive part of this program.
