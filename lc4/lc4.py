from __future__ import print_function

import argparse
import os
import random
import sys

import numpy as np

version_txt = os.path.join(os.path.dirname(__file__), 'version.txt')
with open(version_txt, 'r') as f:
    __version__ = f.read().strip()

# ************************************************************
# * Utils
# ************************************************************

_major_version = sys.version_info.major
if _major_version not in (2, 3):
    raise RuntimeError("Unsupported version of Python: {}".format(_major_version))


def _range(*args, **kwargs):
    if _major_version == 2:
        import __builtin__
        return __builtin__.xrange(*args, **kwargs)
    else:
        import builtins
        return builtins.range(*args, **kwargs)


def _input(*args, **kwargs):
    if _major_version == 2:
        return raw_input(*args, **kwargs)
    else:
        return input(*args, **kwargs)

# ************************************************************
# * Core (private)
# ************************************************************

_DEFAULT_ALPHABET = "#_23456789abcdefghijklmnopqrstuvwxyz"


class _State:
    def __init__(self, K):
        self.S = np.empty((6, 6), dtype=int)
        for k in _range(36):
            self.S[divmod(k, 6)] = K[k]
        self.i = 0
        self.j = 0

    def astuple(self):
        return (self.S, self.i, self.j)

    def _update(self, S, i, j):
        self.S = S
        self.i = i
        self.j = j

    def step(self, r, x, y, ct):
        S, i, j = self.astuple()
        S[r, :] = np.roll(S[r, :], 1)
        y = (y + (x == r)) % 6
        j = (j + (i == r)) % 6
        S[:, y] = np.roll(S[:, y], 1)
        i = (i + (j == y)) % 6
        i = (i + ct // 6) % 6
        j = (j + ct % 6) % 6
        self._update(S, i, j)


def _encrypt(state, P):
    n = P.shape[0]
    C = np.empty(n, dtype=int)
    for idx, pt in enumerate(P):
        S, i, j = state.astuple()
        where = np.where(S == pt)
        r = where[0][0]
        c = where[1][0]
        x = (r + S[i, j] // 6) % 6
        y = (c + S[i, j] % 6) % 6
        ct = S[x, y]
        C[idx] = ct
        state.step(r, x, y, ct)
    return C


def _decrypt(state, C):
    n = C.shape[0]
    P = np.empty(n, dtype=int)
    for idx, ct in enumerate(C):
        S, i, j = state.astuple()
        where = np.where(S == ct)
        x = where[0][0]
        y = where[1][0]
        r = (x - S[i, j] // 6) % 6
        c = (y - S[i, j] % 6) % 6
        pt = S[r, c]
        P[idx] = pt
        state.step(r, x, y, ct)
    return P


# ************************************************************
# * Core (public)
# ************************************************************

def encrypt(key, text, nonce="", alphabet=_DEFAULT_ALPHABET):
    index_lookup = {c: idx for idx, c in enumerate(alphabet)}
    K = np.array([index_lookup[x] for x in key.lower()])
    state = _State(K)
    _encrypt(state, np.array([index_lookup[x] for x in nonce.lower()]))
    P = np.array([index_lookup[x] for x in text.lower()])
    encrypted = "".join(alphabet[x] for x in _encrypt(state, P))
    return encrypted


def decrypt(key, text, nonce="", alphabet=_DEFAULT_ALPHABET):
    index_lookup = {c: idx for idx, c in enumerate(alphabet)}
    K = np.array([index_lookup[x] for x in key.lower()])
    state = _State(K)
    _encrypt(state, np.array([index_lookup[x] for x in nonce.lower()]))
    C = np.array([index_lookup[x] for x in text.lower()])
    decrypted = "".join(alphabet[x] for x in _decrypt(state, C))
    return decrypted


# ************************************************************
# * Interactive Command Line Interface
# ************************************************************

def _input_loop(prompt, strip=True, required=True):
    try:
        import readline
    except:
        pass
    while True:
        try:
            selection = _input(prompt)
            if strip:
                selection = selection.strip()
        except EOFError:
            sys.exit(1)
        except KeyboardInterrupt:
            # With readline, stdin is flushed after a KeyboarInterrupt.
            # Otherwise, exit.
            if 'readline' not in sys.modules:
                sys.exit(1)
            print()
            continue
        if required and not selection:
            continue
        break
    return selection


def _parse_args(argv):
    def positive_int_arg_type(val):
        int_val = int(val)
        if int_val <= 0:
            raise argparse.ArgumentTypeError("invalid positive int value: '{}'".format(val))
        return int_val

    def alphabet_arg_type(val):
        if len(val) != 36:
            raise argparse.ArgumentTypeError("alphabet must have 36 characters")
        if len(val) != len(set(val)):
            raise argparse.ArgumentTypeError("characters in alphabet must be unique")
        return val

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--version", action="version", version="lc4 {}".format(__version__))
    parser.add_argument(
        "-a", "--alphabet",
        default=_DEFAULT_ALPHABET,
        type=alphabet_arg_type,
        metavar="STRING",
        help="A string of 36 characters representing the alphabet."
    )
    parser.add_argument(
        "-n", "--nonce-length",
        default=6,
        type=positive_int_arg_type,
        metavar="INTEGER",
        help="The number of characters in randomly generated nonces when using option 2."
    )
    args = parser.parse_args(argv[1:])
    return args


def main(argv=sys.argv):
    args = _parse_args(argv)

    while True:
        print("1. Generate Key")
        print("2. Generate Nonce")
        print("3. Encrypt")
        print("4. Decrypt")
        print("5. Quit")
        selection = _input_loop(">>> ")
        if selection == "1":
            print("".join(random.sample(args.alphabet, 36)))
        elif selection == "2":
            nonce_chars = []
            for _ in _range(args.nonce_length):
                nonce_chars.extend(random.sample(args.alphabet, 1))
            print("".join(nonce_chars))
        elif selection in ("3", "4"):
            def validated_input(prompt, valid_chars):
                while True:
                    val = _input_loop(prompt)
                    diff = set(val) - valid_chars
                    if not diff:
                        return val
                    sys.stderr.write("Unsupported characters: {}\n".format("".join(diff)))

            valid_chars = set(args.alphabet)
            while True:
                key = validated_input("Key: ", valid_chars)
                valid_key = True
                if len(key) != len(args.alphabet):
                    valid_key = False
                    sys.stderr.write("Key must include exactly 36 characters.\n")
                missing_chars = set(args.alphabet) - set(key)
                if len(missing_chars) > 0:
                    valid_key = False
                    sys.stderr.write("Missing characters: {}\n".format("".join(missing_chars)))
                if valid_key:
                    break
            nonce = validated_input("Nonce: ", valid_chars)
            text = validated_input("Text: ", valid_chars)
            if selection == "3":
                print(encrypt(key, text, nonce=nonce))
            else:
                print(decrypt(key, text, nonce=nonce))
        elif selection == "5":
            pass
        else:
            print("Invalid selection: {}".format(selection))
            continue
        break

    return 0


if __name__ == "__main__":
    sys.exit(main())
