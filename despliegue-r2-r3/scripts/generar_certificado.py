"""Crea una autoridad certificadora local y un certificado TLS para agenda.localhost.

Uso: python scripts/generar_certificado.py <carpeta_destino>
Genera ca-local.crt, agenda.crt y agenda.key. La llave privada nunca se versiona.
"""
import ipaddress
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

DOMINIOS = ['agenda.localhost', 'localhost']


def main(destino):
    destino.mkdir(parents=True, exist_ok=True)
    ahora = datetime.now(timezone.utc)
    llave_ca = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nombre_ca = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Agenda Academica CA local')])
    ca = (x509.CertificateBuilder().subject_name(nombre_ca).issuer_name(nombre_ca)
          .public_key(llave_ca.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(ahora - timedelta(days=1)).not_valid_after(ahora + timedelta(days=365))
          .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
          .add_extension(x509.KeyUsage(False, False, False, False, False, True, True, False, False), critical=True)
          .sign(llave_ca, hashes.SHA256()))
    llave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nombres = [x509.DNSName(d) for d in DOMINIOS] + [x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]
    cert = (x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, DOMINIOS[0])]))
            .issuer_name(nombre_ca).public_key(llave.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(ahora - timedelta(days=1)).not_valid_after(ahora + timedelta(days=397))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(x509.SubjectAlternativeName(nombres), critical=False)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .sign(llave_ca, hashes.SHA256()))
    (destino / 'ca-local.crt').write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    (destino / 'agenda.crt').write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    (destino / 'agenda.key').write_bytes(llave.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    print(f'Certificado para {", ".join(DOMINIOS)} válido hasta {cert.not_valid_after_utc:%d/%m/%Y}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Uso: python scripts/generar_certificado.py <carpeta_destino>')
    main(Path(sys.argv[1]))
