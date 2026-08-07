#!/usr/bin/env python3
"""Localhost helper for autonomous job applications.

Serves:
  GET /            -> HTML bootstrap page that reads the resume into window.name
                      as a base64 data URL, so it survives cross-origin navigation
                      to the ATS form (where CSP blocks fetching localhost directly).
  GET /resume.pdf  -> the resume bytes (same-origin fetch from the bootstrap page).

Bound to 127.0.0.1 only. Serves nothing but the resume."""
import base64, http.server, socketserver, os

PORT = 8765
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resume_path():
    """config/profile.json -> resume, relative to the repo root. Falls back to data/resume.pdf."""
    import json
    try:
        with open(os.path.join(REPO_ROOT, "config", "profile.json")) as f:
            rel = json.load(f).get("resume") or "data/resume.pdf"
    except Exception:
        rel = "data/resume.pdf"
    return os.path.join(REPO_ROOT, rel)


RESUME = _resume_path()
FILENAME = os.path.basename(RESUME)

BOOTSTRAP = """<!doctype html><meta charset=utf-8><title>resume-bootstrap</title>
<body>bootstrapping resume...</body>
<script>
fetch('/resume.pdf',{cache:'no-store'}).then(r=>r.arrayBuffer()).then(buf=>{
  let bin=''; const b=new Uint8Array(buf);
  for(let i=0;i<b.length;i++) bin+=String.fromCharCode(b[i]);
  window.name = 'RESUMEB64:' + btoa(bin);
  document.body.textContent = 'ready:' + b.length + ' bytes in window.name';
}).catch(e=>{document.body.textContent='error:'+e});
</script>"""

class H(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
    def do_GET(self):
        if self.path.startswith("/resume.pdf"):
            try:
                with open(RESUME, "rb") as f: data = f.read()
            except OSError:
                self.send_response(404); self.end_headers(); return
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", str(len(data)))
            self._cors(); self.end_headers(); self.wfile.write(data)
        else:
            body = BOOTSTRAP.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass

with socketserver.TCPServer(("127.0.0.1", PORT), H) as httpd:
    print(f"serving on http://127.0.0.1:{PORT}")
    httpd.serve_forever()
