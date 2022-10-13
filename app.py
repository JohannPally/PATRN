from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import praw

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

reddit = praw.Reddit(
    client_id="d-7c-MSgBBHA0Mirq5Z3cw",
    client_secret="EZzaLo5N0p-jmXJYdSF74j7Z7er1VQ",
    user_agent="Reddit: PATRN:1.0 (by u/<uwukungfuwu>)",
    username="mace_user_account",
    password="macebot123")

for submission in reddit.subreddit("science").hot(limit=10):
    print(submission.title)