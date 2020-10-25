import flask, os, json
from flask import Flask, request, session
import google_auth_oauthlib.flow
import googleapiclient.discovery
import google

API_SERVICE = 'youtube'
API_VERSION = 'v3'

YOUTUBE_SSL = ['https://www.googleapis.com/auth/youtube.force-ssl']

VIDEO_ID = 'lqZinLXwxPo'  # this video u want to update
CLIENT_SECRET_NAME = 'client_secret.json'  # client_secret coming from google api

app = Flask(__name__)
app.secret_key = 'sandrocagara'  # this is for creating session


# The session is unavailable because no secret key was set.  Set the secret_key on the application to something
# unique and secret.

def getBuildApiService(credentials):
    return googleapiclient.discovery.build(API_SERVICE, API_VERSION, credentials=credentials)


def getClientSecretPath(filename):
    try:
        file = open(filename)
        path = os.path.realpath(file.name)
        file.close()
    except FileNotFoundError as e:
        print('Error Message: ', e)
        return None
    return path


def storeCredentials(credentials):
    if credentials:
        flask.session['credentials'] = {}

    get_credentials = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'id_token': credentials.id_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'quota_project_id': credentials.quota_project_id

    }
    flask.session['credentials'] = json.dumps(get_credentials)


def authenticate(client_secret):
    googleFlow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(client_secret, YOUTUBE_SSL)
    googleFlow.redirect_uri = flask.url_for('callback', _external=True)
    authorization_url, state = googleFlow.authorization_url(access_type='offline', include_granted_scopes='true')
    flask.session['state'] = state
    return authorization_url


def getVideoStatistics(credentials):
    youtube = getBuildApiService(credentials)
    requests = youtube.videos().list(part="statistics", id=VIDEO_ID)
    response = requests.execute()
    return response


def getVideoTitleWithViews(credentials):
    videoInfo = getVideoStatistics(credentials)
    # print(videoInfo["items"][0]["statistics"])
    title = "Music Taste has " + str(videoInfo["items"][0]["statistics"]["viewCount"]) + " Views for this video."
    return title


@app.route('/title/update')
def titleUpdate():
    credentials = json.loads(flask.session['credentials'])
    credential = google.oauth2.credentials.Credentials(**credentials)
    youtube = getBuildApiService(credential)
    title = getVideoTitleWithViews(credential)
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
    return 'YOUTUBE TITLE UPDATED'


@app.route('/callback')
def callback():
    state = flask.session['state']
    client_secret = getClientSecretPath('client_secret.json')
    if not client_secret:
        return 'CREDENTIALS NOT STORED'

    googleFlow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secret,
        scopes=YOUTUBE_SSL,
        state=state)
    googleFlow.redirect_uri = flask.url_for('callback', _external=True)  # where came from link

    response = flask.request.url
    googleFlow.fetch_token(authorization_response=response)

    credentials = googleFlow.credentials
    # Returns credentials from the OAuth 2.0 session.
    # Returns: The constructed credentials.
    # Return type: https://google-auth.readthedocs.io/en/stable/reference/google.oauth2.credentials.html
    # Raises: ValueError – If there is no access token in the session.
    storeCredentials(credentials)
    print(flask.session['credentials'])
    return flask.redirect('/title/update')


@app.route('/auth')
def auth():
    client_secret = getClientSecretPath(CLIENT_SECRET_NAME)
    if not client_secret:
        return None
    # print(client_secret)
    authorization_url = authenticate(client_secret)

    return flask.redirect(authorization_url)


@app.route('/')
def main():
    print('APP STARTED')
    return 'd'


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run()
    session.permanent = True
