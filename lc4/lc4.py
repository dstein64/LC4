from __future__ import print_function

import argparse
import sys

import numpy as np

_ALPHABET = list("#_23456789abcdefghijklmnopqrstuvwxyz")
_INDEX_LOOKUP = {val: idx for idx, val in enumerate(_ALPHABET)}


class _State:
    def __init__(self, K):
        self.S = np.empty((6, 6), dtype=int)
        for k in range(36):
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


def encrypt(key, nonce, text, signature="", header=""):
    K = np.array([_INDEX_LOOKUP[x] for x in key.lower()])
    state = _State(K)
    _encrypt(state, np.array([_INDEX_LOOKUP[x] for x in nonce.lower()]))
    _encrypt(state, np.array([_INDEX_LOOKUP[x] for x in header.lower()]))
    P = np.array([_INDEX_LOOKUP[x] for x in (text + signature).lower()])
    encrypted = ''.join(_ALPHABET[x] for x in _encrypt(state, P))
    return encrypted


def decrypt(key, nonce, text, header=""):
    K = np.array([_INDEX_LOOKUP[x] for x in key.lower()])
    state = _State(K)
    _encrypt(state, np.array([_INDEX_LOOKUP[x] for x in nonce.lower()]))
    _encrypt(state, np.array([_INDEX_LOOKUP[x] for x in header.lower()]))
    C = np.array([_INDEX_LOOKUP[x] for x in text.lower()])
    decrypted = ''.join(_ALPHABET[x] for x in _decrypt(state, C))
    return decrypted


def main(argv=sys.argv):
    print(argv)
    key = "xv7ydq#opaj_39rzut8b45wcsgehmiknf26l"
    nonce = "solwbf"
    text = "im_about_to_put_the_hammer_down"
    signature = "#rubberduck"

    encrypted = encrypt(key, nonce, text, signature=signature)
    print("Encrypted: {}".format(encrypted))

    decrypted = decrypt(key, nonce, encrypted)
    print("Decrypted: {}".format(decrypted))


if __name__ == "__main__":
    sys.exit(main())
