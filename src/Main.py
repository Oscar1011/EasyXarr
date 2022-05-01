from gevent import monkey
from gevent.pywsgi import WSGIServer

monkey.patch_all()

import TMDB
import threading
from Sonarr import Sonarr
from Radarr import Radarr
from flask import Flask, request
import xml.etree.cElementTree as ET
import sys
from WXBizMsgCrypt import WXBizMsgCrypt
import Logger
from XarrNotify import SonarrData, RadarrData
import json
from Config import WXHOST_APIKEY, QWX_Token, QWX_EncodingAESKey, CorpID, Host, Port

app = Flask(__name__)


@app.route('/XarrNotify', methods=['POST'])
def XarrNotify():
    try:
        key = request.args.get("apikey")
        if key != WXHOST_APIKEY:
            Logger.error(f'异常访问，请求 apikey 错误')
            return ''
        arr_type = request.args.get("type")
        data = json.loads(request.data)
        if arr_type == 'sonarr':
            Logger.info('sonarr')
            SonarrData(data).exec()
        elif arr_type == 'radarr':
            RadarrData(data).exec()
    except:
        ExceptionInformation = sys.exc_info()
        Text = f'[通知]运行异常,异常信息为:{ExceptionInformation}'
        Logger.error(Text)
        return ''
    return ''


@app.route('/addMovie', methods=['GET'])
def addMovie():
    try:
        key = request.args.get("apikey")
        if key != WXHOST_APIKEY:
            Logger.error(f'异常访问添加电影，请求 apikey 错误')
            return ''
        tmdbId = request.args.get("tmdbId")
        Logger.info(f'[添加电影] tmdbId={tmdbId}')
        t = threading.Thread(target=Radarr.add_movie, name="Thread-addMovie", kwargs={'tmdbId': tmdbId})
        t.start()
        return '已请求添加'
    except:
        ExceptionInformation = sys.exc_info()
        Text = f'[添加电影]异常,异常信息为:{ExceptionInformation}'
        Logger.error(Text)
        return ''


@app.route('/addSeries', methods=['GET'])
def addSeries():
    try:
        key = request.args.get("apikey")
        if key != WXHOST_APIKEY:
            Logger.error(f'异常访问添加剧集，请求 apikey 错误')
            return ''
        tvdbId = request.args.get("tvdbId")
        tmdbId = request.args.get("tmdbId")
        Logger.info(f'[添加剧集] tvdbId={tvdbId}')
        t = threading.Thread(target=Sonarr.add_series, name="Thread-addSeries", kwargs={'tvdbId': tvdbId,'tmdbId':tmdbId})
        t.start()
        return '已请求添加'
    except:
        ExceptionInformation = sys.exc_info()
        Text = f'[添加剧集]异常,异常信息为:{ExceptionInformation}'
        Logger.error(Text)
        return ''


# 响应企业微信
@app.route('/', methods=['GET', 'POST'])
def QWX():
    try:
        if request.method == 'GET':
            msg_signature = request.args.get("msg_signature")
            timestamp = request.args.get("timestamp")
            nonce = request.args.get("nonce")
            echostr = request.args.get("echostr")
            QWX_Crypt = WXBizMsgCrypt(QWX_Token, QWX_EncodingAESKey, CorpID)
            ret, result = QWX_Crypt.VerifyURL(msg_signature, timestamp, nonce, echostr)
            if ret == 0:
                return result
            else:
                Logger.error(f"GET请求异常{ret}{result}")
                return ''

        # ---接收消息---
        msg_signature = request.args.get("msg_signature")
        timestamp = request.args.get("timestamp")
        nonce = request.args.get("nonce")
        data = request.data
        QWX_Crypt = WXBizMsgCrypt(QWX_Token, QWX_EncodingAESKey, CorpID)
        ret, message = QWX_Crypt.DecryptMsg(data, msg_signature, timestamp, nonce)
        XmlTree = ET.fromstring(message)
        ToUser = XmlTree.find("FromUserName").text
        MsgType = XmlTree.find("MsgType").text
        Logger.info(f'[消息接收接口]接收到来自[{ToUser}]的[{MsgType}]类型消息')
        if MsgType == 'event':
            EventType = XmlTree.find("Event").text
            if EventType == 'click':
                EventKey = XmlTree.find("EventKey").text
                Logger.info(EventKey)
                if EventKey in TMDB.TMBD_FUNC_LIST:
                    t = threading.Thread(target=TMDB.getTMDBInfo, name="TMDBHelper", kwargs={'type': EventKey})
                    t.start()

        elif MsgType == 'text':
            Content = XmlTree.find("Content").text.split(" ")
            Command = Content[0]
            if len(Content) == 2:
                if Command == '电视剧':
                    name = Content[1]
                    t = threading.Thread(target=Sonarr.search, name="Sonarr-search", kwargs={'name': name})
                    t.start()
                elif Command == '电影':
                    name = Content[1]
                    t = threading.Thread(target=Radarr.search, name="Radarr-search", kwargs={'name': name})
                    t.start()
        return ""
        # ---接收消息---
    except Exception:
        ExceptionInformation = sys.exc_info()
        Text = f'[消息接收接口]运行异常,异常信息为:{ExceptionInformation}'
        Logger.error(Text)
        return ""


if __name__ == '__main__':
    Logger.info("[服务启动]启动服务")
    WSGIServer((Host, Port), app).serve_forever()
