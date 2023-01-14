headline = "Two killed in a Hot Wheels car crash"

organization = "hot wheels"

import re


# make the regex insensitive
print(re.findall('\\b'+organization+'\\b', headline, flags=re.IGNORECASE))

# if organization.lower() in headline.lower():
#     print("organization name deteched in headline")
# else:
#     print("skipping")