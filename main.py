from flask import Flask
import requests
from bs4 import BeautifulSoup
import base64
import os
import threading

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
OWNER = 'fancyotter99'
REPO = 'Chat'
PATH = 'users.txt'
SITE_URL = 'https://chat-le5h.onrender.com/secret-users?key=letmein'

def get_pre_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    pres = soup.find_all('pre')
    return '\n\n'.join(pre.get_text() for pre in pres).strip()

def get_file_sha():
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()['sha']
    return None

def update_github_file(content, sha=None):
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json'
    }
    message = 'Update file with extracted <pre> content'
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    data = {
        'message': message,
        'content': encoded_content,
    }
    if sha:
        data['sha'] = sha

    r = requests.put(url, headers=headers, json=data)
    print(r.json())

def update_task():
    try:
        r = requests.get(SITE_URL)
        r.raise_for_status()
        pre_content = get_pre_content(r.text)
        sha = get_file_sha()
        update_github_file(pre_content, sha)
        print('Update successful!')
    except Exception as e:
        print('Error during update:', e)

@app.route('/')
def run_update():
    # Run update in a thread to avoid timeout
    threading.Thread(target=update_task).start()
    return 'Update triggered!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
