import base64
import os

import cv2
import numpy as np
import pytest

from fhir import mapping as m
from fhir.crypto import KeyDestroyed, KeyStore, master_key_from_env


@pytest.fixture
def ks(tmp_path):
    return KeyStore(os.urandom(32), tmp_path / "keys.json")


def _png():
    ok, buf = cv2.imencode(".png", np.random.randint(0, 255, (32, 32, 3), np.uint8))
    return buf.tobytes()


def test_round_trip_fresh_nonce_and_tamper(ks):
    img = _png()
    a, kid = ks.encrypt("p1", img)
    b, _ = ks.encrypt("p1", img)
    assert a[:12] != b[:12] and a != b
    assert ks.decrypt("p1", a, kid) == img
    with pytest.raises(ValueError):
        ks.decrypt("p1", a[:-1] + bytes([a[-1] ^ 1]), kid)
    with pytest.raises(ValueError):  # ciphertext bound to the patient (AAD)
        ks.decrypt("p2", a, ks.encrypt("p2", img)[1])


def test_key_file_holds_only_wrapped_keys(ks, tmp_path):
    ks.encrypt("p1", b"x")
    assert (tmp_path / "keys.json").stat().st_mode & 0o777 == 0o600
    other = KeyStore(os.urandom(32), tmp_path / "keys.json")
    with pytest.raises(Exception):  # wrong master key cannot unwrap
        other.decrypt("p1", b"0" * 40, "x")


def test_destroy_makes_data_undecryptable(ks):
    blob, kid = ks.encrypt("p1", b"secret")
    ks.destroy("p1")
    with pytest.raises(KeyDestroyed):
        ks.decrypt("p1", blob, kid)
    ks.encrypt("p1", b"secret")  # a new key is not the old one
    with pytest.raises(KeyDestroyed):
        ks.decrypt("p1", blob, kid)


def test_master_key_required(monkeypatch):
    monkeypatch.delenv("APP_MASTER_KEY", raising=False)
    with pytest.raises(RuntimeError, match="APP_MASTER_KEY"):
        master_key_from_env()
    monkeypatch.setenv("APP_MASTER_KEY", base64.b64encode(b"short").decode())
    with pytest.raises(RuntimeError, match="32 bytes"):
        master_key_from_env()


@pytest.mark.fhir
def test_stored_media_is_not_an_image_and_decrypts(fhir, ks):
    img = _png()
    pat = fhir.create(m.patient("TEST-CRYPTO", "Testcrypto", "A", "female", "1980-01-01"))
    pid = pat["id"]
    prac = fhir.create(m.practitioner("test-crypto", "Testprac", "C"))
    enc = fhir.create(m.encounter(f"Patient/{pid}", "screening", f"Practitioner/{prac['id']}"))
    try:
        blob, kid = ks.encrypt(pid, img)
        med = fhir.create(m.media(f"Patient/{pid}", f"Encounter/{enc['id']}", blob, kid))
        stored = base64.b64decode(fhir.read("Media", med["id"])["content"]["data"])
        assert stored == blob and img not in stored
        assert cv2.imdecode(np.frombuffer(stored, np.uint8), cv2.IMREAD_COLOR) is None
        assert cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR) is not None
        ext = fhir.read("Media", med["id"])["extension"][0]["extension"]
        assert {e["url"]: e["valueString"] for e in ext} == {"algorithm": "AES-256-GCM", "keyId": kid}
        assert ks.decrypt(pid, stored, kid) == img
    finally:
        for t, i in (("Media", med["id"]), ("Encounter", enc["id"]), ("Practitioner", prac["id"]), ("Patient", pid)):
            fhir.delete(t, i)
