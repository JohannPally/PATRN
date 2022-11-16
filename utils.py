from collections import defaultdict
import validators
import praw
import pprint
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
from nltk.sentiment import SentimentIntensityAnalyzer
import toxicity_example
import time

import plotly.express as px
import numpy as np
import pandas as pd

import datetime

reddit = praw.Reddit(
        client_id="d-7c-MSgBBHA0Mirq5Z3cw",
        client_secret="EZzaLo5N0p-jmXJYdSF74j7Z7er1VQ",
        user_agent="Reddit: PATRN:1.0 (by u/<uwukungfuwu>)",
        username="mace_user_account",
        password="macebot123")

sia = SentimentIntensityAnalyzer()

#==================R-Index=====================
def rindex(username, limit):
    user = reddit.redditor(username)
    submissions = user.submissions.new(limit=limit)
    scores = []
    for link in submissions:
        scores.append(link.score)

    scores.sort(reverse=True)
    n = len(scores)
    for i in range(n):
        if scores[i] < i:
            return i
    return i

def rindex_instance(userinstance, limit):
    user = userinstance
    submissions = user.submissions.new(limit=limit)
    scores = []
    for link in submissions:
        scores.append(link.score)

    scores.sort(reverse=True)
    n = len(scores)
    for i in range(n):
        if scores[i] < i:
            return i
    return i

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

#=============GRAPHS==============

def plt_rindex_community(subreddit_name, limit):
    # print(px.data.tips())
    rinds = []
    max_ri = 1
    for submission in reddit.subreddit(subreddit_name).hot(limit = limit):
        sa = submission.author
        ri_temp = rindex_instance(sa, limit)
        rinds.append(ri_temp)
        if ri_temp > max_ri:
            max_ri = ri_temp
    df = pd.DataFrame(data = rinds, columns = ['R-Indeces'])
    fig = px.histogram(df, x='R-Indeces',nbins = max_ri)
    fig.show()

def plt_toxicity_overtime(username, limit):
    user = reddit.redditor(username)
    submissions = user.comments.new(limit=limit)
    data = []
    cnt = 0
    for link in submissions:
        if cnt == 60:
            print('Waiting... (exceeding per minute Google API quota)')
            time.sleep(58)
            cnt = 0
        temp = []
        temp.append(link.created_utc)
        temp.append(toxicity_example.get_toxicity_score(link.body))
        data.append(temp)
        cnt+=1

    df = pd.DataFrame(data = data , columns = ["Date", "Toxicity"])
    fig = px.line(df, x='Date', y='Toxicity')
    fig.show()

#============SUBREDDIT DAG================
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

def plt_toxicity_post(post_link, post_limit, threshold):
    post = reddit.submission(url=post_link)
    data = []
    limit_count = 0
    for comment in post.comments:
        if (limit_count>=post_limit):
            break
        
        if validators.url(comment.body):
            continue
        
        toxicity_score = toxicity_example.get_toxicity_score(comment.body)
        data.append(toxicity_score)
        time.sleep(1)
        limit_count += 1
            
    plt.xlabel("toxicity score")
    np_data = np.array(data)
    plt.axvline(x = threshold, color = 'b', label = '')

    plt.hist(np_data)
    
    plt.show()

#========NON-NORMATIVE BEHAVIORS==========

def get_nsfw_over_subreddit(subreddit_name, post_limit):
    submissions = list(reddit.subreddit(subreddit_name).hot(limit = post_limit))
    tot = len(submissions)
    cnt = 0
    for submission in submissions:
        if submission.over_18:
            cnt+=1
    return (cnt/tot)

def get_number_controversial_user(username):
    submissions = list(reddit.redditor(username).controversial())
    return len(submissions)

def get_upvote_ratio_post(post):
    return reddit.submission(post).upvote_ratio
    
#===========ENGAGEMENT===================


def plt_user_engagement(username, post_limit):
    submissions = list(reddit.redditor(username).submissions.new(limit = post_limit))
    time_dict = defaultdict(lambda: 0)
    if len(submissions) > 0:
        temp_date = datetime.fromtimestamp(submissions[0].created_utc).date()
        for submission in submissions:
            timestamp = datetime.fromtimestamp(submission.created_utc)
            time_dict[timestamp.date()] = time_dict[timestamp.date()] + 1

    data = []
    for key in time_dict:
        data.append([key, time_dict[key]])

    df = pd.DataFrame(data = data , columns = ["Date", "Engagement"])
    fig = px.line(df, x='Date', y='Engagement')
    fig.show()

    return

def plt_subreddit_engagement(subreddit, post_limit):
    submissions = list(reddit.subreddit(subreddit).new(limit = post_limit))
    time_dict = defaultdict(lambda: 0)
    if len(submissions) > 0:
        temp_date = datetime.fromtimestamp(submissions[0].created_utc).date()
        for submission in submissions:
            timestamp = datetime.fromtimestamp(submission.created_utc)
            time_dict[timestamp.date()] = time_dict[timestamp.date()] + 1

    # pprint.pprint(time_dict)
    data = []
    for key in time_dict:
        data.append([key, time_dict[key]])

    df = pd.DataFrame(data = data , columns = ["Date", "Engagement"])
    fig = px.line(df, x='Date', y='Engagement')
    fig.show()

    return

def get_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def plt_post_engagement(post):
    comments = list(reddit.submission(post).comments)
    time_dict = defaultdict(lambda: 0)
    if len(comments) > 0:
        temp_date = get_datetime(comments[0].created_utc)
        for comment in comments:
            if isinstance(comment, praw.models.MoreComments):
                continue
            timestamp = get_datetime(comment.created_utc)
            if abs(temp_date - timestamp) > datetime.timedelta(hours = 1):
                temp_date = timestamp
            time_dict[temp_date] = time_dict[temp_date] + 1
    # pprint.pprint(time_dict)

    data = []
    for key in sorted(time_dict.keys()):
        data.append([key, time_dict[key]])
    df = pd.DataFrame(data = data , columns = ["Date", "Engagement"])
    print(df)
    
    fig = px.line(df, x='Date', y='Engagement')
    fig.show()

    return

#=================TESTING===============
# plt_toxicity_overtime('User_Simulator', 30)
# plt_rindex_community('UIUC',100)
# subreddit_interaction('UIUC')
# plt_toxicity_post("https://www.reddit.com/r/funny/comments/3g1jfi/buttons/", 30, 0.7)
# radar_sentiment('ydcy8i')
# print(get_nsfw_over_last_posts('FiftyFifty', 30))

# print(get_number_controversial_user('uwukungfuwu'))
# print(get_upvote_ratio_post('yvmpx6'))
# plt_user_engagement('OopsImACrow', 10)
# plt_subreddit_engagement('UIUC', 1000)
# plt_post_engagement('yvu8tx')
