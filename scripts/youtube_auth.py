#!/usr/bin/env python3
"""
One-time YouTube sign-in. Run this on YOUR OWN computer (it opens a browser).

    python3 scripts/youtube_auth.py CLIENT_ID CLIENT_SECRET

CLIENT_ID / CLIENT_SECRET come from a Google Cloud "Desktop app" OAuth client with the
YouTube Data API v3 enabled. You sign in with the Google account that owns the channel and
allow "Manage your YouTube videos" (upload only). The script prints a refresh token.

Store the three values as environment variables in the cloud environment's settings
(never paste them into a chat):
    YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN
Standard library only: nothing to install.
"""
import http.server
import json
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser

SCOPE = "https://www.googleapis.com/auth/youtube.upload"
PORT = 8765
REDIRECT = f"http://127.0.0.1:{PORT}/"


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    client_id, client_secret = sys.argv[1], sys.argv[2]
    state = secrets.token_urlsafe(16)
    got = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get("state", [""])[0] == state and "code" in q:
                got["code"] = q["code"][0]
                msg = "Done. You can close this tab and go back to the terminal."
            else:
                got["error"] = q.get("error", ["unknown"])[0]
                msg = "Sign-in failed: " + got["error"]
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(msg.encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    threading.Thread(target=srv.handle_request, daemon=True).start()
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": client_id, "redirect_uri": REDIRECT, "response_type": "code", "scope": SCOPE,
        "access_type": "offline", "prompt": "consent", "state": state})
    print("Opening your browser to sign in with the Google account that owns the channel...")
    print("If it doesn't open, visit:\n" + url)
    webbrowser.open(url)
    while "code" not in got and "error" not in got:
        threading.Event().wait(0.3)
    srv.server_close()
    if "error" in got:
        print("Sign-in failed:", got["error"])
        return 1
    data = urllib.parse.urlencode({"code": got["code"], "client_id": client_id, "client_secret": client_secret,
                                   "redirect_uri": REDIRECT, "grant_type": "authorization_code"}).encode()
    tok = json.loads(urllib.request.urlopen("https://oauth2.googleapis.com/token", data=data).read())
    if "refresh_token" not in tok:
        print("No refresh token returned:", tok)
        return 1
    print("\nAdd these three environment variables in the cloud environment settings:\n")
    print("YOUTUBE_CLIENT_ID=" + client_id)
    print("YOUTUBE_CLIENT_SECRET=" + client_secret)
    print("YOUTUBE_REFRESH_TOKEN=" + tok["refresh_token"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
