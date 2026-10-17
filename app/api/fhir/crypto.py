"""Per-patient AES-256-GCM image encryption with crypto-shredding (design D9).

Data keys are wrapped by APP_MASTER_KEY and live in a local key file, never in FHIR. Destroying a
patient's data key makes every ciphertext copy (including FHIR history versions) undecryptable.
Never log image bytes or keys.
"""
import base64
import json
import os
import uuid
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ALG = "AES-256-GCM"
KEY_FILE = Path(__file__).resolve().parent.parent / ".keys" / "keys.json"


class KeyDestroyed(Exception):
    """The patient's data key is gone (consent withdrawn) or never existed."""


def master_key_from_env():
    raw = os.environ.get("APP_MASTER_KEY")
    if not raw:
        raise RuntimeError("APP_MASTER_KEY is not set (base64 of 32 random bytes); refusing to start")
    key = base64.b64decode(raw)
    if len(key) != 32:
        raise RuntimeError("APP_MASTER_KEY must be base64 of exactly 32 bytes")
    return key


class KeyStore:
    def __init__(self, master_key, path=KEY_FILE):
        if len(master_key) != 32:
            raise ValueError("master key must be 32 bytes")
        self._master, self.path = AESGCM(master_key), Path(path)

    def _load(self):
        return json.loads(self.path.read_text()) if self.path.exists() else {}

    def _save(self, keys):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(keys))
        tmp.chmod(0o600)
        tmp.replace(self.path)

    def _data_key(self, patient_id):
        e = self._load().get(patient_id)
        if not e:
            raise KeyDestroyed(f"no data key for patient {patient_id}")
        raw = base64.b64decode(e["wrapped"])
        return e["key_id"], AESGCM(self._master.decrypt(raw[:12], raw[12:], e["key_id"].encode()))

    def encrypt(self, patient_id, data: bytes):
        """Returns (nonce||ciphertext||tag, key_id); creates the patient's data key on first use."""
        keys = self._load()
        if patient_id not in keys:
            kid, dk = str(uuid.uuid4()), AESGCM.generate_key(256)
            nonce = os.urandom(12)
            keys[patient_id] = {"key_id": kid, "wrapped": base64.b64encode(nonce + self._master.encrypt(nonce, dk, kid.encode())).decode()}
            self._save(keys)
        kid, aes = self._data_key(patient_id)
        nonce = os.urandom(12)  # fresh 96-bit nonce per encryption
        return nonce + aes.encrypt(nonce, data, patient_id.encode()), kid

    def decrypt(self, patient_id, blob: bytes, key_id):
        kid, aes = self._data_key(patient_id)
        if kid != key_id:
            raise KeyDestroyed(f"key {key_id} is not the current key for patient {patient_id}")
        try:
            return aes.decrypt(blob[:12], blob[12:], patient_id.encode())
        except InvalidTag as e:
            raise ValueError("image ciphertext failed authentication") from e

    def destroy(self, patient_id):
        keys = self._load()
        if keys.pop(patient_id, None) is not None:
            self._save(keys)
