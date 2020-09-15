import requests, re, json
from lxml import html
from bs4 import BeautifulSoup

if __name__ == "__main__":
    session_requests = requests.Session()
    result = session_requests.get('https://www.paxegx.com/')
    result.encoding = 'utf-8'
    if result.status_code == 200:
        f = open('test.txt','w+', encoding='utf-8')
        soup = BeautifulSoup(result.content, 'lxml')
        soups = soup.findAll(attrs={'class':'back'})
        # print(soups)
        for thesoup in soups:
            # print(thesoup)
            # f.write(thesoup)
            name = thesoup.find(attrs={'class':'name'})
            desc = thesoup.find(attrs={'class':'description'})

            if name and desc:
                f.write(name.text.replace("\n","").replace("\r","") + " - " + desc.text.replace("\n","").replace("\r","") + "\n\n")
                # print(desc)
            elif name and not desc:
                f.write(name.text.replace("\n","").replace("\r","") + "\n\n")
                # print(name.text.replace("\n","").replace("\r","") + "\n\n")
            elif not name and desc:
                f.write(desc.text.replace("\n","").replace("\r","") + "\n\n")
                # print(desc.text.replace("\n","").replace("\r","") + "\n\n")

        f.close()
            
            # print(thesoup.contents[1].text)
            # print(len(thesoup.contents))
            # if len(thesoup.contents) >= 3:
            #     print(thesoup.contents[3])
            # # name = thesoup.find('name')
            # print(name)