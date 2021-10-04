import random
import re
from crypto_utils import extended_gcd, modular_inverse, generate_random_prime, blocks_from_text, text_from_blocks

__author__ = "Peter Skaar Nordby"


class Cipher():
    """Cipher superclass with dummy methods for generating keys, encoding and decoding and method for verifying the cipher
    """
    alphabet_size = 95
    alphabet_start = 32
    alphabet_end = 126

    def generate_key(self):
        pass

    def encode(self, key, msg):
        pass

    def decode(self, key, msg):
        pass

    def verify(self, key, msg):
        return msg == self.decode(key, self.encode(key, msg))


class Caesar(Cipher):
    """Uses key to shift alphabet by a number of places
    """

    def generate_key(self):
        """Generates a random key between 0 and the size of the alphabet

        Returns:
            int: key
        """
        return random.randint(0, self.alphabet_size)

    def encode(self, key, msg):
        """Encodes the message with the given key

        Args:
            key (int): The encoding key
            msg (str): The message to be encoded

        Returns:
            str: Encoded message
        """
        encoded_msg = ""
        for char in msg:
            encoded_msg += chr((ord(char) + key - self.alphabet_start) %
                               self.alphabet_size + self.alphabet_start)
        return encoded_msg

    def decode(self, key, msg):
        """Decodes the message with the given key

        Args:
            key (int): The encoding key
            msg (str): The message to be decoded

        Returns:
            str: Decoded message"""
        decoding_key = self.alphabet_size - key
        return self.encode(decoding_key, msg)


class Multiplication(Cipher):
    """Uses key to map each letter to a new letter by multiplication
    """

    def generate_key(self):
        """Generates random valid key between 0 and the size of the alphabet

        Returns:
            int: key
        """
        key = random.randint(0, self.alphabet_size)
        while extended_gcd(key, self.alphabet_size)[0] != 1:
            key = random.randint(0, self.alphabet_size)
        return key

    def encode(self, key, msg):
        """Encodes the message with the given key

        Args:
            key (int): The encoding key
            msg (str): The message to be encoded

        Returns:
            str: Encoded message
        """
        encoded_msg = ""
        for char in msg:
            encoded_msg += chr((ord(char) * key - self.alphabet_start) %
                               self.alphabet_size + self.alphabet_start)
        return encoded_msg

    def decode(self, key, msg):
        """Decodes the message with the given key

        Args:
            key (int): The encoding key
            msg (str): The message to be decoded

        Returns:
            str: Decoded message
        """
        mod_inverse = modular_inverse(key, self.alphabet_size)
        return self.encode(mod_inverse, msg)


class Affine(Cipher):
    """Uses a combination of caesar and multiplication
    """
    caesar = Caesar()
    multiplication = Multiplication()

    def generate_key(self):
        """Generates random key based on ceasar and mulitplication ciphers

        Returns:
            tuple: key pair
        """
        return (self.multiplication.generate_key(), self.caesar.generate_key())

    def encode(self, key, msg):
        """Encodes the message with the given key pair

        Args:
            key (tuple): The encoding key
            msg (str): The message to be encoded

        Returns:
            str: Encoded message
        """
        return self.caesar.encode(key[1], self.multiplication.encode(key[0], msg))

    def decode(self, key, msg):
        """Decodes the message with the given key pair

        Args:
            key (tuple): The encoding key
            msg (str): The message to be decoded

        Returns:
            str: Decoded message
        """
        return self.multiplication.decode(key[0], self.caesar.decode(key[1], msg))


class Unbreakable(Cipher):
    """Uses keywoard to avoid cracking by looking at letter frequency
    """

    def generate_key(self):
        """Generates key based on an input word

        Returns:
            list: key
        """
        keyword = input("Keyword: ")
        key = []
        for char in keyword:
            key.append(ord(char))
        return key

    def encode(self, key, msg):
        """Encodes the message with the given key

        Args:
            key (list): The encoding key
            msg (str): The message to be encoded

        Returns:
            str: Encoded message
        """
        encoded_msg = ""
        for i, char in enumerate(msg):
            encoded_msg += chr((ord(char) + key[i % len(key)] - self.alphabet_start) %
                               self.alphabet_size + self.alphabet_start)
        return encoded_msg

    def decode(self, key, msg):
        """Decodes the message with the given key

        Args:
            key (list): The encoding key
            msg (str): The message to be decoded

        Returns:
            str: Decoded message
        """
        decoding_key = []
        for val in key:
            decoding_key.append((self.alphabet_size - val) %
                                self.alphabet_size)
        return self.encode(decoding_key, msg)


class RSA(Cipher):
    """Uses private and public keys to encrypt message
    """
    bits = 8
    block_length = 2

    def generate_key(self):
        """Generates key pairs based on random primes

        Returns:
            tuple: public and private key pair
        """
        p = generate_random_prime(self.bits)
        q = generate_random_prime(self.bits)
        while q == p:
            q = generate_random_prime(self.bits)
        n = p * q
        phi = (p-1) * (q-1)
        e = random.randint(3, phi-1)
        while extended_gcd(e, phi)[0] != 1:
            e = random.randint(3, phi-1)
        d = modular_inverse(e, phi)
        return (n, e), (n, d)

    def encode(self, key, msg):
        """Encodes the message with the given key

        Args:
            key (tuple): The encoding key
            msg (str): The message to be encoded

        Returns:
            list: Encoded message in list of integers
        """
        encoded_msg = []
        n = key[0]
        e = key[1]
        blocks = blocks_from_text(msg, self.block_length)
        for block in blocks:
            encoded_msg.append((block ** e) % n)
        return encoded_msg

    def decode(self, key, msg):
        """Decodes the message with the given key

        Args:
            key (tuple): The decoding key
            msg (str): List of integers to be decoded

        Returns:
            str: Decoded message
        """
        decoded_msg = []
        n = key[0]
        d = key[1]
        for block in msg:
            decoded_msg.append((block ** d) % n)
        return text_from_blocks(decoded_msg, self.block_length)

    def verify(self, key, msg):
        return msg == self.decode(key[1], self.encode(key[0], msg))


class Person():
    """Person super class
    """

    def __init__(self, cipher):
        self.key = None
        self.cipher = cipher

    def set_key(self, key):
        self.key = key

    def get_key(self):
        return self.key

    def operate_cipher(self, msg):
        pass


class Sender(Person):
    def operate_cipher(self, msg):
        """Encodes the given message with Persons chosen Cipher

        Args:
            msg (str): The message to be encoded

        Returns:
            str: Encoded message
        """
        return self.cipher.encode(self.key, msg)


class Receiver(Person):
    def operate_cipher(self, msg):
        """Decodes the given message with Persons chosen Cipher

        Args:
            msg (str): The message to be decoded

        Returns:
            str: Decoded message
        """
        return self.cipher.decode(self.key, msg)


class Hacker(Receiver):
    """Hacker class to brute force the various Ciphers
    """

    def __init__(self, encoded_msg, cipher):
        super().__init__(cipher)
        self.encoded_msg = encoded_msg
        self.most_likely_msg = ""
        self.max_count = 0
        file = open("english_words.txt")
        contents = file.read()
        self.words = set(contents.split("\n"))
        file.close()

    def count_english_words(self, decoded_msg):
        """Counts the number of english words in the decoded message

        Args:
            decoded_msg (str): Decoded message

        Returns:
            int: Number of english words
        """
        decoded_msg = re.sub("[^0-9a-zA-Z]+", " ", decoded_msg)
        decoded_msg_list = decoded_msg.split()
        count = 0
        for word in decoded_msg_list:
            if word.lower() in self.words:
                count += 1
        return count

    def check_key(self, key):
        """Checks if this key is possible

        Args:
            key (int/tuple/list): The key to check
        """
        self.key = key
        decoded_msg = self.operate_cipher(self.encoded_msg)
        count = self.count_english_words(decoded_msg)
        if count > self.max_count:
            self.max_count = count
            self.most_likely_msg = decoded_msg

    def brute_force(self):
        """Brute forces all possible keys to find possible original message

        Returns:
            str: Most likely original message
        """
        if isinstance(self.cipher, (Caesar, Multiplication)):
            for key in range(0, self.cipher.alphabet_size):
                if isinstance(self.cipher, Multiplication) and extended_gcd(key, self.cipher.alphabet_size)[0] != 1:
                    continue
                self.check_key(key)
            return self.most_likely_msg, self.max_count

        if isinstance(self.cipher, Affine):
            for c_key in range(0, self.cipher.alphabet_size):
                for m_key in range(0, self.cipher.alphabet_size):
                    if extended_gcd(m_key, self.cipher.alphabet_size)[0] != 1:
                        continue
                    self.check_key((m_key, c_key))
            return self.most_likely_msg, self.max_count

        if isinstance(self.cipher, Unbreakable):
            for word in self.words:
                try:
                    encryption_key = []
                    for char in word:
                        encryption_key.append(ord(char))
                    self.check_key(encryption_key)
                except ZeroDivisionError:
                    continue
            return self.most_likely_msg, self.max_count


def test():
    cipher_choice = input("What cipher do you want to use? (c, m, a, u, r) ")
    cipher_map = {"c": Caesar(), "m":  Multiplication(), "a": Affine(), "u": Unbreakable(), "r": RSA()}
    cipher = cipher_map[cipher_choice.lower().strip()]
    key = cipher.generate_key()

    msg = input("What message do you want to send? ")
    print("Key:", key, "\nMessage:", msg, "\n")
    sender = Sender(cipher)
    sender.set_key(key)
    receiver = Receiver(cipher)
    receiver.set_key(key)
    if isinstance(cipher, RSA):
        sender.set_key(key[0])
        receiver.set_key(key[1])
    encrypted = sender.operate_cipher(msg)
    print("Encrypted:", encrypted)
    decrypted = receiver.operate_cipher(encrypted)
    print("Decrypted:", decrypted)
    print("Encryption and decryption succesfull:", cipher.verify(key, msg))
    if not isinstance(cipher, RSA):
        hacker = Hacker(encrypted, cipher)
        brute_forced = hacker.brute_force()
        print("\nBrute forced:", brute_forced[0], "\nEnglish words:", brute_forced[1])


test()
