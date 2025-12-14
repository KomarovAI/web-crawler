import asyncio,os,sqlite3,time,hashlib,mimetypes
from urllib.parse import urljoin,urlparse
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()
class FullDB:
    def __init__(self,f='archive.db'):
        self.f=f
        self.init_db()
    def init_db(self):
        c=sqlite3.connect(self.f)
        c.execute('''CREATE TABLE IF NOT EXISTS assets
        (id INTEGER PRIMARY KEY,url TEXT UNIQUE,data BLOB,type TEXT,ts REAL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS pages
        (id INTEGER PRIMARY KEY,url TEXT UNIQUE,html TEXT,local_path TEXT,ts REAL)''')
        c.commit()
        c.close()
    def save_asset(self,url,data,type):
        try:
            c=sqlite3.connect(self.f)
            c.execute('INSERT OR REPLACE INTO assets(url,data,type,ts)VALUES(?,?,?,?)',
            (url,data,type,time.time()))
            c.commit()
            c.close()
            return True
        except:return False
    def save_page(self,url,html,path):
        try:
            c=sqlite3.connect(self.f)
            c.execute('INSERT OR REPLACE INTO pages(url,html,local_path,ts)VALUES(?,?,?,?)',
            (url,html,path,time.time()))
            c.commit()
            c.close()
            return True
        except:return False
    def get_asset(self,url)->bytes|None:
        c=sqlite3.connect(self.f)
        r=c.execute('SELECT data FROM assets WHERE url=?',(url,)).fetchone()
        c.close()
        return r[0]if r else None
class FullCrawler:
    def __init__(self,u,m=50,t=10,out='site_archive'):
        self.u=u
        self.m=m
        self.t=t
        self.v=set()
        self.q=[u]
        self.d=urlparse(u).netloc
        self.out=Path(out)
        self.out.mkdir(exist_ok=True)
        self.db=FullDB(str(self.out/'archive.db'))
        self.file_map={}
    def _ok(self,url)->bool:
        return url not in self.v and len(self.v)<self.m and urlparse(url).netloc==self.d and url.startswith(('http://','https://'))
    def _make_local_path(self,url)->str:
        p=urlparse(url).path or '/'
        if p=='/':
            p='/index.html'
        if not p.endswith(('.html','.htm')):
            if not Path(p).suffix:
                p+='/index.html'
        return str(self.out/p.lstrip('/'))
    async def fetch_asset(self,s,url)->bytes|None:
        try:
            async with s.get(url,timeout=self.t,ssl=False)as r:
                if r.status==200:
                    data=await r.read()
                    ct=r.headers.get('content-type','application/octet-stream')
                    self.db.save_asset(url,data,ct)
                    return data
        except:pass
        return None
    async def fetch_html(self,s,url)->str|None:
        try:
            async with s.get(url,timeout=self.t,ssl=False)as r:
                if r.status==200 and 'text/html'in r.headers.get('content-type',''):
                    return await r.text()
        except:pass
        return None
    async def download_assets(self,s,html,base_url):
        soup=BeautifulSoup(html,'html.parser')
        tasks=[]
        for tag,attr in[('img','src'),('script','src'),('link','href'),('source','src')]:
            for el in soup.find_all(tag):
                src=el.get(attr)
                if src:
                    asset_url=urljoin(base_url,src)
                    if self._ok(asset_url)or urlparse(asset_url).netloc==self.d:
                        tasks.append(self._download_single(s,asset_url))
        if tasks:
            await asyncio.gather(*tasks)
    async def _download_single(self,s,url):
        if url not in self.file_map:
            data=await self.fetch_asset(s,url)
            if data:
                ext=Path(urlparse(url).path).suffix or '.bin'
                fname=hashlib.md5(url.encode()).hexdigest()+ext
                fpath=self.out/'assets'/fname
                fpath.parent.mkdir(exist_ok=True)
                fpath.write_bytes(data)
                self.file_map[url]=f"assets/{fname}"
    def _rewrite_html(self,html,base_url)->str:
        soup=BeautifulSoup(html,'html.parser')
        for tag,attr in[('img','src'),('script','src'),('link','href'),('source','src'),('a','href')]:
            for el in soup.find_all(tag):
                href=el.get(attr)
                if href:
                    abs_url=urljoin(base_url,href)
                    if abs_url in self.file_map:
                        el[attr]=self.file_map[abs_url]
                    elif self._ok(abs_url):
                        local=self._make_local_path(abs_url)
                        el[attr]=os.path.relpath(local,Path(self._make_local_path(base_url)).parent)
        return str(soup)
    async def run(self)->dict:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=5,ssl=False))as s:
            while self.q and len(self.v)<self.m:
                url=self.q.pop(0)
                if url in self.v:continue
                self.v.add(url)
                print(f"[{len(self.v)}/{self.m}]{url}")
                html=await self.fetch_html(s,url)
                if html:
                    await self.download_assets(s,html,url)
                    html_rewritten=self._rewrite_html(html,url)
                    fpath=self._make_local_path(url)
                    Path(fpath).parent.mkdir(parents=True,exist_ok=True)
                    Path(fpath).write_text(html_rewritten)
                    self.db.save_page(url,html_rewritten,fpath)
                    soup=BeautifulSoup(html,'html.parser')
                    for a in soup.find_all('a',href=True):
                        link_url=urljoin(url,a['href'])
                        if self._ok(link_url):
                            self.q.append(link_url)
                await asyncio.sleep(.1)
        return{"total":len(self.v),"output":str(self.out)}
async def main():
    url=os.getenv('START_URL','https://example.com')
    m=int(os.getenv('MAX_PAGES',10))
    out=os.getenv('OUTPUT_DIR','site_archive')
    crawler=FullCrawler(url,m,out_dir=out)
    r=await crawler.run()
    print(f"\n✅ {r['total']} pages downloaded")
    print(f📁 Archive: {r['output']}")
    print(f🔗 Open: {r['output']}/index.html")
if __name__=='__main__':asyncio.run(main())
