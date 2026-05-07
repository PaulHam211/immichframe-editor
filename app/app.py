import os, sys, json, functools, docker
from flask import Flask, render_template, request, redirect, url_for, flash, Response

app = Flask(__name__)
app.secret_key = os.urandom(24)

SETTINGS_FILE = '/config/Settings.yml'
IMMICHFRAME_CONTAINER = 'immichframe'

def get_settings_account():
    import yaml
    with open(SETTINGS_FILE, 'r') as f:
        data = yaml.safe_load(f)
    return (data.get('Accounts') or [{}])[0]

def get_immich_people():
    import yaml, urllib.request
    try:
        account = get_settings_account()
        server_url = account.get('ImmichServerUrl', '')
        api_key = account.get('ApiKey', '')
        if not server_url or not api_key:
            return [], 'No server URL or API key'
        req = urllib.request.Request(f'{server_url}/api/people')
        req.add_header('x-api-key', api_key)
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        if isinstance(result, dict):
            people_list = result.get('people', [])
        elif isinstance(result, list):
            people_list = result
        else:
            return [], f'Unexpected response type: {type(result)}'
        return [(p['id'], p.get('name')) for p in people_list if p.get('name')], None
    except Exception as e:
        return [], str(e)

def get_immich_albums():
    import urllib.request
    try:
        account = get_settings_account()
        server_url = account.get('ImmichServerUrl', '')
        api_key = account.get('ApiKey', '')
        if not server_url or not api_key:
            return [], 'No server URL or API key'
        req = urllib.request.Request(f'{server_url}/api/albums')
        req.add_header('x-api-key', api_key)
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        if isinstance(result, dict):
            albums_list = result.get('albums', [])
        elif isinstance(result, list):
            albums_list = result
        else:
            return [], f'Unexpected response type: {type(result)}'
        return [(a['id'], a.get('albumName', 'Untitled')) for a in albums_list], None
    except Exception as e:
        return [], str(e)

# Thumbnail cache
_thumb_cache = {}
_thumb_max = 200

@app.route('/thumb/<person_id>')
def thumb(person_id):
    import urllib.request
    if person_id in _thumb_cache:
        return Response(_thumb_cache[person_id], mimetype='image/jpeg')
    try:
        account = get_settings_account()
        server_url = account.get('ImmichServerUrl', '')
        api_key = account.get('ApiKey', '')
        req = urllib.request.Request(f'{server_url}/api/people/{person_id}/thumbnail')
        req.add_header('x-api-key', api_key)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        if len(_thumb_cache) < _thumb_max:
            _thumb_cache[person_id] = data
        return Response(data, mimetype='image/jpeg')
    except:
        return '', 404

@app.route('/')
def index():
    import yaml
    with open(SETTINGS_FILE, 'r') as f:
        data = yaml.safe_load(f)

    account = (data.get('Accounts') or [{}])[0]
    general = data.get('General', {})
    selected_people = account.get('People', [])
    selected_albums = account.get('Albums', [])

    people, _ = get_immich_people()
    albums, _ = get_immich_albums()

    return render_template('edit.html',
                         general=general,
                         selected_people=selected_people,
                         selected_albums=selected_albums,
                         people=people,
                         albums=albums)

@app.route('/save', methods=['POST'])
def save():
    import yaml, subprocess

    selected_people = request.form.getlist('people')
    selected_albums = request.form.getlist('albums')

    with open(SETTINGS_FILE, 'r') as f:
        data = yaml.safe_load(f)

    if data.get('Accounts') and len(data['Accounts']) > 0:
        data['Accounts'][0]['People'] = selected_people
        data['Accounts'][0]['Albums'] = selected_albums

    with open(SETTINGS_FILE, 'w') as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    try:
        client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
        client.containers.get(IMMICHFRAME_CONTAINER).restart()
        flash(f'Saved! ImmichFrame restarting...', 'success')
    except Exception as e:
        flash(f'Saved but could not restart ImmichFrame: {e}', 'warning')

    return redirect(url_for('index'))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)
