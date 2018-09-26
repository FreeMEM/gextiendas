from M2Crypto import BIO, SMIME, X509, EVP
import os
from gluon import current
class PaypalCrypto(object):

    def __init__(self, attributes):
        self.attributes=attributes

    def paypalencrypt(self):

        plaintext = ''

        for key, value in self.attributes.items():
            plaintext += u'%s=%s\n' % (key, value)

        plaintext = plaintext.encode('utf-8')
        

        # Instantiate an SMIME object.
        s = SMIME.SMIME()

        # Load signer's key and cert. Sign the buffer.    
        s.pkey = EVP.load_key(os.path.join(current.request.folder,'private/paypal','priv_paypalgextiendas.pem'))
        s.x509 = X509.load_cert(os.path.join(current.request.folder,'private/paypal','pub_paypalgextiendas.pem'))

        p7 = s.sign(BIO.MemoryBuffer(plaintext), flags=SMIME.PKCS7_BINARY)

   
        x509 = X509.load_cert(os.path.join(current.request.folder,'private/paypal','paypal_cert_pem.txt'))

        sk = X509.X509_Stack()    
        sk.push(x509)    
        s.set_x509_stack(sk)

        # Set cipher: 3-key triple-DES in CBC mode.    
        s.set_cipher(SMIME.Cipher('des_ede3_cbc'))

        # Create a temporary buffer.    
        tmp = BIO.MemoryBuffer()

        # Write the signed message into the temporary buffer.    
        p7.write_der(tmp)

        # Encrypt the temporary buffer.    
        p7 = s.encrypt(tmp, flags=SMIME.PKCS7_BINARY)

        # Output p7 in mail-friendly format.    
        out = BIO.MemoryBuffer()    
        p7.write(out)

        return out.read()