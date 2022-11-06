from googleapiclient import discovery
import json

# use this API key for all calls
# use https://github.com/googleapis/google-api-python-client under 
#   installation in the readme to set up the necessary requirements


API_KEY = 'AIzaSyC7AsGyLvB5_xR_z2oa5W-io1C6OFrB3dM'
negative_str = 'i hate you die'
positive_str = 'welcome to this API'

client = discovery.build(
  "commentanalyzer",
  "v1alpha1",
  developerKey=API_KEY,
  discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
  static_discovery=False,
)


def get_toxicity_score(input_str):
    analyze_request = {
    'comment': { 'text': input_str },
    'requestedAttributes': {'TOXICITY': {}}
    }

    response = client.comments().analyze(body=analyze_request).execute()

    toxicity_score = response['attributeScores']['TOXICITY']['summaryScore']['value']

    # print(toxicity_score)
    return toxicity_score

# print(get_toxicity_score(positive_str))
# print(get_toxicity_score(negative_str))