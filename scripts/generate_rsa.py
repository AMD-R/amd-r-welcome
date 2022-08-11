#!/usr/bin/env python3
"""
This module is used to generate RSA key pair used by AMD-R welcome.
"""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_key_pair(password: str = None,
                      key_options: dict = {
                          "public_exponent": 65537,
                          "key_size": 4096
                      },
                      private_file: str = None,
                      public_file: str = None) -> dict:
    # Generating Key
    key = rsa.generate_private_key(
        public_exponent=key_options["public_exponent"],
        key_size=key_options["key_size"],
    )

    # Setting up encryption
    encryption: serialization.KeySerializationEncryption
    if password:
        encryption = serialization.BestAvailableEncryption(bytes(password,
                                                                 'utf-8'))
    else:
        encryption = serialization.NoEncryption()

    # Wrting private key to a file
    if private_file is not None:
        export_private = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )
        with open(private_file, "wb") as f:
            f.write(export_private)

    # Wrting public key to a file
    if public_file is not None:
        export_public = key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1,
        )
        with open(public_file, "wb") as f:
            f.write(export_public)

    return {
        "private": key,
        "public": key.public_key()
    }
