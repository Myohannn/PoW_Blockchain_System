import time

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from os import chmod


def key_gen():
    # generate the private key
    private_key = rsa.generate_private_key(backend=crypto_default_backend(),
                                           public_exponent=65537,
                                           key_size=2048)
    # derive the public key
    public_key = private_key.public_key()

    return (private_key, public_key)


def encrypt(pk, message):
    # encrypt the message using the public key
    # the message should be padded
    ciphertext = pk.encrypt(
        message,
        padding.OAEP(padding.MGF1(algorithm=hashes.SHA256()), hashes.SHA256(),
                     None))
    return ciphertext


def decrypt(sk, ciphertext):
    # decrypt the ciphertext using the private key
    # the decrypted plaintext should be unpadded
    plaintext = sk.decrypt(
        ciphertext,
        padding.OAEP(padding.MGF1(algorithm=hashes.SHA256()), hashes.SHA256(),
                     None))
    return plaintext


def saveKey(sk):
    # get private key in PEM container format
    # pem = sk.private_bytes(encoding=serialization.Encoding.PEM,
    #                        format=serialization.PrivateFormat.TraditionalOpenSSL,
    #                        encryption_algorithm=serialization.NoEncryption())

    pem = sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    print("Old pem",pem)

    with open("private.pem", 'wb') as content_file:
        content_file.write(pem)
    print("Key saved")
    return pem


def loadKey():
    with open("private.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    pem2 = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    newkey = serialization.load_pem_private_key(pem2,password=None)
    print("New pem1",newkey)
    newkey = serialization.load_pem_private_key(pem2, password=None)
    print("New pem2", newkey)
    return newkey


def main():
    # generate the keypair
    sk, pk = key_gen()
    print("sk", sk)
    print("pk", pk)
    pem = saveKey(sk)

    time.sleep(5)

    newsk = loadKey()
    # newpk = newsk.public_key()
    print("newsk", newsk)
    # print("newpk", newpk)

    if (newsk == pem):
        print("same")
    else:
        print("different")

    # if(newpk == pk):
    #     print("same")
    # else:
    #     print("different")

    # # encrypt the message 'This is COMP5521' under RSA, getting the ciphertext
    # ciphertext = encrypt(pk, b'We are PolyU, Together We Excel!')
    # print(f'ciphertext:\t {ciphertext.hex()}')
    #
    # # decrypte the ciphertext, getting the plaintext
    # plaintext = decrypt(sk, ciphertext)
    # print(f'plaintext:\t {plaintext.decode("utf-8")}')


if __name__ == '__main__':
    main()
