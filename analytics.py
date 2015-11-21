from base64 import b64decode
import datetime
import json
import os
from urlparse import parse_qsl, urlparse

from flask import Flask, Response, abort, request
import peewee

# 1 pixel transparent GIF, base64-encoded.
BEACON = b64decode('R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')


# Store the database file in the app directory.
APP_DIR = os.path.dirname(__file__)
DATABASE_NAME = os.path.join(APP_DIR, 'analytics.db')
DOMAIN = 'http://127.0.0.1:5300'  # TODO: change me.


# Simple JavaScript which will be included and executed on the client-side.
JAVASCRIPT = """(function(){
    var d=document,i=new Image,e=encodeURIComponent;
    i.src='{DOMAIN}/a.gif?url='+e(d.location.href)+'&ref='+e(d.referrer)+'&t='+e(d.title);
    })()""".replace('\n', '')


# Flask application settings.
DEBUG = bool(os.environ.get('DEBUG'))
SECRET_KEY = 'secret - change me'  # TODO: change me.


app = Flask(__name__)
app.config.from_object(__name__)

database = peewee.SqliteDatabase(DATABASE_NAME)


class JSONField(peewee.TextField):
    """Store JSON data in a TextField."""

    def python_value(self, value):
        if value is not None:
            return json.loads(value)

    def db_value(self, value):
        if value is not None:
            return json.dumps(value)


class PageView(peewee.Model):
    domain = peewee.CharField()
    url = peewee.TextField()
    timestamp = peewee.DateTimeField(default=datetime.datetime.now, index=True)
    title = peewee.TextField(default='')
    ip = peewee.CharField(default='')
    referrer = peewee.TextField(default='')
    headers = JSONField()
    params = JSONField()

    @classmethod
    def create_from_request(cls):
        parsed = urlparse(request.args['url'])
        params = dict(parse_qsl(parsed.query))

        return PageView.create(
            domain=parsed.netloc,
            url=parsed.path,
            title=request.args.get('t') or '',
            ip=request.headers.get('X-Forwarded-For', request.remote_addr),
            referrer=request.args.get('ref') or '',
            headers=dict(request.headers),
            params=params)

    class Meta:
        database = database


@app.route('/a.gif')
def analyze():
    if not request.args.get('url'):
        abort(404)

    with database.transaction():
        PageView.create_from_request()

    response = Response(app.config['BEACON'], mimetype='image/gif')
    response.headers['Cache-Control'] = 'private, no-cache'
    return response

@app.route('/a.js')
def script():
    return Response(
        app.config['JAVASCRIPT'].format(DOMAIN=app.config['DOMAIN']),
        mimetype='text/javascript'
    )

@app.errorhandler(404)
def not_found(e):
    return Response('Not found.')

if __name__ == '__main__':
    database.create_tables([PageView], safe=True)
    app.run()
