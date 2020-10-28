import flask
import google
import google_auth_oauthlib.flow
import json
import os
import sys
from flask import Flask, session
from Utils import helpers
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

API_SERVICE = os.getenv("API_SERVICE")
API_VERSION = os.getenv("API_VERSION")
YOUTUBE_SSL = os.getenv("YOUTUBE_SSL")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_SECRET_WITH_TOKEN = os.getenv("CLIENT_SECRET_WITH_TOKEN")
VIDEO_ID = os.getenv("VIDEO_ID")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SESSION_SECRET_KEY")


def createBody(title):
    body = {
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

WARNING: These videos may cause people with photosensitive epilepsy to convulse in seizures. Viewer discretion is 
advised.
        """,
        },
    }
    return body


@app.route('/title/update')
def titleUpdate():
    try:
        credentials_with_token = helpers.getClientSecretWithToken(CLIENT_SECRET_WITH_TOKEN)
        credentials = google.oauth2.credentials.Credentials(**credentials_with_token)
        if credentials.expired:
            # print('TOKEN EXPIRED')
            return 'TOKEN EXPIRED'
        youtube = helpers.getBuildApiService(credentials, API_SERVICE, API_VERSION)
        title = helpers.getVideoTitleWithViews(credentials, API_SERVICE, API_VERSION, VIDEO_ID)
        requests = youtube.videos().update(part="snippet", body=createBody(title))
        response = requests.execute()
        # print(response)
    except sys.exc_info()[0] as e:
        return "ERROR: " + str(e)
    return 'YOUTUBE TITLE UPDATED'


@app.route('/callback')
def callback():
    state = flask.session['state']
    client_secret = helpers.getPath(CLIENT_SECRET_WITH_TOKEN)
    response = flask.request.url
    if not client_secret:
        return 'CREDENTIALS NOT FOUND'
    googleFlow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(client_secret, scopes=YOUTUBE_SSL, state=state)
    googleFlow.redirect_uri = flask.url_for('callback', _external=True)  # where came from link
    googleFlow.fetch_token(authorization_response=response)

    credentials = googleFlow.credentials
    # Return type: https://google-auth.readthedocs.io/en/stable/reference/google.oauth2.credentials.html
    helpers.storeCredentials(credentials, CLIENT_SECRET_WITH_TOKEN)
    return flask.redirect('/title/update')


@app.route('/authenticate')
def auth():
    client_secret, client_secret_with_token = helpers.getPath(CLIENT_SECRET), helpers.getPath(CLIENT_SECRET_WITH_TOKEN)
    credentials = {}
    try:
        with open(client_secret_with_token) as file:
            credentials = json.load(file)
    except sys.exc_info()[0] as e:
        with open(client_secret) as file:
            credentials = json.load(file)
        helpers.createFileCredentials(client_secret_with_token, credentials)
    finally:
        if 'token' not in credentials['web']:
            authorization_url = helpers.authenticate(client_secret_with_token, YOUTUBE_SSL)
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
    app.run(debug=True)
    session.permanent = True
