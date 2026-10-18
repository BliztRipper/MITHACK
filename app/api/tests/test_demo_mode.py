"""live-demo-deployment group 1: the API as a public demo (DEMO_MODE=1)."""
import os
import subprocess
import sys

import deps

ML = ("torch", "torchvision", "timm", "cv2", "pytorch_grad_cam", "efficientnet_pytorch")


def test_import_main_loads_no_ml_stack():
    """1.1: with no model configured, the API (and a cached analysis) imports neither torch nor OpenCV."""
    code = ("import sys, json, main, analysis, routes.monitoring\n"
            "from fhir import seed\n"
            "img = json.loads((analysis.CACHE / '33c3877c97c56ec2845cd339e1bea4becb65c4b64f24a424254d3854318e9f38' / 'meta.json').read_text())\n"
            "assert analysis.cache_get('33c3877c97c56ec2845cd339e1bea4becb65c4b64f24a424254d3854318e9f38', main.deps.model())\n"
            "analysis.emergency(img, {}, 2, True, False, None)\n"
            f"print(sorted(m for m in {ML!r} if m in sys.modules))\n")
    env = {k: v for k, v in os.environ.items() if k != "CRAO_MODEL"} | {"DEMO_MODE": "1"}
    out = subprocess.run([sys.executable, "-c", code], cwd=deps.API, env=env, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "[]"
