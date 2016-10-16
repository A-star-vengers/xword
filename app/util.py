from binascii import hexlify
from os import urandom
from Crypto.Hash import SHA256


def getsalt():
    'Generate a 32 bytestring based off of a random 16 byte string.'
    return hexlify(urandom(16))


def createhash(salt, password):
    'Apply SHA256 on salt + password and return 128 byte string.'
    thehash = SHA256.new(salt + password)
    return thehash.hexdigest()


def validate_table(table, source):
    'Validates POST arguments from a request'
    valid = True
    for entry in table:
        if entry not in source:
            valid = False
            break
    return valid
