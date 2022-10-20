import validators


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
