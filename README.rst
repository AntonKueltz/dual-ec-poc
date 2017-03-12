Intro
=====
Proof of concept code exploiting the backdoor in Dual_EC_DBRG_ written in python. The code is based
on this blog-post_ as well as this paper_.

Usage
=====

Requirements
~~~~~~~~~~~~

This code requires the `fastecdsa` package v1.4.1 or higher:

.. code:: bash

    $ pip install -r requirements.txt

OR

.. code:: bash

    $ pip install fastecdsa

Run
~~~
To run do :code:`python dualec.py`. For verbose output :code:`python dualec.py -v`

.. _Dual_EC_DBRG: http://csrc.nist.gov/publications/nistpubs/800-90A/SP800-90A.pdf
.. _blog-post: https://blog.0xbadc0de.be/archives/155
.. _paper: http://dualec.org/DualECTLS.pdf
