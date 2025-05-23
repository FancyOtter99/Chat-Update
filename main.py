from flask import Flask
import requests
from bs4 import BeautifulSoup
import base64
import os
import threading

app = Flask(__name__)

# Shared GitHub config
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
OWNER = 'fancyotter99'
REPO = 'Chat'

# Define each task: (file path, source URL)
tasks = [
    {
        'path': 'users.txt',
        'url': 'https://chat-le5h.onrender.com/secret-users?key=letmein',
    },
    {
        'path': 'admins.json',
        'url': 'https://chat-le5h.onrender.com/secret-roles?key=letmein',
    },
    {
        'path': 'user_items.json',
        'url': 'https://chat-le5h.onrender.com/secret-items?key=letmein',
    }
]

def get_pre_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    pres = soup.find_all('pre')
    return '\n\n'.join(pre.get_text() for pre in pres).strip()

def get_file_sha(path):
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()['sha']
    return None

def update_github_file(content, path, sha=None):
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json'
    }
    message = f'Update {path} with extracted <pre> content'
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    data = {
        'message': message,
        'content': encoded_content,
    }
    if sha:
        data['sha'] = sha

    r = requests.put(url, headers=headers, json=data)
    print(f'Updated {path}:', r.status_code, r.json())

def update_task(url, path):
    try:
        r = requests.get(url)
        r.raise_for_status()
        pre_content = get_pre_content(r.text)
        sha = get_file_sha(path)
        update_github_file(pre_content, path, sha)
        print(f'{path} update successful!')
    except Exception as e:
        print(f'Error during update for {path}:', e)

@app.route('/')
def run_updates():
    for task in tasks:
        update_task(task['url'], task['path'])  # no threading
    return 'All 3 updates triggered (sequentially)!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
