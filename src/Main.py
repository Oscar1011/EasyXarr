from gevent import monkey
from gevent.pywsgi import WSGIServer

monkey.patch_all()

from flask import Flask, request
import sys
import Logger
from XarrNotify import SonarrData, RadarrData
import json
from Config import WXHOST_APIKEY, Host, Port

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

if __name__ == '__main__':
    Logger.info("[服务启动]启动服务")
    WSGIServer((Host, Port), app).serve_forever()
