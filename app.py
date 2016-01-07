from pprint import pprint

from flask import Flask, request, Response, send_file

app = Flask(__name__)


@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/analytics/', methods=['POST'])
def api_root():
    print 'running api_root()'

    data = request.get_data()
    print type(data)
    print data
    print request.get_json()

    pprint(dict(request.headers))

    resp = Response('', 200)
    h = resp.headers

    h['Access-Control-Allow-Origin'] = '*'
    h['Access-Control-Allow-Methods'] = 'POST'
    h['Access-Control-Max-Age'] = str(21600)

    # resp = Response('', 200)
    # resp.headers['Access-Control-Allow-Origin'] = '*'
    # # resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    return resp

@app.route('/a.js')
def script():
    print 'serving a.js'
    return send_file('static/app.js', mimetype='text/javascript')

if __name__ == '__main__':
    app.debug = True  # server auto-reload on code changes
    app.run(port=5001)
