from __future__ import print_function

from lc4 import encrypt, decrypt

key = "xv7ydq#opaj_39rzut8b45wcsgehmiknf26l"
nonce = "solwbf"
text = "im_about_to_put_the_hammer_down"
signature = "#rubberduck"

encrypted = encrypt(key, text + signature, nonce=nonce)
print("Encrypted: {}".format(encrypted))

decrypted = decrypt(key, encrypted, nonce=nonce)
print("Decrypted: {}".format(decrypted))
