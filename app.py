import traceback
import praw
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
import utils
from pywebio import config, session

# # ==================R-Index=====================
reddit = praw.Reddit(
    client_id="d-7c-MSgBBHA0Mirq5Z3cw",
    client_secret="EZzaLo5N0p-jmXJYdSF74j7Z7er1VQ",
    user_agent="Reddit: PATRN:1.0 (by u/<uwukungfuwu>)",
    username="mace_user_account",
    password="macebot123")


@config(theme="yeti")
def app():
    session.set_env(title='PATRN', output_max_width='90%')
    # group all the inputs to make a form
    data = input_group("PATRN tool for Reddit users, submissions, and subreddits", [
        input('Input valid Reddit link', name='URL', required=True, type='text', datalist=["https://www.reddit.com/r"
                                                                                           "/UIUC/",
                                                                                           "https://www.reddit.com"
                                                                                           "/user/The-Judge1/"])
    ])

    put_markdown("____")
    # print(data['URL'])
    # formatting the data with html

    # displaying the data
    level_type = URL_parse(data['URL'])

    # res = f"""
    # <b>URL Level Type:</b> {level_type}<br>
    # """
    # put_html(res)


def URL_parse(URL_str):
    try:
        submission = reddit.submission(url=URL_str)
        after_slash = URL_str.split("/")
        if 'user' in after_slash:
            parse_user(submission)

        else:
            parse_post(URL_str)

    except praw.exceptions.InvalidURL as ex:
        if "Invalid URL (subreddit, not submission):" in ex.args[0] and "www.reddit.com" in URL_str.split("/"):
            after_slash = URL_str.split("/")
            sr = after_slash[-2]
            parse_subreddit(sr)

        elif "www.reddit.com" and "user" in URL_str.split("/"):
            after_slash = URL_str.split("/")
            if 'user' in after_slash:
                submission = reddit.submission(id=after_slash[-2])
                parse_user(submission)


def parse_user(submission):
    put_text('User evaluation').style('font-size: 30px; text-align: center')
    userinfo = utils.get_user_info(submission.id)
    for k, v in userinfo.items():
        put_row([put_code(k).style('color:red'), None, put_code(v)], size='30% 10px 70%')
    usermetrics = ['R-index', 'Toxicity', 'Sentiment', 'No. of Controversial posts', 'Engagement']
    metric_list_dict = []
    for metric in usermetrics:
        my_dictionary = {'title': metric, 'content': utils.user_desc(metric)}
        metric_list_dict.append(my_dictionary)
    put_scope("metdesc")
    with use_scope("metdesc"):
        put_collapse("Metric Descriptions", put_tabs(metric_list_dict))
    data = input_group("Basic info", [
        select('Choose metric for user',
               usermetrics, name="metric",
               multiple=True, required=True),
        slider(label='How many posts would you like to analyze?', value=25, min_value=1, max_value=1000, step=1,
               help_text="Choose", name="limit")
    ])
    metrics = data['metric']
    limit = data['limit']
    clear(scope="metdesc")
    utils.user_all(submission.id, metrics, limit)


def parse_post(URL_str):
    put_text('Post/Comment evaluation').style('font-size: 30px; text-align: center')
    submission = reddit.submission(url=URL_str)
    postinfo = utils.get_post_info(submission.id)
    for k, v in postinfo.items():
        put_row([put_code(k).style('color:red'), None, put_code(v)], size='30% 10px 70%')
    postmetrics = ['R-index', 'Sentiment', 'Toxicity', 'Engagement', 'Upvote Ratio']
    metric_list_dict = []
    for metric in postmetrics:
        my_dictionary = {'title': metric, 'content': utils.post_desc(metric)}
        metric_list_dict.append(my_dictionary)
    put_scope("metdesc")
    with use_scope("metdesc"):
        put_collapse("Metric Descriptions", put_tabs(metric_list_dict))
    data = input_group("Basic info", [
        select('Choose metric for post/comment',
               postmetrics, name="metric",
               multiple=True, required=True),
        slider(label='How many comments would you like to analyze?', value=25, min_value=1, max_value=1000, step=1,
               help_text="Choose", name="limit")
    ])
    metrics = data['metric']
    limit = data['limit']
    clear(scope="metdesc")
    utils.post_all(URL_str, metrics, limit)


def parse_subreddit(sr):
    put_text('Subreddit evaluation').style('font-size: 30px; text-align: center')
    srinfo = utils.get_sub_info(sr)
    for k, v in srinfo.items():
        put_row([put_code(k).style('color:red'), None, put_code(v)], size='30% 10px 70%')
    srmetrics = ['R-index', 'Sentiment', 'Toxicity', 'Engagement', 'NSFW']
    metric_list_dict = []
    for metric in srmetrics:
        my_dictionary = {'title': metric, 'content': utils.sr_desc(metric)}
        metric_list_dict.append(my_dictionary)
    put_scope("metdesc")
    with use_scope("metdesc"):
        put_collapse("Metric Descriptions", put_tabs(metric_list_dict))
    data = input_group("Basic info", [
        select('Choose metric for subreddit',
               srmetrics, name="metric",
               multiple=True, required=True),
        slider(label='How many posts would you like to analyze?', value=25, min_value=1, max_value=1000, step=1,
               help_text="Choose", name="limit")
    ])
    metrics = data['metric']
    limit = data['limit']
    clear(scope="metdesc")
    utils.sr_all(sr, metrics, limit)


# main function
if __name__ == '__main__':
    start_server(app, port=32420, debug=True)
