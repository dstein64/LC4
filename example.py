from __future__ import print_function

from lc4 import encrypt, decrypt

key = "#qiye7hozcb2asm5kd9x_nlvrwput6f3j84g"
nonce = "mi2zwe"
text = "this_is_an_example"

encrypted = encrypt(key, text, nonce=nonce)
print("Encrypted: {}".format(encrypted))

decrypted = decrypt(key, encrypted, nonce=nonce)
print("Decrypted: {}".format(decrypted))
