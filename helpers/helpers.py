import json
import os
import sys
import flask
import google_auth_oauthlib
import googleapiclient.discovery


def getBuildApiService(credentials, api_service, api_version):
    return googleapiclient.discovery.build(api_service, api_version, credentials=credentials)


def authenticate(client_secret_with_token, youtube_ssl):
    try:
        googleFlow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(client_secret_with_token, youtube_ssl)
        googleFlow.redirect_uri = flask.url_for('callback', _external=True)
        authorization_url, state = googleFlow.authorization_url(access_type='offline', include_granted_scopes='true')
        flask.session['state'] = state
    except sys.exc_info()[0] as err:
        return '/error'
    return authorization_url


def getFilePath(folder, filename):
    try:
        file = open(folder + '/' + filename, 'r+')
        path = os.path.normpath(file.name)
        file.close()
    except sys.exc_info()[0] as e:
        print('Error Message: ', e)
        return None
    return path


def createFileCredentials(filename, credentials):
    createCredentials = open(filename, 'w')
    createCredentials.write(json.dumps(credentials))
    createCredentials.close()


def storeCredentials(credentials, filename):
    client_secret_with_token = getFilePath('clients', filename)
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


def getVideoStatistics(credentials, api_service, api_version, video_id):
    youtube = getBuildApiService(credentials, api_service, api_version)
    requests = youtube.videos().list(part="statistics", id=video_id)
    response = requests.execute()
    return response


def getVideoTitleWithViews(credentials, api_service, api_version, video_id):
    videoInfo = getVideoStatistics(credentials, api_service, api_version, video_id)
    title = "This Video Has {} Views".format(str(videoInfo["items"][0]["statistics"]["viewCount"]))
    return title


def getClientSecretWithToken(filename):
    client_secret_with_token = getFilePath('clients', filename)
    with open(client_secret_with_token) as file:
        credentials = json.load(file)
    return credentials["web"]
