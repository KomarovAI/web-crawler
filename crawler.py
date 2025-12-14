import asyncio,os
from urllib.parse import urljoin,urlparse
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()
class Crawler:
    def __init__(self,u,m=50,t=10):
        self.u=u
        self.m=m
        self.t=t
        self.v=set()
        self.q=[u]
        self.d=urlparse(u).netloc
    def _ok(self,url)->bool:
        return url not in self.v and len(self.v)<self.m and urlparse(url).netloc==self.d and url.startswith(('http://','https://'))
    async def fetch(self,s,url)->str|None:
        try:
            async with s.get(url,timeout=self.t,ssl=False)as r:
                return await r.text()if r.status==200 else None
        except:return None
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
        return{"total":len(self.v),"urls":sorted(self.v)}
async def main():
    r=await Crawler(os.getenv('START_URL','https://example.com'),int(os.getenv('MAX_PAGES',50))).run()
    print(f"\n✅ {r['total']} pages")
if __name__=='__main__':asyncio.run(main())
