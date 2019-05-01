import json
import requests

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

TOKEN = "eJiX8m+0k2Zg5y9d9VSep2E3IkSO5FkTS3D0tI7+hxFXegMDuak2KGMU3l/u3VXpb9ueFdq6Md7xTL8ibc0SCicorMM50327kU4gZQ+tEddaANMaw+dIUoRO8spm5+W1bL0axuaP6uJOjPNpmkKVXQdB04t89/1O/w1cDnyilFU="

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
    url = "https://nccu-107356017.mybluemix.net/linebot"
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
    generic, indents, entities = postWatson(text)
    for g in generic:
        t = g['text']
        reply(msg, text)
    # ----------------
    
    return HttpResponse("POST")

@csrf_exempt
def debug(request):
    text = request.POST.get('text')
    print(text)
    return doReply(text)

def printDebug(text):
    requests.post("http://140.119.96.43:8000/debug/", data={"text": text,})
    
@csrf_exempt
def elapp(request):
    printDebug(request.body.decode('utf-8'))
    body_unicode = request.body.decode('utf-8')
    return doReply(body_unicode)