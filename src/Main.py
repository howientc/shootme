'''
Created on Jan 14, 2017

@author: howie
'''
import gtk
from flask import Flask, render_template, request, jsonify, send_from_directory
from multiprocessing import Process, Queue

from GtkSlide import SlideShow
SECONDS_BETWEEN_PICTURES = 3
delay = SECONDS_BETWEEN_PICTURES

app = Flask(__name__,static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = False

queue = Queue()

def main(queue, delay):
    try:
        gui = SlideShow(queue,delay)
        gtk.main()
    except:
        pass
#         shutdown_server()
        

@app.route('/')
def flashPage():
    global delay
    return render_template('shootme.html', delay=delay)

@app.route('/shoot',methods=['POST'])
def shoot():
    queue.put(-1)
    return jsonify("")

@app.route('/delay',methods=['POST'])
def set_delay():
    info = request.get_json(force=True)
    print info
    global delay
    delay = int(info['delay'])
    queue.put(delay)
    print "setting delay to ", delay
    return jsonify("")

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
    
if __name__ == '__main__':
    try:
        p = Process(target=main,args=(queue,delay))
        p.start()
        app.run()
        p.join()
    except:
        p.terminate()
#         shutdown_server()

