from M2Crypto import SMIME, X509, BIO
import os, config, base64
from flask import json


def verify_pkcs7(pkcs7_sig, document):
    try:
        # raw_sig = pkcs7_sig
        raw_sig = str(pkcs7_sig).encode('ascii')
        msg = document

        sm_obj = SMIME.SMIME()
        x509 = X509.load_cert(os.path.join(config.APP_STATIC, 'AWSpubkey'))  # public key cert used by the remote
        # client when signing the message
        sk = X509.X509_Stack()
        sk.push(x509)
        sm_obj.set_x509_stack(sk)

        st = X509.X509_Store()
        st.load_info(os.path.join(config.APP_STATIC, 'AWSpubkey'))  # Public cert for the CA which signed
        # the above certificate
        sm_obj.set_x509_store(st)

        # re-wrap signature so that it fits base64 standards
        cooked_sig = '\n'.join(raw_sig[pos:pos + 76] for pos in xrange(0, len(raw_sig), 76))
        # cooked_sig = raw_sig
        # now, wrap the signature in a PKCS7 block
        sig = ("-----BEGIN PKCS7-----\n" + cooked_sig + "\n-----END PKCS7-----").encode('ascii')

        # and load it into an SMIME p7 object through the BIO I/O buffer:
        buf = BIO.MemoryBuffer(sig)
        p7 = SMIME.load_pkcs7_bio(buf)

        # finally, try to verify it:
        if dict(json.loads(sm_obj.verify(p7))) == dict(json.loads(msg)):
            return True
        else:
            return False
    except Exception as e:
        raise Exception("INVALID CLIENT MESSAGE SIGNATURE")
