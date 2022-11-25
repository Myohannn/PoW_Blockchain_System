from ecdsa import SigningKey, VerifyingKey, SECP256k1


# SECP384R1


# sk = SigningKey.generate(curve=SECP256k1)
# vk = sk.verifying_key
# with open("private.pem", "wb") as f:
#     f.write(sk.to_pem())
# with open("public.pem", "wb") as f:
#     f.write(vk.to_pem())


def sign(sk, message):
    signature = sk.sign(message)
    return signature


def verify(vk, signature, message):
    try:
        vk.verify(signature, message)
    except:
        return "false"
    else:
        return "true"


def main():
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.verifying_key
    message = b'We are PolyU, Together We Excel!'
    signature = sign(sk, message)

    ver_res = verify(vk, signature, message)
    print(f'verification: {ver_res}')


def genKey():
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.verifying_key
    with open("keypair/private4.pem", "wb") as f:
        f.write(sk.to_pem())
    with open("keypair/public4.pem", "wb") as f:
        f.write(vk.to_pem())


def loadKey(index):
    sk_path = f"keypair/private{index}.pem"
    with open(sk_path) as f:
        sk = SigningKey.from_pem(f.read())

    vk_path = f"keypair/public{index}.pem"
    with open(vk_path) as f:
        a = f.read()
        vk = VerifyingKey.from_pem(a)
        # print(a)
    return sk, vk

# sk, vk = loadKey(1)
# # message = b"cnm"
# # with open("message", "wb") as f:
# #     f.write(message)
# # sig = sk.sign(message)
# # with open("signature", "wb") as f:
# #     f.write(sig)
#
# print("private key:",sk)
# # print(vk)
#
#
# with open("message", "rb") as f:
#     message = f.read()
# with open("signature", "rb") as f:
#     sig = f.read()
# try:
#     vk.verify(sig, message)
#     print("good signature")
# except:
#     print("BAD SIGNATURE")
