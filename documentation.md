Documentation
-------------

To use LC4, first import the *lc4* module.

    >>> import lc4

### Encryption and Decryption

Text is encrypted with *lc4.encrypt*.
    
    >>> import lc4
    >>> key = "#qiye7hozcb2asm5kd9x_nlvrwput6f3j84g"
    >>> nonce = "mi2zwe"
    >>> text = "this_is_an_example"
    >>> encrypted = lc4.encrypt(key, text, nonce=nonce)

Text is decrypted with *lc4.decrypt*.

    >>> decrypted = lc4.decrypt(key, encrypted, nonce=nonce)

*lc4.encrypt* and *lc4.decrypt* both take the following arguments:

* **key** A *secret* permutation of the characters in the alphabet (see documentation for
*alphabet* below). A key can be randonly generated using the command-line utility (see
*Interactive Command-Line Utility* documentaion below).
* **text** Text to be encrypted/decrypted.
* **nonce** (optional) A sequence of randomly chosen characters from the alphabet. The paper
specifies that nonces be 6 or more characters and different for each message. A nonce can be
randonly generated using the command-line utility (see *Interactive Command-Line Utility*
documentaion below).
* **alphabet** (optional; defaults to "#_23456789abcdefghijklmnopqrstuvwxyz") A string of 36
unique characters that comprise messages.
* **verbose** (optional; defaults to False) A boolean indicating whether there should be
status logging to stdout.

### Interactive Command-Line Utility

The *lc4* package includes an interactive command line utility. This can be used to
generate nonces, generate keys, and encrypt/decrypt text.

##### Example session

```
$ lc4 --version
lc4 0.1.3

$ lc4 --help
usage: lc4.py [-h] [-a STRING] [-n INTEGER]

optional arguments:
  -h, --help            show this help message and exit
  -a STRING, --alphabet STRING
                        A string of 36 characters representing the alphabet.
                        (default: #_23456789abcdefghijklmnopqrstuvwxyz)
  -n INTEGER, --nonce-length INTEGER
                        The number of characters in randomly generated nonces
                        when using option 2. (default: 6)

$ lc4
1. Generate Key
2. Generate Nonce
3. Encrypt
4. Decrypt
5. Quit
>>> 1
#qiye7hozcb2asm5kd9x_nlvrwput6f3j84g

$ lc4
1. Generate Key
2. Generate Nonce
3. Encrypt
4. Decrypt
5. Quit
>>> 2
mi2zwe

$ lc4
1. Generate Key
2. Generate Nonce
3. Encrypt
4. Decrypt
5. Quit
>>> 3
Key: #qiye7hozcb2asm5kd9x_nlvrwput6f3j84g
Nonce: mi2zwe
Text: this_is_an_example
emt9lnk8gg7#3h7s8k

$ lc4
1. Generate Key
2. Generate Nonce
3. Encrypt
4. Decrypt
5. Quit
>>> 4
Key: #qiye7hozcb2asm5kd9x_nlvrwput6f3j84g
Nonce: mi2zwe
Text: emt9lnk8gg7#3h7s8k
this_is_an_example
```
