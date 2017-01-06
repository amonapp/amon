import unittest
from nose.tools import eq_
from amon.utils.security import AESCipher

from faker import Factory
fake = Factory.create()


class EncryptDecryptTest(unittest.TestCase):

    def setUp(self):
        self.aes_cipher = AESCipher()


    def test_encrypt_decrypt(self):


        for i in range(0, 100):
            name = fake.name()

            encrypted_string = self.aes_cipher.encrypt(name)
            decrypted_message = self.aes_cipher.decrypt(encrypted_string)
            print(decrypted_message)
            eq_(name, decrypted_message)
            
        for i in range(0, 100):
            text = fake.text(max_nb_chars=200)

            encrypted_string = self.aes_cipher.encrypt(text)
            decrypted_message = self.aes_cipher.decrypt(encrypted_string)
            eq_(text, decrypted_message)

        for i in range(0, 100):
            text = fake.text(max_nb_chars=200)

            encrypted_string = self.aes_cipher.encrypt(name)
            decrypted_message = self.aes_cipher.decrypt(encrypted_string)
            eq_(name, decrypted_message)