import asyncio,os,sqlite3,time,hashlib
from urllib.parse import urljoin,urlparse
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()
class DB:
    def __init__(self,f='crawled.db'):
        self.f=f
        self.init_db()
    def init_db(self):
        c=sqlite3.connect(self.f)
        c.execute('''CREATE TABLE IF NOT EXISTS pages
        (id INTEGER PRIMARY KEY,url TEXT UNIQUE,html TEXT,hash TEXT,ts REAL)''')
        c.commit()
        c.close()
    def save(self,url,html):
        try:
            h=hashlib.md5(html.encode()).hexdigest()
            c=sqlite3.connect(self.f)
            c.execute('INSERT INTO pages(url,html,hash,ts)VALUES(?,?,?,?)',
            (url,html,h,time.time()))
            c.commit()
            c.close()
            return True
        except:return False
    def exists(self,url)->bool:
        c=sqlite3.connect(self.f)
        r=c.execute('SELECT 1 FROM pages WHERE url=?',(url,)).fetchone()
        c.close()
        return r is not None
    def get(self,url)->str|None:
        c=sqlite3.connect(self.f)
        r=c.execute('SELECT html FROM pages WHERE url=?',(url,)).fetchone()
        c.close()
        return r[0]if r else None
    def count(self)->int:
        c=sqlite3.connect(self.f)
        n=c.execute('SELECT COUNT(*)FROM pages').fetchone()[0]
        c.close()
        return n
class Crawler:
    def __init__(self,u,m=50,t=10,db_f='crawled.db',use_db=True):
        self.u=u
        self.m=m
        self.t=t
        self.v=set()
        self.q=[u]
        self.d=urlparse(u).netloc
        self.db=DB(db_f)if use_db else None
    def _ok(self,url)->bool:
        return url not in self.v and len(self.v)<self.m and urlparse(url).netloc==self.d and url.startswith(('http://','https://'))
    async def fetch(self,s,url)->str|None:
        if self.db and self.db.exists(url):
            h=self.db.get(url)
            print(f"[CACHE] {url}")
            return h
        try:
            async with s.get(url,timeout=self.t,ssl=False)as r:
                if r.status==200:
                    h=await r.text()
                    if self.db:self.db.save(url,h)
                    return h
        except:pass
        return None
    async def parse(self,h,b)->list:
        return[urljoin(b,a.get('href'))for a in BeautifulSoup(h,'html.parser').find_all('a',href=True)if self._ok(urljoin(b,a.get('href')))]
    async def run(self)->dict:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=5,ssl=False))as s:
            while self.q and len(self.v)<self.m:
                url=self.q.pop(0)
                if url in self.v:continue
                self.v.add(url)
                print(f"[{len(self.v)}/{self.m}]{url}")
                if h:=await self.fetch(s,url):self.q.extend(await self.parse(h,url))
                await asyncio.sleep(.1)
        return{"total":len(self.v),"urls":sorted(self.v),"db_pages":self.db.count()if self.db else 0}
async def main():
    use_db=os.getenv('USE_DB','true').lower()=='true'
    r=await Crawler(os.getenv('START_URL','https://example.com'),int(os.getenv('MAX_PAGES',50)),db_f=os.getenv('DB_FILE','crawled.db'),use_db=use_db).run()
    print(f"\n✅ {r['total']} pages")
    if use_db:print(f"💾 {r['db_pages']} pages in DB")
if __name__=='__main__':asyncio.run(main())
