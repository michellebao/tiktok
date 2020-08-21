#!/usr/bin/env python

# INSTRUCTIONS FOR RUNNING
# pip install TikTokApi

import pprint
from TikTokApi import TikTokApi
api = TikTokApi(debug=True)
pp = pprint.PrettyPrinter()

#### Aggregate Functions ####

def getTrendingTikToks(n:int = 10, printOutput:bool = False) -> dict: # returns info on n trending tiktoks
    trendingTiktoks = api.trending(count=n)
    resp = {}
    for tiktok in trendingTiktoks:
        processTikTokObject(tiktok, resp)
    if printOutput:
        pp.pprint(resp)
    return resp

def getTrendingHashtags(n:int = 10, printOutput:bool = False) -> dict: # returns info on hashtags/challenges shown on side of trending page on desktop (up to 10)
    trendingHashtags = api.discoverHashtags()
    resp = {}
    for i in range(min(n, 10)):
        hashtag = trendingHashtags[i].get('cardItem', {})
        id = hashtag.get('id')
        resp[id] = {}
        resp[id]['title'] = hashtag.get('title')
        resp[id]['desc'] = hashtag.get('description')
        resp[id]['views'] = hashtag.get('extraInfo', {}).get('views')
    if printOutput:
        pp.pprint(resp)
    return resp

def getTrendingMusic(n:int = 10, printOutput:bool = False) -> dict: # returns info on music shown on side of trending page on desktop
    trendingMusic = api.discoverMusic()
    resp = {}
    for i in range(min(n, 10)):
        music = trendingMusic[i].get('cardItem', {})
        processMusicObject(music, resp)
    if printOutput:
        pp.pprint(resp)
    return resp

#### Functions for Individual Objects ####

def getHashtagInfo(hashtag: str, printOutput:bool = False) -> dict: # returns info for specific hashtag (exclude # symbol from string)
    resp = {}
    obj = api.getHashtagObject(hashtag)
    if (obj.get('statusCode') != 0):
        print("Error getting object for hashtag: ", hashtag)
        return resp
    hashtagInfo = obj.get('challengeInfo', {})
    resp['id'] = hashtagInfo.get('challenge', {}).get('id') 
    resp['title'] = hashtagInfo.get('challenge', {}).get('title') 
    resp['desc'] = hashtagInfo.get('challenge', {}).get('desc') 
    resp['videoCount'] = hashtagInfo.get('stats', {}).get('videoCount')
    resp['viewCount'] = hashtagInfo.get('stats', {}).get('viewCount')
    if printOutput:
        pp.pprint(resp)
    return resp

def getUserInfo(username: str, printOutput:bool = False) -> dict: # returns info for specific user account
    obj = api.getUser(username)
    resp = {}
    if (obj.get('statusCode') != 0):
        print("Error getting object for username: ", username)
        return resp
    usernameInfo = obj.get('userInfo', {})
    resp['id'] = usernameInfo.get('user', {}).get('id')
    resp['username'] = usernameInfo.get('user', {}).get('uniqueId')
    resp['verified'] = usernameInfo.get('user', {}).get('verified')
    resp['followingCount'] = usernameInfo.get('stats', {}).get('followingCount')
    resp['followerCount'] = usernameInfo.get('stats', {}).get('followerCount')
    resp['heartCount'] = usernameInfo.get('stats', {}).get('heartCount')
    resp['videoCount'] = usernameInfo.get('stats', {}).get('videoCount')
    resp['diggCount'] = usernameInfo.get('stats', {}).get('diggCount')
    if printOutput:
        pp.pprint(resp)
    return resp

def getUserLikedByUsername(username: str, n:int = 10, printOutput:bool = False) -> list: # returns list of given user's liked tiktoks (returns 0 if private list)
    userId = usernameToUserId(username)
    obj = api.getUser(username)
    userInfo = obj.get('userInfo', {})
    likedList = api.userLiked(userId, userInfo.get('user', {}).get('secUid'), count=n)
    lst = []
    for tiktok in likedList:
        resp = {}
        processTikTokObject(tiktok, resp)
        lst.append(resp)
    if printOutput:
        pp.pprint(lst)
    return lst

def getSuggestedUsers(username:str, count:int = 10, crawl:bool = False, printOutput:bool = False) -> list: # returns list of suggested users given an account. 
    # if crawl is True, will return suggested users for given username's suggested users
    userId = usernameToUserId(username)
    suggested = api.getSuggestedUsersbyIDCrawler(count = count, startingId = userId) if crawl else api.getSuggestedUsersbyID(count = count, userId = userId)
    lst = []
    for user in suggested:
        username = user.get('subTitle')
        if username:
            username = username.replace('@', '')
        lst.append(getUserInfo(username, printOutput))
    return lst

def getSuggestedHashtags(username:str, count:int = 10, crawl:bool = False, printOutput:bool = False) -> list: # returns list of suggested hashtags given an account
    # if crawl is True, will return suggested hashtags for given username's suggested users
    userId = usernameToUserId(username)
    suggested = api.getSuggestedHashtagsbyIDCrawler(count = count, startingId = userId) if crawl else api.getSuggestedHashtagsbyID(count = count, userId = userId)
    lst = []
    for hashtag in suggested:
        hashStr = hashtag.get('title')
        if hashStr:
            hashStr = hashStr.replace('#', '')
        lst.append(getHashtagInfo(hashStr, printOutput))

def getSuggestedMusic(username:str, count:int = 10, crawl:bool = False, printOutput:bool = False) -> list: # returns list of suggested music given an account
    # if crawl is True, will return suggested music for given username's suggested users
    userId = usernameToUserId(username)
    suggested = api.getSuggestedMusicIDCrawler(count = count, startingId = userId) if crawl else api.getSuggestedMusicbyID(count = count, userId = userId)
    lst = []
    for music in suggested:
        resp = {}
        processMusicObject(music, resp)
        lst.append(resp)
        if printOutput:
            pp.pprint(resp)
    return lst

#### Util Functions ####

def processTikTokObject(tiktok:dict, resp: dict) -> dict:
    id = tiktok['id']
    resp[id] = {}
    resp[id]['desc'] = tiktok.get('desc')
    resp[id]['createTime'] = tiktok.get('createTime')
    resp[id]['playAddr'] = tiktok.get('video', {}).get('playAddr')
    resp[id]['username'] = tiktok.get('author', {}).get('uniqueId')
    resp[id]['diggCount'] = tiktok.get('stats', {}).get('diggCount')
    resp[id]['shareCount'] = tiktok.get('stats', {}).get('shareCount')
    resp[id]['commentCount'] = tiktok.get('stats', {}).get('commentCount')
    resp[id]['playCount'] = tiktok.get('stats', {}).get('playCount')

def processMusicObject(music:dict, resp: dict) -> dict:
    id = music.get('id')
    resp[id] = {}
    resp[id]['title'] = music.get('title')
    resp[id]['desc'] = music.get('description')
    resp[id]['playUrl'] = music.get('extraInfo', {}).get('playUrl')
    resp[id]['videoCount'] = music.get('extraInfo', {}).get('posts')

def usernameToUserId(username: str) -> str:
    obj = api.getUser(username)
    userInfo = obj.get('userInfo', {})
    userId = userInfo.get('user', {}).get('id')
    return userId

# tiktoks = getTrendingTikToks(3, True)
# hashtags = getTrendingHashtags(3, True)
# songs = getTrendingMusic(3, True)
# hashtagInfo = getHashtagInfo("tiktokwithalexa", True)
# user = getUserInfo('newt', True)
# userLiked = getUserLikedByUsername('kyliejenner', 3, True)

# getSuggestedUsers('kyliejenner', 3, False, True)
# getSuggestedUsers('kyliejenner', 3, True, True)

# getSuggestedHashtags('kyliejenner', 3, False, True)
# getSuggestedHashtags('kyliejenner', 3, True, True)

# getSuggestedMusic('kyliejenner', 3, False, True)
# getSuggestedMusic('kyliejenner', 3, True, True)