import flask
import google
import google_auth_oauthlib.flow
import googleapiclient.discovery
import json
import os
import sys
from flask import Flask, session

API_SERVICE = 'youtube'
API_VERSION = 'v3'

YOUTUBE_SSL = ['https://www.googleapis.com/auth/youtube.force-ssl']

VIDEO_ID = 'lqZinLXwxPo'  # this video u want to update
CLIENT_SECRET = 'client_secret.json'  # client_secret coming from google api
CLIENT_SECRET_WITH_TOKEN = 'client_secret_with_token.json'

app = Flask(__name__)
app.secret_key = 'sandrocagara'  # this is for creating flask session

def getBuildApiService(credentials):
    return googleapiclient.discovery.build(API_SERVICE, API_VERSION, credentials=credentials)


def getPath(filename):
    try:
        file = open('clients/' + filename)
        path = os.path.realpath(file.name)
        file.close()
    except sys.exc_info()[0] as e:
        print('Error Message: ', e)
        return None
    return path


def createFileCredentials(filename, credentials):
    createCredentials = open(filename, 'w')
    createCredentials.write(json.dumps(credentials))
    createCredentials.close()


def storeCredentials(credentials):
    client_secret_with_token = getPath(CLIENT_SECRET_WITH_TOKEN)
    store_credentials = {
        'web': {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'id_token': credentials.id_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'quota_project_id': credentials.quota_project_id
        }
    }

    createFileCredentials(client_secret_with_token, store_credentials)


def getVideoStatistics(credentials):
    youtube = getBuildApiService(credentials)
    requests = youtube.videos().list(part="statistics", id=VIDEO_ID)
    response = requests.execute()
    return response


def getVideoTitleWithViews(credentials):
    videoInfo = getVideoStatistics(credentials)
    # print(videoInfo["items"][0]["statistics"])
    title = "Music Taste has {} Views for this video.".format(str(videoInfo["items"][0]["statistics"]["viewCount"]))
    return title


def getClientSecretWithToken():
    with open('clients/client_secret_with_token.json') as file:
        credentials = json.load(file)

    return credentials["web"]


def authenticate(client_secret):
    try:
        googleFlow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(client_secret, YOUTUBE_SSL)
        googleFlow.redirect_uri = flask.url_for('callback', _external=True)
        authorization_url, state = googleFlow.authorization_url(access_type='offline', include_granted_scopes='true')
        flask.session['state'] = state
    except sys.exc_info()[0] as e:
        return '/error'
    return authorization_url


@app.route('/title/update')
def titleUpdate():
    try:
        credentials_with_token = getClientSecretWithToken()
        credentials = google.oauth2.credentials.Credentials(**credentials_with_token)
        if credentials.expired:
            print('TOKEN EXPIRED')
            return 'TOKEN EXPIRED'
        youtube = getBuildApiService(credentials)
        title = getVideoTitleWithViews(credentials)

        requests = youtube.videos().update(
            part="snippet",
            body={
                "id": VIDEO_ID,
                "snippet": {
                    "categoryId": 10,
                    "defaultLanguage": "en",
                    "title": "Music Taste",
                    "description": """
                             Upload Playlist: https://bit.ly/392sDEP
8D Audio Playlist: https://bit.ly/2vwtuQ2
Danucd: https://bit.ly/37Seyta
Old but Gold Playlist: https://bit.ly/3dHQqfp
Hours Music Playlist: https://bit.ly/2Z0U1RJ
Subscriber Requested Music: https://bit.ly/3bsQga7

If you need a song removed on my channel, please e-mail me.

WARNING: These videos may cause people with photosensitive epilepsy to convulse in seizures. Viewer discretion is advised.
    """,
                },
            })

        response = requests.execute()
        print(response)
    except sys.exc_info()[0] as e:
        return "ERROR: " + str(e)

    return 'YOUTUBE TITLE UPDATED'


@app.route('/callback')
def callback():
    state = flask.session['state']
    client_secret = getPath(CLIENT_SECRET_WITH_TOKEN)
    if not client_secret:
        return 'CREDENTIALS NOT FOUND'

    googleFlow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(client_secret, scopes=YOUTUBE_SSL, state=state)
    googleFlow.redirect_uri = flask.url_for('callback', _external=True)  # where came from link
    response = flask.request.url
    googleFlow.fetch_token(authorization_response=response)

    credentials = googleFlow.credentials
    # Return type: https://google-auth.readthedocs.io/en/stable/reference/google.oauth2.credentials.html
    storeCredentials(credentials)
    return flask.redirect('/title/update')


@app.route('/authenticate')
def auth():
    client_secret, client_secret_with_token = getPath(CLIENT_SECRET), getPath(CLIENT_SECRET_WITH_TOKEN)
    credentials = {}
    try:
        with open(client_secret_with_token) as file:
            credentials = json.load(file)
    except FileNotFoundError as err:
        with open(client_secret) as file:
            credentials = json.load(file)

        createFileCredentials(client_secret_with_token, credentials)
    finally:
        if 'token' not in credentials['web']:
            authorization_url = authenticate(client_secret_with_token)
            return flask.redirect(authorization_url)

    return flask.redirect('/title/update')


@app.route('/')
def main():
    print('APP STARTED')
    return 'd'


@app.route('/error')
def error():
    return 'SOMETHING WENT WRONG'


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run()
    session.permanent = True
