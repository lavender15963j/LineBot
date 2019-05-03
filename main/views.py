import json
import requests

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

TOKEN = "eJiX8m+0k2Zg5y9d9VSep2E3IkSO5FkTS3D0tI7+hxFXegMDuak2KGMU3l/u3VXpb9ueFdq6Md7xTL8ibc0SCicorMM50327kU4gZQ+tEddaANMaw+dIUoRO8spm5+W1bL0axuaP6uJOjPNpmkKVXQdB04t89/1O/w1cDnyilFU="

WATSON_API_URL = "https://nccu-107356017.mybluemix.net/linebot" 
WATSON_API_URL = "https://nccu-106356015.mybluemix.net/hw2" 

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
    text = msg['message']['text']
    
    # --- do reply ---    
    # if text == 天氣:
        # 查詢 API
        # reply(天氣)
    # elif text == 餐廳景點:
        # 找餐廳
        # reply(餐廳景點)
    # else:
        # 傳給 WationAPI
        # reply(聊天)
        
    generic, indents, entities = postWatson(text)
    for g in generic:
        t = g['text']
        reply(msg, t)
    # ----------------
    
    return HttpResponse("POST")

@csrf_exempt
def debug(request):
    text = request.POST.get('text')
    print(text)
    return doReply(text)

def printDebug(text):
    requests.post("http://140.119.96.43:8000/debug/", data={"text": text,})
    return
    
@csrf_exempt
def elapp(request):
    body_unicode = request.body.decode('utf-8')
    printDebug(body_unicode)
    return doReply(body_unicode)