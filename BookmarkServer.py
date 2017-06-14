import os
import http.server
import requests
from urllib.parse import unquote, parse_qs

memory = {}

form = '''<!DOCTYPE html>
<title>Bookmark Server</title>
<form method="POST">
    <label>Long URI:
        <input name="longuri">
    </label>
    <br>
    <label>Short name:
        <input name="shortname">
    </label>
    <br>
    <button type="submit">Save it!</button>
</form>
<p>URIs I know about:
<pre>
{}
</pre>
'''


def CheckURI(uri, timeout=5):

    try:
        r = requests.get(uri, timeout=timeout)
        if r.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        return False


class Shortener(http.server.BaseHTTPRequestHandler):
    def do_GET(self):

        name = unquote(self.path[1:])

        if name:
            if name in memory:
                self.send_response(303)
                self.send_header('Location', memory[name])
                self.end_headers()

            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("I don't know '{}'.".format(name).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # List the known associations in the form.
            known = "\n".join("{} : {}".format(key, memory[key])
                              for key in sorted(memory.keys()))
            self.wfile.write(form.format(known).encode())

    def do_POST(self):
        # Decode the form data.
        length = int(self.headers.get('Content-length', 0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)
        longuri = params["longuri"][0]
        shortname = params["shortname"][0]

        if CheckURI(longuri):
            # This URI is good!  Remember it under the specified name.
            memory[shortname] = longuri

            # 3. Serve a redirect to the root page (the form).
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset-utf-8')
            self.end_headers()
            self.wfile.write(
            "Unable to find {}".format(longuri).encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, Shortener)
    httpd.serve_forever()
