import requests
import random
# a = requests.get(
#     'http://www.padaili.com/proxyapi.php?apikey=b24d1c5c457639d59931eb0eff5a99ee&num=1000&type=1,2&order=default')
#
# print(a.text.strip('\n').split('</br>'))

s=[1,2,3,4,4,4]
s=set(s)
s=tuple(s)
print(type(s))
print(s)
print(random.choice(s))