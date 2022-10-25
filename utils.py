from collections import defaultdict
import validators
import praw
import pprint
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
from nltk.sentiment import SentimentIntensityAnalyzer

import plotly.express as px
import pandas as pd

reddit = praw.Reddit(
        client_id="d-7c-MSgBBHA0Mirq5Z3cw",
        client_secret="EZzaLo5N0p-jmXJYdSF74j7Z7er1VQ",
        user_agent="Reddit: PATRN:1.0 (by u/<uwukungfuwu>)",
        username="mace_user_account",
        password="macebot123")

sia = SentimentIntensityAnalyzer()

#==================R-Index=====================
def rindex(username):
    user = reddit.redditor(username)
    submissions = user.submissions.new(limit=1000)
    scores = []
    for link in submissions:
        scores.append(link.score)

    scores.sort(reverse=True)
    n = len(scores)
    for i in range(n):
        if scores[i] < i:
            print(i)
            break

#================SENTIMENT ANALYSIS==============

# for submission in reddit.subreddit("science").hot(limit=10):
#     print(sia.polarity_scores(submission.title))
    # print(submission.title)

def radar_sentiment(post):
    
    body = reddit.submission(post).selftext
    sent_sub = sia.polarity_scores(body)
    senti_list = [sent_sub['pos'], sent_sub['neg'], sent_sub['neu']]
    df = pd.DataFrame(dict(
    r=senti_list,
    theta=['positive', 'negative', 'neutral']))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself')
    fig.show()

# radar_sentiment('ydcy8i')

#====================LINK SPLITTING=========================
# -1 for invalid 
# 1 for user
# 2 for post/comment 
# 3 for community
output_dict = {1: "user", 
               2: "post",
               3: "community",
               -1: "invalid"}

def identify_link(link):
  valid=validators.url(link)

  if (not valid):
    return -1
  
  link_parsed = link.split("/")

  idx = 0
  classification = -1
  while (idx < len(link_parsed)):
    if link_parsed[idx] == 'r':
      classification = 3

    if link_parsed[idx] == 'user':
      classification = 1

    if link_parsed[idx] == 'comments':
      classification = 2
    idx += 1
    
  return classification

#============Subreddit DAG================
def subreddit_interaction(subreddit_name):
    comment_authors = defaultdict(lambda: defaultdict(lambda: 0))
    post_authors = defaultdict(lambda: 0)

    for submission in tqdm(reddit.subreddit(subreddit_name).hot(limit = 30)):
        sa = submission.author
        post_authors[sa] += len(submission.comments)
        for comment in submission.comments:
            ca = comment.author
            post_authors[ca] += 1
            comment_authors[ca][sa] += 1


    G = nx.DiGraph()
    for author in tqdm(post_authors):
        G.add_node(author, node_size = post_authors[author])
    
    for author in tqdm(comment_authors):
        for rec_author in comment_authors[author]:
            # print(author, rec_author, comment_authors[author][rec_author])
            G.add_edge(author, rec_author, weight = comment_authors[author][rec_author])


    nx.draw(G, pos=nx.spring_layout(G))
    plt.show()

# subreddit_interaction('UIUC')