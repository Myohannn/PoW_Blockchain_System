from ecdsa import SigningKey, VerifyingKey, SECP256k1


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
