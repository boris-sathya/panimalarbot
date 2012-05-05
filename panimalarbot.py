import twitter
import yaml
import time
import pickle
import re
global match, api, msg, oldID
import random
msg = ''

#RegEx for parsing twitter handle from retrived mentions
handle = re.compile(
    '''
    #catches @twitterhandle
    (?<=@)
    ([\w\d_]+)       
    ''',
    re.UNICODE | re.VERBOSE)

#UTF_CHARS = ur'a-z0-9_\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u00ff'
#TAG_EXP = ur'(^|[^0-9A-Z&/]+)(#|\uff03)([0-9A-Z_]*[A-Z_]+[%s]*)' % UTF_CHARS
#TAG_REGEX = re.compile(TAG_EXP, re.UNICODE | re.IGNORECASE)


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

def get_and_post_replies(old):
    cache_msg_to_post = ' '
    global match, api
    while(1):
        try:
            i = 0
            repl = api.GetReplies()
            newID = int(repl[i].id)
            while(newID != old):
                print repl[i].text+", by @"+repl[i].user.screen_name
                for match in handle.findall(repl[i].text):
                    if(match=="panimalarbot"):
                        #search_term = [terms for terms in repl[i].text.split() if terms.startswith("#")]
                        pass
                print "Match is", match
                extract_handle()
                msg_to_post = "@"+repl[i].user.screen_name+" "+msg
                if(msg_to_post == cache_msg_to_post):
                    msg_to_post = msg_to_post + random.randint(0,1000)
                    cache_msg_to_post = msg_to_post
                try:
                    api.PostUpdate(msg_to_post, in_reply_to_status_id=repl[i].id)
                    print "Msg posted is", msg_to_post
                    i = i+1
                    newID = int(repl[i].id)
                except twitter.TwitterError:
                    print "Something happend.. Saving ID's to file.. Not to Worry"
                    fileObj = open("idstore",'r+')
                    old = repl[0].id
                    fileObj.seek(0)
                    fileObj.write(old)
                    fileObj.close()
                    return  
            old = int(repl[0].id)
            print "No New Tweets !!"
            print "Gonna sleep for a minute :)"
            time.sleep(60)
        except KeyboardInterrupt:
            fileObj = open("idstore", 'r+')
            fileObj.seek(0)
            fileObj.write(str(old))
            print "Exiting!!"
            return    

authenticate()
fileObj = open("idstore",'r+')
old = fileObj.read()
old = int(old)
get_and_post_replies(old)
