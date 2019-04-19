import unittest
from lc4 import encrypt, decrypt

class TestLC4(unittest.TestCase):
    """LC4 tests using the example from the paper."""
    KEY = 'xv7ydq#opaj_39rzut8b45wcsgehmiknf26l'
    NONCE = 'solwbf'
    MESSAGE = 'im_about_to_put_the_hammer_down'
    SIGNATURE = '#rubberduck'
    TEXT = MESSAGE + SIGNATURE
    CIPHERTEXT = 'i2zqpilr2yqgptltrzx2_9fzlmbo3y8_9pyssx8nf2'

    def test_encrypt(self):
        encrypted = encrypt(
            TestLC4.KEY,
            TestLC4.TEXT,
            nonce=TestLC4.NONCE)
        self.assertEqual(encrypted, TestLC4.CIPHERTEXT)

    def test_decrypt(self):
        decrypted = decrypt(
            TestLC4.KEY,
            TestLC4.CIPHERTEXT,
            nonce=TestLC4.NONCE)
        self.assertEqual(decrypted, TestLC4.TEXT)

if __name__ == '__main__':
    unittest.main()
