import io
import time
from collections import defaultdict
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import praw
import validators
from nltk.sentiment import SentimentIntensityAnalyzer
from pywebio.output import *
from tqdm import tqdm
import datetime
import toxicity_example

reddit = praw.Reddit(
    client_id="d-7c-MSgBBHA0Mirq5Z3cw",
    client_secret="EZzaLo5N0p-jmXJYdSF74j7Z7er1VQ",
    user_agent="Reddit: PATRN:1.0 (by u/<uwukungfuwu>)",
    username="mace_user_account",
    password="macebot123")

sia = SentimentIntensityAnalyzer()

matplotlib.use('agg')


# ==================R-Index=====================
def rindex_user(username, limit):
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


def plt_rindex_community(subreddit_name, limit):
    # print(px.data.tips())
    rinds = []
    max_ri = 1
    for submission in reddit.subreddit(subreddit_name).hot(limit=limit):
        sa = submission.author
        ri_temp = rindex_instance(sa, limit)
        rinds.append(ri_temp)
        if ri_temp > max_ri:
            max_ri = ri_temp
    df = pd.DataFrame(data=rinds, columns=['R-Indeces'])
    fig = px.histogram(df, x='R-Indeces', nbins=max_ri)
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    return html


def rindex_post(post, limit):
    sub = reddit.submission(post)
    return rindex_instance(sub.author, limit)


# ================SENTIMENT ANALYSIS==============


def radar_sentiment(submission):
    post = submission
    body = reddit.submission(post).selftext
    sent_sub = sia.polarity_scores(body)
    senti_list = [sent_sub['pos'], sent_sub['neg'], sent_sub['neu']]
    df = pd.DataFrame(dict(
        r=senti_list,
        theta=['positive', 'negative', 'neutral']))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself')
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    return html


def sentiment_user(username, limit):
    user = reddit.redditor(username)
    submissions = user.submissions.new(limit=limit)
    senti_list = []
    theta_list = []
    color_list = []
    for i, link in enumerate(submissions):
        sent_sub = sia.polarity_scores(link.selftext)
        senti_list.extend([sent_sub['pos'], sent_sub['neg'], sent_sub['neu']])
        theta_list.extend(['positive', 'negative', 'neutral'])
        color_list.extend([i, i, i])
    df = pd.DataFrame(dict(
        r=senti_list,
        theta=theta_list,
        color=color_list))
    print(df)
    fig = px.line_polar(df, r='r', theta='theta', color='color', line_close=True)
    fig.update_traces(fill='toself')
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    return html


def sentiment_community(subreddit, limit):
    submissions = reddit.subreddit(subreddit).hot(limit=limit)
    senti_list = []
    theta_list = []
    color_list = []
    for i, link in enumerate(submissions):
        sent_sub = sia.polarity_scores(link.selftext)
        senti_list.extend([sent_sub['pos'], sent_sub['neg'], sent_sub['neu']])
        theta_list.extend(['positive', 'negative', 'neutral'])
        color_list.extend([i, i, i])
    df = pd.DataFrame(dict(
        r=senti_list,
        theta=theta_list,
        color=color_list))
    print(df)
    fig = px.line_polar(df, r='r', theta='theta', color='color', line_close=True)
    fig.update_traces(fill='toself')
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    return html


# =============GRAPHS==============#

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
        timestamp = datetime.datetime.fromtimestamp(link.created_utc)
        temp.append(timestamp.date())
        temp.append(toxicity_example.get_toxicity_score(link.body))
        data.append(temp)
        cnt += 1

    df = pd.DataFrame(data=data, columns=["Date", "Toxicity"])
    fig = px.line(df, x='Date', y='Toxicity')
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    return html


def plt_toxicity_post(post_link, post_limit, threshold=0.6):
    post = post_link
    data = []
    limit_count = 0
    for comment in post.comments:
        if limit_count >= post_limit:
            break

        if validators.url(comment.body):
            continue

        toxicity_score = toxicity_example.get_toxicity_score(comment.body)
        data.append(toxicity_score)
        time.sleep(1)
        limit_count += 1

    df = pd.DataFrame(data=data, columns=["Toxicity"])
    df["Color"] = np.where(df["Toxicity"] > threshold, 'red', 'blue')
    fig = px.histogram(df, x='Toxicity', nbins=10, color="Color")
    fig.update_traces(marker_line_width=1, marker_line_color="black")
    fig.update_layout(showlegend=False)
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    return html
    #
    # plt.xlabel("toxicity score")
    # np_data = np.array(data)
    # plt.axvline(x=threshold, color='b', label='')
    #
    # plt.hist(np_data)
    # fig = plt.gcf()
    # buf = io.BytesIO()
    # fig.savefig(buf)
    # return buf


def plt_toxicity_community(subreddit, limit):
    rinds = []
    max_ri = 10
    submission_list = reddit.subreddit(subreddit).hot(limit=limit)
    for submission in submission_list:
        sa = submission.title
        rinds.append(toxicity_example.get_toxicity_score(sa))

    df = pd.DataFrame(data=rinds, columns=['Toxicity'])
    fig = px.histogram(df, x='Toxicity', nbins=max_ri)
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    return html


# ========NON-NORMATIVE BEHAVIORS==========
def get_nsfw_over_subreddit(subreddit_name, post_limit):
    submissions = list(reddit.subreddit(subreddit_name).hot(limit=post_limit))
    tot = len(submissions)
    cnt = 0
    for submission in submissions:
        if submission.over_18:
            cnt += 1
    print(cnt/tot)
    return cnt / tot


def get_number_controversial_user(username):
    submissions = list(reddit.redditor(username).submissions.controversial())
    return len(submissions)


def get_upvote_ratio_post(post):
    return reddit.submission(post).upvote_ratio


# ===========ENGAGEMENT===================


def plt_user_engagement(username, post_limit):
    submissions = list(reddit.redditor(username).submissions.new(limit=post_limit))
    time_dict = defaultdict(lambda: 0)
    if len(submissions) > 0:
        temp_date = datetime.datetime.fromtimestamp(submissions[0].created_utc).date()
        for submission in submissions:
            timestamp = datetime.datetime.fromtimestamp(submission.created_utc)
            time_dict[timestamp.date()] = time_dict[timestamp.date()] + 1
    data = []

    for key in time_dict:
        data.append([key, time_dict[key]])

    df = pd.DataFrame(data=data, columns=["Date", "Engagement"])
    fig = px.line(df, x='Date', y='Engagement')
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    return html


def plt_subreddit_engagement(subreddit, post_limit):
    submissions = list(reddit.subreddit(subreddit).new(limit=post_limit))
    time_dict = defaultdict(lambda: 0)
    if len(submissions) > 0:
        temp_date = datetime.datetime.fromtimestamp(submissions[0].created_utc).date()
        for submission in submissions:
            timestamp = datetime.datetime.fromtimestamp(submission.created_utc)
            time_dict[timestamp.date()] = time_dict[timestamp.date()] + 1

    # pprint.pprint(time_dict)
    data = []
    for key in time_dict:
        data.append([key, time_dict[key]])

    df = pd.DataFrame(data=data, columns=["Date", "Engagement"])
    fig = px.line(df, x='Date', y='Engagement')
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    return html


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
            if abs(temp_date - timestamp) > datetime.timedelta(hours=1):
                temp_date = timestamp
            time_dict[temp_date] = time_dict[temp_date] + 1
    # pprint.pprint(time_dict)

    data = []
    for key in sorted(time_dict.keys()):
        data.append([key, time_dict[key]])
    df = pd.DataFrame(data=data, columns=["Date", "Engagement"])
    print(df)

    fig = px.line(df, x='Date', y='Engagement')
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    return html


def get_user_info(username):
    # should return username, date of creation, bio, karma

    user = reddit.redditor(username)

    name = user.name
    bio = user.subreddit.public_description
    date = datetime.date.fromtimestamp(user.created_utc)
    karma = user.comment_karma + user.link_karma + user.awarder_karma + user.awardee_karma

    to_return = {"username": name, "bio": bio, "date created": date, "karma": karma}
    return to_return


def get_post_info(post_id):
    post = reddit.submission(post_id)
    time = datetime.date.fromtimestamp(post.created)
    title = post.title
    score = post.score

    to_return = {"title": title, "date created": time, "score": score}
    return to_return


def get_sub_info(sub):
    subreddit = reddit.subreddit(sub)
    name = subreddit.display_name
    date = datetime.date.fromtimestamp(subreddit.created_utc)
    description = subreddit.public_description
    num_subscribers = subreddit.subscribers

    to_return = {"name": name, "date created": date, "description": description, "total subscribers": num_subscribers}

    return to_return


def sr_all(sr, metrics, limit):
    while len(metrics) != 5:
        metrics.append("")
    put_grid([
        [span(put_markdown('## Metrics'), col=3)],
        [put_scope('1-1'), None, put_scope('1-2')],
        [put_scope('2-1'), None, put_scope('2-2')],
        [put_scope('3-1')],
    ], cell_widths='48% 4% 48%')

    with use_scope('1-1'):
        put_collapse(metrics[0], user_desc(metrics[0])).style('text-align: center')
        put_html(return_sr_output(sr, metrics[0], limit)).style('text-align: center')
        if metrics[0] == "":
            clear(scope='1-1')

    with use_scope('1-2'):
        put_collapse(metrics[1], user_desc(metrics[1])).style('text-align: center')
        put_html(return_sr_output(sr, metrics[1], limit)).style('text-align: center')
        if metrics[1] == "":
            clear(scope='1-2')

    with use_scope('2-1'):
        put_collapse(metrics[2], user_desc(metrics[2])).style('text-align: center')
        put_html(return_sr_output(sr, metrics[2], limit)).style('text-align: center')
        if metrics[2] == "":
            clear(scope='2-1')

    with use_scope('2-2'):
        put_collapse(metrics[3], user_desc(metrics[3])).style('text-align: center')
        put_html(return_sr_output(sr, metrics[3], limit)).style('text-align: center')
        if metrics[3] == "":
            clear(scope='2-2')

    with use_scope('3-1'):
        put_collapse(metrics[4], user_desc(metrics[4])).style('text-align: center')
        put_html(return_sr_output(sr, metrics[4], limit)).style('text-align: center')
        if metrics[4] == "":
            clear(scope='3-1')


def return_sr_output(sr, metric, limit):
    if metric == 'R-index':
        return str(plt_rindex_community(sr, limit))
    elif metric == 'Toxicity':
        return plt_toxicity_community(sr, limit)
    elif metric == 'Sentiment':
        return sentiment_community(sr, limit)
    elif metric == 'NSFW':
        return str(get_nsfw_over_subreddit(sr, limit))
    elif metric == 'Engagement':
        return plt_subreddit_engagement(sr, limit)


def post_all(URL_str, metrics, limit):
    submission = reddit.submission(url=URL_str)
    while len(metrics) != 5:
        metrics.append("")
    put_grid([
        [span(put_markdown('## Metrics'), col=3)],
        [put_scope('1-1'), None, put_scope('1-2')],
        [put_scope('2-1'), None, put_scope('2-2')],
        [put_scope('3-1')],
    ], cell_widths='48% 4% 48%')

    with use_scope('1-1'):
        put_collapse(metrics[0], user_desc(metrics[0])).style('text-align: center')
        put_html(return_post_output(submission, metrics[0], limit)).style('text-align: center')
        if metrics[0] == "":
            clear(scope='1-1')

    with use_scope('1-2'):
        put_collapse(metrics[1], user_desc(metrics[1])).style('text-align: center')
        put_html(return_post_output(submission, metrics[1], limit)).style('text-align: center')
        if metrics[1] == "":
            clear(scope='1-2')

    with use_scope('2-1'):
        put_collapse(metrics[2], user_desc(metrics[2])).style('text-align: center')
        put_html(return_post_output(submission, metrics[2], limit)).style('text-align: center')
        if metrics[2] == "":
            clear(scope='2-1')

    with use_scope('2-2'):
        put_collapse(metrics[3], user_desc(metrics[3])).style('text-align: center')
        put_html(return_post_output(submission, metrics[3], limit)).style('text-align: center')
        if metrics[3] == "":
            clear(scope='2-2')

    with use_scope('3-1'):
        put_collapse(metrics[4], user_desc(metrics[4])).style('text-align: center')
        put_html(return_post_output(submission, metrics[4], limit)).style('text-align: center')
        if metrics[4] == "":
            clear(scope='3-1')


def return_post_output(submission, metric, limit):
    if metric == 'R-index':
        return str(rindex_post(submission, limit))
    elif metric == 'Toxicity':
        return plt_toxicity_post(submission, limit)
    elif metric == 'Sentiment':
        return radar_sentiment(submission.id)
    elif metric == 'Upvote Ratio':
        return str(get_upvote_ratio_post(submission))
    elif metric == 'Engagement':
        return plt_post_engagement(submission)


def return_user_output(submission, metric, limit):
    if metric == 'R-index':
        return str(rindex_user(submission, limit))
    elif metric == 'Toxicity':
        return plt_toxicity_overtime(submission, limit)
    elif metric == 'Sentiment':
        return sentiment_user(submission, limit)
    elif metric == 'No. of Controversial posts':
        return str(get_number_controversial_user(submission))
    elif metric == 'Engagement':
        return plt_user_engagement(submission, limit)


def user_all(username, metrics, limit):
    while len(metrics) != 5:
        metrics.append("")
    put_grid([
        [span(put_markdown('## Metrics'), col=3)],
        [put_scope('1-1'), None, put_scope('1-2')],
        [put_scope('2-1'), None, put_scope('2-2')],
        [put_scope('3-1')],
    ], cell_widths='48% 4% 48%')

    with use_scope('1-1'):
        put_collapse(metrics[0], user_desc(metrics[0])).style('text-align: center')
        put_html(return_user_output(username, metrics[0], limit)).style('text-align: center')
        if metrics[0] == "":
            clear(scope='1-1')

    with use_scope('1-2'):
        put_collapse(metrics[1], user_desc(metrics[1])).style('text-align: center')
        put_html(return_user_output(username, metrics[1], limit)).style('text-align: center')
        if metrics[1] == "":
            clear(scope='1-2')

    with use_scope('2-1'):
        put_collapse(metrics[2], user_desc(metrics[2])).style('text-align: center')
        put_html(return_user_output(username, metrics[2], limit)).style('text-align: center')
        if metrics[2] == "":
            clear(scope='2-1')

    with use_scope('2-2'):
        put_collapse(metrics[3], user_desc(metrics[3])).style('text-align: center')
        put_html(return_user_output(username, metrics[3], limit)).style('text-align: center')
        if metrics[3] == "":
            clear(scope='2-2')

    with use_scope('3-1'):
        put_collapse(metrics[4], user_desc(metrics[4])).style('text-align: center')
        put_html(return_user_output(username, metrics[4], limit)).style('text-align: center')
        if metrics[4] == "":
            clear(scope='3-1')


def user_desc(metric):
    if metric == 'R-index':
        return "rindex"
    elif metric == 'Toxicity':
        return "Toxicity"
    elif metric == 'Sentiment':
        return 'Sentiment'
    elif metric == 'No. of Controversial posts':
        return 'No. of Controversial posts'
    elif metric == 'Engagement':
        return 'Engagement'
    else:
        return ""


def post_desc(metric):
    if metric == 'R-index':
        return "rindex"
    elif metric == 'Toxicity':
        return "Toxicity"
    elif metric == 'Sentiment':
        return 'Sentiment'
    elif metric == 'Upvote Ratio':
        return 'Upvote Ratio'
    elif metric == 'Engagement':
        return 'Engagement'
    else:
        return ""


def sr_desc(metric):
    if metric == 'R-index':
        return "rindex"
    elif metric == 'Toxicity':
        return "Toxicity"
    elif metric == 'Sentiment':
        return 'Sentiment'
    elif metric == 'NSFW':
        return 'NSFW'
    elif metric == 'Engagement':
        return 'Engagement'
    else:
        return ""
