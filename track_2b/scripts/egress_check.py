"""Try to leave the container: DNS, raw TCP and HTTPS. Prints one line per probe."""

import socket
import sys

socket.setdefaulttimeout(5)
results = {}
try:
    results["dns huggingface.co"] = socket.gethostbyname("huggingface.co")
except OSError as e:
    results["dns huggingface.co"] = f"FAILED ({type(e).__name__}: {e})"
try:
    socket.create_connection(("1.1.1.1", 443)).close()
    results["tcp 1.1.1.1:443"] = "connected"
except OSError as e:
    results["tcp 1.1.1.1:443"] = f"FAILED ({type(e).__name__}: {e})"
try:
    import httpx

    r = httpx.get("https://huggingface.co", timeout=5)
    results["https huggingface.co"] = f"HTTP {r.status_code}"
except Exception as e:
    results["https huggingface.co"] = f"FAILED ({type(e).__name__})"
for k, v in results.items():
    print(f"egress {k}: {v}")
blocked = all(v.startswith("FAILED") for v in results.values())
print("egress verdict:", "BLOCKED (no internet)" if blocked else "REACHABLE")
sys.exit(0 if blocked or "--expect-open" in sys.argv else 1)
