import requests, json
from tqdm import tqdm
from bs4 import BeautifulSoup

cookie = ''
with open('myconf.json', 'r') as f:
    j = json.load(f)
    cookie = j['cookie']

session = requests.session()
session.headers = {'Cookie': cookie}

html = session.get('https://3d.nicovideo.jp/works/td31639')
html = BeautifulSoup(html.text, 'lxml')
authenticity_token = html.find('meta', attrs={'name':'csrf-token'})['content']

url = 'https://3d.nicovideo.jp/downloads/6098/session'
params = {'authenticity_token':authenticity_token}
r = session.post(url, stream=True, params=params)
progress_bar = tqdm(total=int(r.headers['Content-Length']), unit_scale=True)
with open('mmd/a.zip', 'wb') as f:
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)
            f.flush()
            progress_bar.update(len(chunk))
    progress_bar.close()