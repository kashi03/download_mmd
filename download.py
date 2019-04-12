import requests, json, time
from urllib.parse import urljoin
from tqdm import tqdm
from bs4 import BeautifulSoup

class DownloadMMD:
    def __init__(self, cookie=None):
        self.session = requests.session()
        self.session.headers = {'Cookie': cookie}
        self.base_url = 'https://3d.nicovideo.jp/'
        self.mmd_list = []

    def search_mmd(self, word='', pages=1, start_page=1 ,value=28):
        for page in range(start_page, pages+1):
            mmd_search_url = f'https://3d.nicovideo.jp/search?word={word}&page={page}&limit=28&word_type=tag&category=all&work_type=mmd&download_filter=all&sort=total&order=1&perfect_match=0&usable_animation='
            html = self.session.get(mmd_search_url)
            html = BeautifulSoup(html.text, 'lxml')
            mmd_links = [urljoin(self.base_url, i['href']) for i in html.find_all('a', class_='work-box-link')]
            
            prb = tqdm(total=len(mmd_links), unit_scale=True)
            for link in mmd_links:
                html = self.session.get(link)
                html = BeautifulSoup(html.text, 'lxml')
                mmd_info = {}
                mmd_info['file_name'] = html.find('dl', class_='horizontal').find('dd').text
                mmd_info['url'] = urljoin(self.base_url, html.find('a', id='js-download')['href'])
                mmd_info['authenticity_token'] = html.find('meta', attrs={'name':'csrf-token'})['content']
                self.mmd_list.append(mmd_info)
                prb.update(1)
            prb.close()

    def download(self):
        for info in self.mmd_list:
            params = {'authenticity_token':info['authenticity_token']}
            r = self.session.post(info['url'], stream=True, params=params)
            pbr = tqdm(total=int(r.headers['Content-Length']), unit_scale=True)
            with open(f'mmd/{info["file_name"]}', 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        pbr.update(len(chunk))
                pbr.close()
            time.sleep(0.3)

def main():
    cookie = ''
    with open('myconf.json', 'r') as f:
        j = json.load(f)
        cookie = j['cookie']

    session = requests.session()
    session.headers = {'Cookie': cookie}

    # html = session.get('https://3d.nicovideo.jp/works/td31639')
    mmd_search_url = 'https://3d.nicovideo.jp/search?page=1&limit=28&word_type=tag&category=all&work_type=mmd&download_filter=mmd&sort=total&order=1&perfect_match=0'
    html = session.get(mmd_search_url)
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

if __name__ == "__main__":
    cookie = ''
    with open('myconf.json', 'r') as f:
        j = json.load(f)
        cookie = j['cookie']
    mmd = DownloadMMD(cookie)
    mmd.search_mmd(word='艦これ',start_page=4, pages=3)
    mmd.download()