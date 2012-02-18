import twitter
import yaml
import time
import pickle
import re
global match, api, msg
import random

#RegEx for parsing twitter handle from retrived mentions
handle = re.compile(
    '''
    #catches @twitterhandle
    (?<=@)
    ([\w\d_]+)       
    ''',
    re.UNICODE | re.VERBOSE)

#Performs OAuth authentication, place all the neccessary keys in access.yaml
def authenticate():
    global api
    data = yaml.load(open("access.yaml"))
    api = twitter.Api(consumer_key=data['consumer-key'],consumer_secret=data['consumer-secret'],access_token_key=data['access-key'],access_token_secret=data['access-secret'])

#Parses response.yaml to search and reply with relevant messages according to twitterhandles, fill your responses in response.yaml
def extract_handle():
    global match, msg
    comments = yaml.load(open("response.yaml"))
    for name in comments['name']:
        if(name['handle']==match):
            msg = random.choice(name['response'])

#Module which checks for mentions and replies to the mentioner and the person mentioned
#current version supports only one mentioned person
def get_and_post_replies():
    i = 0
    global match, api
    fileObj = open("idstore",'r+')
    oldID = fileObj.read()
    oldID = int(oldID)
    repl = api.GetReplies()
    newID = int(repl[i].id)
    while(newID != oldID):
        print repl[i].text+", by @"+repl[i].user.screen_name
        for match in handle.findall(repl[i].text):
            if(match=="panimalarbot"):
                pass
        extract_handle()
        localtime = time.asctime(time.localtime(time.time()))
        msg_to_post = "@"+repl[i].user.screen_name+" "+msg
        api.PostUpdate(msg_to_post, in_reply_to_status_id=repl[i].id)
        i = i+1
        newID = int(repl[i].id)
    oldID = str(repl[0].id)
    fileObj.seek(0)
    fileObj.write(oldID)
    print "No job, Master!"


authenticate()
while(1):
    get_and_post_replies()
    print "Gonna sleep for 60 Secs"
    time.sleep(60)
