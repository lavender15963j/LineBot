from django.shortcuts import render

# Create your views here.
import json
import sys
import requests
import urllib.request
import urllib.error
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def debug(request):
    print(request.POST.get('text'))
    return HttpResponse("POST")

def printDebug(text):
    requests.post("http://140.119.96.58:8000/debug/", data={"text": text,})
    
    

@csrf_exempt
def elapp(request):
    printDebug(str(request.POST))
    return HttpResponse("GET")
    
    (mid,text)=_decode_json(request)
    _to_LINE_server(mid, text)
    if request.method == 'GET':
        return HttpResponse("GET")
    elif request.method == 'POST':  
        return HttpResponse("POST")
        #return HttpResponse("POST")

def _decode_json(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode) 
    _mid=body["result"][0]["content"]["from"]
    _text=body["result"][0]["content"]["text"]  
    return (_mid, _text)

def _to_LINE_server(_mid, _text):
    payload = {
        "to": [_mid],
        "toChannel":1383378250,
        "eventType":"138311608800106203",    
        "content":{
            "contentType":1,
            "toType":1,
            "text":_text
            #"text":body_unicode for debug(JSON object)
        } 
    }

    req=urllib.request.Request("https://trialbot-api.line.me/v1/events",
        data=json.dumps(payload).encode('utf8'),
        headers={
            "Content-type": "application/json; charset=UTF-8",
            "X-Line-ChannelID": "Channel ID",
            "X-Line-ChannelSecret": "Channel Secret",
            "X-Line-Trusted-User-With-ACL": "u2b3adc9a2d583fb47b3e942f0043d339"
        })

    try:
        with urllib.request.urlopen(req) as response:
            print(response.read())
    except urllib.error.HTTPError as err: 
        print(err)