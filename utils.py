import validators
import praw

#==================R-Index=====================
reddit = praw.Reddit(
    client_id="d-7c-MSgBBHA0Mirq5Z3cw",
    client_secret="EZzaLo5N0p-jmXJYdSF74j7Z7er1VQ",
    user_agent="Reddit: PATRN:1.0 (by u/<uwukungfuwu>)",
    username="mace_user_account",
    password="macebot123")

user = reddit.redditor('killingmemesoftly')
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
# sia = SentimentIntensityAnalyzer()

# for submission in reddit.subreddit("science").hot(limit=10):
#     print(sia.polarity_scores(submission.title))
#     # print(submission.title)


#====================LINK SPLITTING=========================
# -1 for invalid 
# 1 for user
# 2 for post/comment 
# 3 for community
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

output_dict = {1: "user", 
               2: "post",
               3: "community",
               -1: "invalid"}
