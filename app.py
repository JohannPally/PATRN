from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import praw
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import urllib.parse as urlparse

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        print('hi' + parsed_path.query)
        message = '\n'.join([
            'CLIENT VALUES:',
            'client_address=%s (%s)' % (self.client_address,
                self.address_string()),
            'command=%s' % self.command,
            'path=%s' % self.path,
            'real path=%s' % parsed_path.path,
            'query=%s' % parsed_path.query,
            'request_version=%s' % self.request_version,
            '',
            'SERVER VALUES:',
            'server_version=%s' % self.server_version,
            'sys_version=%s' % self.sys_version,
            'protocol_version=%s' % self.protocol_version,
            '',
            ])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return 

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

sia = SentimentIntensityAnalyzer()

for submission in reddit.subreddit("science").hot(limit=10):
    print(sia.polarity_scores(submission.title))
    # print(submission.title)