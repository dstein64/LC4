from lc4 import encrypt, decrypt

key = '#qiye7hozcb2asm5kd9x_nlvrwput6f3j84g'
nonce = 'mi2zwe'
text = 'this_is_an_example'

encrypted = encrypt(key, text, nonce=nonce, verbose=True)
decrypted = decrypt(key, encrypted, nonce=nonce, verbose=True)
