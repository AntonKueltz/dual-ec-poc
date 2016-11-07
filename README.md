## Intro
Proof of concept code exploiting the backdoor in [Dual_EC_DBRG](http://csrc.nist.gov/publications/nistpubs/800-90A/SP800-90A.pdf)
written in python. The code is based on [this blog post](https://blog.0xbadc0de.be/archives/155)
as well as [this paper](http://dualec.org/DualECTLS.pdf).

## Usage
### Requirements
This code requires the `fastecdsa` package - `$ pip install fastecdsa`.

### Run
To run do `python dualec.py`. For verbose output `python dualec.py -v`
