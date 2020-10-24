import flask, os
from flask import Flask, request
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

API_SERVICE = 'youtube'
API_VERSION = 'v3'
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


@app.route('/')
def run():
    client_secret = getClientSecretPath(CLIENT_SECRET_NAME)
    print(client_secret)

    return 'ACCEPTED'


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run()
