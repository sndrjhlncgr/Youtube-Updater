import flask, os
from flask import Flask, request
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

API_SERVICE = 'youtube'
API_VERSION = 'v3'

YOUTUBE_SSL = ['https://www.googleapis.com/auth/youtube.force-ssl']

VIDEO_ID = 'lqZinLXwxPo'
CLIENT_SECRET_NAME = 'client_secret.json'

app = Flask(__name__)


def getClientSecretPath(filename):
    global path
    try:
        file = open(filename)
        path = os.path.realpath(file.name)
        file.close()
    except FileNotFoundError as e:
        print('Error Message: ', e)
        return None
    return path


def authenticate(client_secret):
    googleFlow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(client_secret, YOUTUBE_SSL)
    googleFlow.redirect_uri = flask.url_for('callback', _external=True)
    authorization_url, state = googleFlow.authorization_url(access_type='offline', include_granted_scopes='true')
    return authorization_url


@app.route('/callback')
def callback():
    print(request.args.get('state'))
    return 's'


@app.route('/')
def main():
    client_secret = getClientSecretPath(CLIENT_SECRET_NAME)
    if not client_secret:
        print('client secret not found')
    print(client_secret)
    authorization_url = authenticate(client_secret)

    return flask.redirect(authorization_url)


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run()
