"""Per-patient AES-256-GCM image encryption with crypto-shredding (design D9).

Data keys are wrapped by APP_MASTER_KEY and live in a local key file, never in FHIR. Destroying a
patient's data key makes every ciphertext copy (including FHIR history versions) undecryptable.
Never log image bytes or keys.
"""
import base64
import contextlib
import fcntl
import json
import os
import threading
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


def _pid(patient_id):
    return patient_id.rsplit("/", 1)[-1]  # accept "Patient/123" and "123"


class ConsentWithdrawn(KeyDestroyed):
    """A new data key is refused for a patient whose consent was withdrawn."""


class KeyStore:
    _lock = threading.Lock()  # in-process; flock below covers other processes

    def __init__(self, master_key, path=KEY_FILE):
        if len(master_key) != 32:
            raise ValueError("master key must be 32 bytes")
        self._master, self.path = AESGCM(master_key), Path(path)

    def _load(self):
        d = json.loads(self.path.read_text()) if self.path.exists() else {}
        return d.setdefault("keys", {}), d.setdefault("withdrawn", []), d

    @contextlib.contextmanager
    def _txn(self):
        """Serialised load-modify-save; atomic replace so readers never see a partial file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, open(self.path.with_suffix(".lock"), "a") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            keys, withdrawn, whole = self._load()
            yield keys, withdrawn
            tmp = self.path.with_suffix(".tmp")
            fd = os.open(tmp, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)  # never world-readable
            with os.fdopen(fd, "w") as f:
                json.dump(whole, f)
            os.replace(tmp, self.path)

    def _data_key(self, patient_id):
        e = self._load()[0].get(_pid(patient_id))
        if not e:
            raise KeyDestroyed(f"no data key for patient {_pid(patient_id)}")
        raw = base64.b64decode(e["wrapped"])
        return e["key_id"], AESGCM(self._master.decrypt(raw[:12], raw[12:], e["key_id"].encode()))

    def encrypt(self, patient_id, data: bytes):
        """Returns (nonce||ciphertext||tag, key_id); creates the patient's data key on first use."""
        pid = _pid(patient_id)
        with self._txn() as (keys, withdrawn):
            if pid in withdrawn:
                raise ConsentWithdrawn(f"consent withdrawn for patient {pid}")
            if pid not in keys:
                kid, dk = str(uuid.uuid4()), AESGCM.generate_key(256)
                nonce = os.urandom(12)
                keys[pid] = {"key_id": kid, "wrapped": base64.b64encode(nonce + self._master.encrypt(nonce, dk, kid.encode())).decode()}
        kid, aes = self._data_key(pid)
        nonce = os.urandom(12)  # fresh 96-bit nonce per encryption
        return nonce + aes.encrypt(nonce, data, pid.encode()), kid

    def decrypt(self, patient_id, blob: bytes, key_id):
        pid = _pid(patient_id)
        kid, aes = self._data_key(pid)
        if kid != key_id:
            raise KeyDestroyed(f"key {key_id} is not the current key for patient {pid}")
        try:
            return aes.decrypt(blob[:12], blob[12:], pid.encode())
        except InvalidTag as e:
            raise ValueError("image ciphertext failed authentication") from e

    def destroy(self, patient_id):
        """Destroys the key and tombstones the patient (no new key). Returns True if a key existed."""
        pid = _pid(patient_id)
        with self._txn() as (keys, withdrawn):
            if pid not in withdrawn:
                withdrawn.append(pid)
            return keys.pop(pid, None) is not None

    def withdrawn(self, patient_id):
        return _pid(patient_id) in self._load()[1]

    def has_key(self, patient_id, key_id=None):
        e = self._load()[0].get(_pid(patient_id))
        return bool(e) and (key_id is None or e["key_id"] == key_id)
