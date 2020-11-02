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


def createBody(title=None):
    body = helpers.getBodyPath('body.json')

    with open(body) as file:
        data = json.load(file)
    categoryId = data['snippet']['categoryId']
    defaultLanguage = data['snippet']['defaultLanguage']

    if not title:
        title = data['snippet']['title']

    description = str('\n'.join(map(str, data['snippet']['description'])))

    body = {
        "id": VIDEO_ID,
        "snippet": {
            "categoryId": categoryId,
            "defaultLanguage": defaultLanguage,
            "title": title,
            "description": description,
        },
    }

    return body


@app.route('/thumbnail/update')
def thumbnailUpdate():
    credentials_with_token = helpers.getClientSecretWithToken(CLIENT_SECRET_WITH_TOKEN)
    credentials = google.oauth2.credentials.Credentials(**credentials_with_token)
    if credentials.expired:
        return 'TOKEN EXPIRED'
    youtube = helpers.getBuildApiService(credentials, API_SERVICE, API_VERSION)
    requests = youtube.thumbnails().set(
        videoId=VIDEO_ID,
        media_body=helpers.getImagePath("thumbnail.jpg")
    )
    print(requests.execute())
    return 'YOUTUBE THUMBNAIL UPDATED'


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
        requests = youtube.videos().update(part="snippet", body=createBody())
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
