import random as sysrandom
import string

from flowgram.core.base36 import int_to_base36

# Code modified from http://www.secureprogramming.com/?action=view&feature=recipes&recipeid=20
class SecureRandom(sysrandom.Random):
    def __init__(self):
        self.useBuiltInRandom = False
        self._file = None
        self.seed(None)

    def seed(self, ignore):
        if self._file:
            try:
                close(self._file)
            except:
                pass
        try:
            self._file = open('/dev/urandom', 'rb')
        except IOError:
            self.useBuiltInRandom = True

    def getstate(self):
        return None

    def setstate(self, ignore):
        pass

    def jumpahead(self, ignore):
        pass

    def random(self):
        """Returns a single random byte, using secure random if possible."""
        if self.useBuiltInRandom:
            return sysrandom.randint(0, 0xFF) # Use 255, not 256 here
        else:
            return ord(self._file.read(1))
            
    def random_bytes(self, num):
        """Returns a string of ``num'' random bytes, using secure random if possible."""
        if self.useBuiltInRandom:
            return ''.join(chr(sysrandom.randint(0, 0xFF)) for i in range(num))
        else:
            return self._file.read(num)

randomGenerator = SecureRandom()

alphabet = string.lowercase + string.digits # alphabet will become our base-32 character set

# We must remove 4 characters from alphabet to make it 32 characters long. We want it to be 32
# characters long so that we can use a whole number of bits from our random bytes to index into it.
for loser in 'l1o0': # Choose to remove ones that might be visually confusing
    i = alphabet.index(loser)
    alphabet = alphabet[:i] + alphabet[i+1:]

def byte_to_base32_chr(byte):
    return alphabet[ord(byte) & 31]

def secure_random_id(length):
    """Generates a random base-32 string of ``length'' characters. If
    /dev/random is available on the system, it will be used as a strong source
    of randomness. The base32 alphabet used is defined in ``alphabet''
    above."""
    return ''.join(map(byte_to_base32_chr, randomGenerator.random_bytes(length)))

def generateSecureRandomId(bytes):
    """Generates a secure random ID with the specified number of bytes of
    randomness. The ID generated will likely be longer than ``bytes'', because
    the numeric value is converted to base-36. I.e. 12 bytes becomes 19
    characters."""
    value = 0
    shift = 0
    usedBytes = 0
    while usedBytes < bytes:
        randomValue = randomGenerator.random()
        value += randomValue << shift
        shift += 8
        usedBytes += 1
    return int_to_base36(value)
