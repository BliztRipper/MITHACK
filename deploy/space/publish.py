"""Create/update the Hugging Face Space and upload the assembled repo (live-demo-deployment task 3.3).

Run from the repo root, logged in with `hf auth login` (write token):
    DEMO_PASSWORDS='gp1:...,oph1:...,admin1:...' python3 deploy/space/publish.py [owner/space]
Fresh secrets are generated here and sent straight to the Space settings; they are never printed or written to disk.
Re-running keeps existing secrets unless ROTATE=1 (rotating APP_MASTER_KEY only matters before data exists).
"""
import base64
import os
import secrets
import subprocess
import sys

from huggingface_hub import HfApi

repo = sys.argv[1] if len(sys.argv) > 1 else "Blizt/retina-demo"
demo = os.environ.get("DEMO_PASSWORDS")
if not demo:
    sys.exit("set DEMO_PASSWORDS (the public demo logins, see the group-1 report)")

api = HfApi()
api.create_repo(repo, repo_type="space", space_sdk="docker", private=False, exist_ok=True)

existing = {s.key for s in api.get_space_secrets(repo)} if hasattr(api, "get_space_secrets") else set()
fresh = {
    "SESSION_SECRET": secrets.token_urlsafe(48),
    "APP_MASTER_KEY": base64.b64encode(secrets.token_bytes(32)).decode(),
    "IRIS_PASSWORD": secrets.token_hex(16),  # hex: safe for IRIS password rules
}
for key, value in fresh.items():
    if key not in existing or os.environ.get("ROTATE") == "1":
        api.add_space_secret(repo, key, value)
api.add_space_variable(repo, "DEMO_PASSWORDS", demo)  # public by design (spec public-demo)
api.add_space_variable(repo, "BOOT_DEADLINE_S", "600")  # cold IRIS boot on the shared CPU can exceed 300 s

folder = subprocess.run(["sh", "deploy/space/assemble.sh"], check=True, capture_output=True, text=True).stdout.strip()
api.upload_folder(repo_id=repo, repo_type="space", folder_path=folder, commit_message="Deploy retina demo",
                  delete_patterns=["*"])
owner, name = repo.split("/")
print(f"uploaded {folder} -> {repo}; build log: Space page > Logs; app: https://{owner.lower()}-{name}.hf.space/health")
