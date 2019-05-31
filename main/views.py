import json
import random

import requests

from django.views import generic
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from main.models import Chat
from django.db.models import Q

TOKEN = "eJiX8m+0k2Zg5y9d9VSep2E3IkSO5FkTS3D0tI7+hxFXegMDuak2KGMU3l/u3VXpb9ueFdq6Md7xTL8ibc0SCicorMM50327kU4gZQ+tEddaANMaw+dIUoRO8spm5+W1bL0axuaP6uJOjPNpmkKVXQdB04t89/1O/w1cDnyilFU="

WATSON_API_URL = "https://nccu-107356017.mybluemix.net/linebot" 
WATSON_API_URL = "https://nccu-106356015.mybluemix.net/hw2" 

PAGE_ACCESS_TOKEN = "EAARyZADnEubsBAFZBMZBMQb2ku8fLpCRO9Xmf4pjpTSMSMCtsIYs8OXIv9DnRPO01EAvI9DOVVqxvTUqZBVcxyMGrI6j0wWWZA7GiKAoLYdSbP0LccmAD4FJv5f08qgC55BP7pmQT3KrjOfwFvq6rCI7F8dwYMevpkVEjhFXRgbakTvFxgQqQnaEn87dwZBUUZD"
VERIFY_TOKEN = "lavender15963j"

def reply(msg, text):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        'Content-Type': 'application/json',
        "Authorization": 'Bearer %s' % TOKEN,
    }
    payload = {
        'replyToken': msg['replyToken'],
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ]
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    
def replyImage(msg, imgUrl):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        'Content-Type': 'application/json',
        "Authorization": 'Bearer %s' % TOKEN,
    }
    payload = {
        'replyToken': msg['replyToken'],
        "messages": [
            {
                "type": "image",
                "originalContentUrl": imgUrl,
                "previewImageUrl": imgUrl
            }
        ]
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    
def replySticker(msg, pkgId, stickerId):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        'Content-Type': 'application/json',
        "Authorization": 'Bearer %s' % TOKEN,
    }
    payload = {
        'replyToken': msg['replyToken'],
        "messages": [
            {
                "type": "sticker",
                "packageId": str(pkgId),
                "stickerId": str(stickerId),
            }
        ]
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    
    
def postWatson(text):
    url = WATSON_API_URL
    r = requests.post(url, data={"text": text})
    
    data = json.loads(r.text)
    
    generic = data.get('output', {}).get('generic', [])
    indents = data.get('output', {}).get('indents', [])
    entities = data.get('output', {}).get('entities', [])
    
    return (generic, indents, entities)
  
def doReply(body_unicode):
    body = json.loads(body_unicode)
    
    msg = body["events"][0]
    type = msg['message']['type']
    
    # --- do reply ---    
    if type == "sticker":
        pkgId = random.choice('1')
        stickerId = random.choice(list(range(1, 10)))
        replySticker(msg, pkgId, stickerId)
    elif type == 'image':
        reply(msg, "姆咪看不懂這張圖片")
    elif type == 'text':
        text = msg['message']['text']
        
        chats = [{'keyword': chat.keyword.split(','), 'response': chat.response,} for chat in Chat.objects.all()]
        response = False
        for c in chats:
            rq = True
            for k in c['keyword']:
                if not k in text:
                    rq = False
            if rq:
                reply(msg, c['response'])
                response = True
        
        if not response:
            generic, indents, entities = postWatson(text)
            for g in generic:
                t = g['text']
                reply(msg, t)
    else:
        reply(msg, "姆咪智障，姆咪不懂")
    # ----------------
    
    return HttpResponse("POST")
    
def getResponse(chats, msg):
    for c in chats:
        rq = True
        for k in c['keyword']:
            if not k in msg:
                rq = False
        if rq:
            return c['response']
    return "小紫兒看不懂你在說什麼"
    

def replyMessager(text):
    body = json.loads(text)
    chats = [{'keyword': chat.keyword.split(','), 'response': chat.response,} for chat in Chat.objects.all()]
    chats.sort(key=lambda x: len(x['response']), reverse=True)
    
    for entry in body['entry']:
        for message in entry['messaging']:
            uid = message['sender']['id']
            msg = message['message']['text']
            
            postUrl = 'https://graph.facebook.com/v3.3/me/messages?access_token=%s' % PAGE_ACCESS_TOKEN
            
            req = getResponse(chats, msg)
            
            responseMsg = json.dumps({
                "recipient": {
                     "id": uid,
                }, 
                "message": {
                     "text": req,
                }
            })
            
            status = requests.post(postUrl, headers={"Content-Type": "application/json"}, data=responseMsg)
    return HttpResponse("POST")

@csrf_exempt
def debug(request):
    text = request.POST.get('text')
    print(text)
    return replyMessager(text)
    return doReply(text)

def printDebug(text):
    requests.post("http://140.119.96.18:8000/messager/webhook/", data=text)
    return
    
@csrf_exempt
def elapp(request):
    body_unicode = request.body.decode('utf-8')
    #printDebug(body_unicode)
    return doReply(body_unicode)
    
class MessagerBotView(generic.View):
    def get(self, request, *args, **kwargs):
        verify = request.GET.get('hub.verify_token')
        if verify == VERIFY_TOKEN:
            return HttpResponse(request.GET.get('hub.challenge'))
        else:
            return HttpResponse('Error, invalid token')
        
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(MessagerBotView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        msg = request.body.decode('utf-8')
        printDebug(msg)
        return HttpResponse('Success')