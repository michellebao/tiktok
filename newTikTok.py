import pprint
import argparse
from TikTokApi import TikTokApi
import inspect
import json
from datetime import datetime
import requests
import os

api = TikTokApi(debug=True, executablePath="/usr/lib/chromium-browser/chromium-browser")
pp = pprint.PrettyPrinter()

#### Aggregate Functions ####

def getTrendingTikToks(n:int = 10, printOutput:bool = False, download:bool = False) -> dict: # returns info on n trending tiktoks
  trendingTiktoks = api.trending(count=n)
  lst = []
  for tiktok in trendingTiktoks:
    resp = processTikTokObject(tiktok)
    lst.append(resp)
  if printOutput:
    pp.pprint(lst)
  if download:
    downloadTikToks(lst)
  return lst

def getTrendingHashtags(n:int = 10, printOutput:bool = False) -> dict: # returns info on hashtags/challenges shown on side of trending page on desktop (up to 10)
  trendingHashtags = api.discoverHashtags()
  lst = []
  for i in range(min(n, 10)):
      hashtag = trendingHashtags[i].get('cardItem', {})
      id = hashtag.get('id')
      resp = {}
      resp['id'] = id
      resp['title'] = hashtag.get('title')
      resp['desc'] = hashtag.get('description')
      resp['views'] = hashtag.get('extraInfo', {}).get('views')
      lst.append(resp)
  if printOutput:
      pp.pprint(lst)
  return lst

def getTrendingMusic(n:int = 10, printOutput:bool = False) -> dict: # returns info on music shown on side of trending page on desktop
  trendingMusic = api.discoverMusic()
  lst = []
  resp = {}
  for i in range(min(n, 10)):
      music = trendingMusic[i].get('cardItem', {})
      resp = processMusicObject(music)
      lst.append(resp)
  if printOutput:
      pp.pprint(lst)
  return lst

#### Functions for Individual Objects ####

def getTikTokByUrl(urls, printOutput:bool = False, download:bool = False):
  lst = []
  for url in urls:
    tiktok = api.getTikTokByUrl(url)
    lst.append(processTikTokObject(tiktok.get('itemInfo', {}).get('itemStruct', {})))
  if printOutput:
    pp.pprint(lst)
  if download:
    downloadTikToks(lst)
  return lst

def byUsername(usernames, n:int = 10, printOutput:bool = False, download:bool = False) -> dict:
  lst = []
  for username in usernames:
    for tiktok in api.byUsername(username, count=n):
      lst.append(processTikTokObject(tiktok))
  if printOutput:
    pp.pprint(lst)
  if download:
    downloadTikToks(lst)
  return lst

def byHashtag(hashtags, n:int = 10, printOutput:bool = False, download:bool = False) -> dict:
  lst = []
  for hashtag in hashtags:
    for tiktok in api.byHashtag(hashtag, count=n):
      resp = {}
      resp['id'] = tiktok.get('itemInfos', {}).get('id')
      resp['text'] = tiktok.get('itemInfos', {}).get('text')
      resp['createTime'] = datetime.fromtimestamp(int(tiktok.get('itemInfos', {}).get('createTime'))).isoformat()
      resp['playAddr'] = tiktok.get('itemInfos', {}).get('video', {}).get('urls')
      if resp['playAddr']:
        resp['playAddr'] = resp['playAddr'][0]
      resp['username'] = tiktok.get('authorInfos', {}).get('uniqueId')
      resp['diggCount'] = tiktok.get('itemInfos', {}).get('diggCount')
      resp['shareCount'] = tiktok.get('itemInfos', {}).get('shareCount')
      resp['commentCount'] = tiktok.get('itemInfos', {}).get('commentCount')
      resp['playCount'] = tiktok.get('itemInfos', {}).get('playCount')
      lst.append(resp)
  if printOutput:
    pp.pprint(lst)
  if download:
    downloadTikToks(lst)
  return lst

def getHashtagInfo(hashtags, printOutput:bool = False) -> dict: # returns info for specific hashtag (exclude # symbol from string)
  lst = []
  for hashtag in hashtags:
    resp = {}
    obj = api.getHashtagObject(hashtag)
    if (obj.get('statusCode') != 0):
        print("Error getting object for hashtag: ", hashtag)
        continue
    hashtagInfo = obj.get('challengeInfo', {})
    resp['id'] = hashtagInfo.get('challenge', {}).get('id') 
    resp['title'] = hashtagInfo.get('challenge', {}).get('title') 
    resp['desc'] = hashtagInfo.get('shareMeta', {}).get('desc') 
    resp['videoCount'] = hashtagInfo.get('stats', {}).get('videoCount')
    resp['viewCount'] = hashtagInfo.get('stats', {}).get('viewCount')
    lst.append(resp)
  if printOutput:
    pp.pprint(lst)
  return lst

def getUserInfo(usernames: list, printOutput:bool = False) -> dict: # returns info for specific user account
  lst = []
  for username in usernames:
    obj = api.getUser(username)
    resp = {}
    if (obj.get('statusCode') != 0):
        print("Error getting object for username: ", username)
        continue
    usernameInfo = obj.get('userInfo', {})
    resp['id'] = usernameInfo.get('user', {}).get('id')
    resp['username'] = usernameInfo.get('user', {}).get('uniqueId')
    resp['verified'] = usernameInfo.get('user', {}).get('verified')
    resp['followingCount'] = usernameInfo.get('stats', {}).get('followingCount')
    resp['followerCount'] = usernameInfo.get('stats', {}).get('followerCount')
    resp['heartCount'] = usernameInfo.get('stats', {}).get('heartCount')
    resp['videoCount'] = usernameInfo.get('stats', {}).get('videoCount')
    resp['diggCount'] = usernameInfo.get('stats', {}).get('diggCount')
    lst.append(resp)
    if printOutput:
        pp.pprint(lst)
  return lst

def getUserLikedByUsername(username: str, n:int = 10, printOutput:bool = False, download:bool = False) -> list: # returns list of given user's liked tiktoks (returns 0 if private list)
  userId = usernameToUserId(username)
  obj = api.getUser(username)
  userInfo = obj.get('userInfo', {})
  likedList = api.userLiked(userId, userInfo.get('user', {}).get('secUid'), count=n)
  lst = []
  for tiktok in likedList:
      resp = processTikTokObject(tiktok)
      lst.append(resp)
  if printOutput:
      pp.pprint(lst)
  if download:
    downloadTikToks(lst)
  return lst

def getSuggestedUsers(usernames:str, n:int = 10, printOutput:bool = False) -> list: # returns list of suggested users given an account. 
  lst = []
  for username in usernames:
    userId = usernameToUserId(username)
    suggested = api.getSuggestedUsersbyID(count = n, userId = userId)
    for user in suggested:
      userN = user.get('subTitle')
      if userN:
        userN = userN.replace('@', '')
        lst += getUserInfo([userN], printOutput)
  return lst

def getSuggestedHashtags(usernames:str, n:int = 10, printOutput:bool = False) -> list: # returns list of suggested hashtags given an account
  lst = []
  for username in usernames:
    userId = usernameToUserId(username)
    suggested = api.getSuggestedHashtagsbyID(count=n, userId = userId)
    for hashtag in suggested:
      hashStr = hashtag.get('title')
      if hashStr:
        hashStr = hashStr.replace('#', '')
        lst += getHashtagInfo([hashStr], printOutput)
  return lst

def getSuggestedMusic(usernames:str, n:int = 10, printOutput:bool = False) -> list: # returns list of suggested music given an account
  lst = []
  for username in usernames:
    userId = usernameToUserId(username)
    suggested = api.getSuggestedMusicIDCrawler(count = n, userId = userId)
    for music in suggested:
        resp = processMusicObject(music)
        lst.append(resp)
  if printOutput:
    pp.pprint(lst)
  return lst

#### Util Functions ####

def processTikTokObject(tiktok:dict) -> dict:
  id = tiktok['id']
  resp = {}
  resp['id'] = id
  resp['desc'] = tiktok.get('desc')
  resp['createTime'] = datetime.fromtimestamp(int(tiktok.get('createTime'))).isoformat()
  resp['playAddr'] = tiktok.get('video', {}).get('playAddr')
  resp['username'] = tiktok.get('author', {}).get('uniqueId')
  resp['diggCount'] = tiktok.get('stats', {}).get('diggCount')
  resp['shareCount'] = tiktok.get('stats', {}).get('shareCount')
  resp['commentCount'] = tiktok.get('stats', {}).get('commentCount')
  resp['playCount'] = tiktok.get('stats', {}).get('playCount')
  return resp

def processMusicObject(music:dict) -> dict:
  id = music.get('id')
  resp = {}
  resp['id'] = id
  resp['title'] = music.get('title')
  resp['desc'] = music.get('description')
  resp['playUrl'] = music.get('extraInfo', {}).get('playUrl')
  resp['videoCount'] = music.get('extraInfo', {}).get('posts')
  return resp

def usernameToUserId(username: str) -> str:
  obj = api.getUser(username)
  userInfo = obj.get('userInfo', {})
  userId = userInfo.get('user', {}).get('id')
  return userId

def downloadTikToks(tiktoks):
  dirName = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
  for tiktok in tiktoks:
    addr = tiktok['playAddr']
    id = tiktok['id']
    path = 'downloadedTikToks/' + dirName + '/' + str(id) + '.mp4'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    r = requests.get(addr, headers={'referer': 'https://www.tiktok.com/'})
    open(path, 'wb').write(r.content)


def main():
# optional arguments:
# -h, --help            show this help message and exit
# --function {getTrendingTikToks,getTrendingHashtags,getTrendingMusic,getHashtagInfo,getUserInfo,getUserLikedByUsername,getSuggestedUsers,getSuggestedHashtags,getSuggestedMusic}
#                       Function name
# --n N                 n count
# --printOutput PRINTOUTPUT
#                       Print output
# --hashtag HASHTAG     Hashtag string
# --username USERNAME   Username
# --crawl CRAWL         Crawl
  FUNCTION_MAP = {
    'getTrendingTikToks': getTrendingTikToks,
    'getTrendingHashtags': getTrendingHashtags,
    'getTrendingMusic': getTrendingMusic,
    'getHashtagInfo': getHashtagInfo,
    'getUserInfo': getUserInfo,
    'getUserLikedByUsername': getUserLikedByUsername,
    'getSuggestedUsers': getSuggestedUsers,
    'getSuggestedHashtags': getSuggestedHashtags,
    #'getSuggestedMusic': getSuggestedMusic,
    'byUsername': byUsername,
    'byHashtag': byHashtag,
    'getTikTokByUrl': getTikTokByUrl
  }
  parser = argparse.ArgumentParser()
  parser.add_argument("--function", choices = FUNCTION_MAP.keys(), required=True)
  parser.add_argument("--n", type=int, required=False)
  parser.add_argument("--printOutput", type=str, required=False)
  parser.add_argument("--hashtag", nargs='+', required=False)
  parser.add_argument("--username", nargs='+', required=False)
  parser.add_argument("--url", nargs='+', required=False)
  parser.add_argument("--download", default=False, action='store_true')
  parser.add_argument("--outFile", type=str, required=False)

  default_n = 10
  default_print = False

  args = parser.parse_args()
  func = FUNCTION_MAP[args.function]
  out = None
  if args.function == 'getTrendingTikToks':
    out = func(args.n or default_n, args.printOutput or default_print, args.download)
  if args.function == 'getTrendingHashtags' or args.function == 'getTrendingMusic':
    out = func(args.n or default_n, args.printOutput or default_print)
  if args.function == 'getHashtagInfo':
    if not args.hashtag:
      print("No hashtag given")
      return
    out = func(args.hashtag, args.printOutput or default_print)
  if args.function == 'getUserInfo':
    if not args.username:
      print("No username given")
      return
    out = func(args.username, args.printOutput or default_print)
  if args.function == 'getUserLikedByUsername':
    if not args.username:
      print("No username given")
      return
    out = func(args.username, args.n or default_n, args.printOutput or default_print, args.download)
  if args.function == 'getSuggestedUsers':
    if not args.username:
      print("No username given")
      return
    out = func(args.username, args.n or default_n, args.printOutput or default_print)
  if args.function == 'getSuggestedHashtags':
    if not args.username:
      print("No username given")
      return
    out = func(args.username, args.n or default_n, args.printOutput or default_print)
  if args.function == 'byUsername':
    if not args.username:
      print('No username given')
      return
    out = func(args.username, args.n or default_n, args.printOutput or default_print, args.download)
  if args.function == 'byHashtag':
    if not args.hashtag:
      print('No hashtag given')
      return
    out = func(args.hashtag, args.n or default_n, args.printOutput or default_print, args.download)
  if args.function == 'getTikTokByUrl':
    if not args.url:
      print('No url given')
      return
    out = func(args.url, args.printOutput or default_print, args.download)

  with open(args.outFile, 'w') as outfile:
    json.dump(out, outfile)

main()
