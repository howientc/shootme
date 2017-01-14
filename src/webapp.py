from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

import requests
import json
import logging
import sys

app = Flask(__name__,static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = False
# app.debug=True
#socketio = SocketIO(app)


class WebApp():
    def __init__(self, xio=False):
        self.controller = None
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        self.log = logging.getLogger("web")
        self.base_url = None
        
        
#     def run(self):
    def start(self):
        self.controller = Controller(self.log)
        self.controller.batchUpdates = True
        controller = self.controller
        controller.setTimeoutMultiplier(4)
        controller.configure()
        socketio.emit("stateChange","start",broadcast=True)

        controller.addStateListener(lambda info: self.onUpdateStateInfo(info))
        if self._xio:
            self._xioView = XioView(deviceDescriptors=self.controller.deviceDescriptors, hubs = self.controller.hubs)
            controller.addStateListener(lambda info: self._xioView.onUpdateStateInfo(info))
         
        call_repeatedly(1, lambda: controller.onPollingTick(0))
        call_repeatedly(2,lambda: controller.onUpdateTrigger(0))
 
    def onUpdateStateInfo(self,info):
        if not self.base_url: #ignore until we have a page listening
            return
        url = self.base_url + 'stateChange'
        fullInfo = info.copy() # get complete info, not just what changed
        if fullInfo.get('state'):
            fullInfo['stateClass'] = stateToClass[fullInfo['state']]
        if fullInfo.get('label'):
            fullInfo['label'] = fullInfo['label'].replace("\n",'<br>')
        if fullInfo.get('stateLabel'):
            fullInfo['stateLabel'] = fullInfo['stateLabel'].replace("\n",'<br>')

        payload = fullInfo #{'info': info}
        headers = {'content-type': 'application/json'}

        requests.post(url, data=json.dumps(payload), headers=headers) #post message to flask. This makes sure that socketio uses main thread

@app.route('/stateChange',methods=['POST'])
def stateChange():
    info = request.get_json()
    socketio.emit("stateChange",info,broadcast = True)
    return jsonify("")

# @app.route('/js/<path:path>')
# def send_js(path):
#     return send_from_directory('js', path)
#         
# @app.route('/css/<path:path>')
# def send_css(path):
#     return send_from_directory('web/css', path)

stateToClass = {RunState.PASSIVE_STATE: 'passive', RunState.PASS_STATE: 'success', RunState.FAIL_STATE: 'fail', RunState.PROMPT_STATE: 'prompt', RunState.ACTIVE_STATE:'active', RunState.PAUSED_STATE:'paused', RunState.IDLE_STATE: 'passive', RunState.DISCONNECTED_STATE: 'disconnected'}
    
@app.route('/')
def flashPage():
#     WebApp.base_url = request.base_url
#     print "base url is" + WebApp.base_url
    WebApp.base_url = "http://127.0.0.1/"

    return render_template('deviceTable.html', stateInfoArray=WebApp.controller.stateInfo.values(), stateToClass=stateToClass)
 
@app.route('/config')
def configPage():
    return render_template('chip_config.html')

if __name__ == '__main__':
    webApp = WebApp(True)
    webApp.start()
    socketio.run(app, host="0.0.0.0",port=80)

