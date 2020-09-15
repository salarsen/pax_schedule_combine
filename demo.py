import requests, re, json, sys, os
from lxml import html
from bs4 import BeautifulSoup

if __name__ == "__main__":
    session_requests = requests.Session()
    result = session_requests.get('https://www.paxegx.com/')
    result.encoding = 'utf-8'
    demo_count = 0
    if result.status_code == 200:
        f = open('demos.csv','w+', encoding='utf-8')
        soup = BeautifulSoup(result.content, 'lxml')
        soups = soup.findAll(attrs={'class':'show-floor-hd-group'})
        # print(soups)
        for showfloor in soups:
            shows = showfloor.findAll('a')
            for show in shows:
                # print(show.get('href'),flush=True)
                sub_url = 'https://www.paxegx.com' + str(show.get('href'))
                print(sub_url,flush=True)
                sub_req = session_requests.get(sub_url)
                if sub_req.status_code == 200:
                    sub_soup = BeautifulSoup(sub_req.content,'lxml')
                    sub_soups = sub_soup.findAll('a',attrs={'class':'games-grid-item'})
                    if sub_soups:
                        for game in sub_soups:
                            print(game.find(attrs={'class':'details'}).h3.text,flush=True)
                            # print(game.get('href'))


                            get_game_pg_url = 'https://www.paxegx.com' + game.get('href')
                            get_game_pg = session_requests.get(get_game_pg_url)

                            if get_game_pg.status_code == 200:
                                game_soup = BeautifulSoup(get_game_pg.content, 'lxml')
                                game_soup_res = game_soup.find('span',text='Get the demo')
                                if game_soup_res:
                                    f.write(show.find(attrs={'class':'front'}).p.text)
                                    f.write(',')
                                    # print('game demo')
                                    f.write(game.find(attrs={'class':'details'}).h3.text)
                                    f.write(',')
                                    print (game_soup_res.parent.get('href'))
                                    f.write(game_soup_res.parent.get('href'))
                                    f.write('\n')
                                    demo_count = demo_count + 1

                            # game_url_suffix = soup.find('a',attrs={'class':'games-grid-items'})
                        # sys.exit()
                            # print(games.get('href'))
                            # print(games)
                # print()

            # print(thesoup)
            # f.write(thesoup)
            # name = thesoup.find(attrs={'class':'name'})
            # desc = thesoup.find(attrs={'class':'description'})

            # if name and desc:
            #     f.write(name.text.replace("\n","").replace("\r","") + " - " + desc.text.replace("\n","").replace("\r","") + "\n\n")
            #     # print(desc)
            # elif name and not desc:
            #     f.write(name.text.replace("\n","").replace("\r","") + "\n\n")
            #     # print(name.text.replace("\n","").replace("\r","") + "\n\n")
            # elif not name and desc:
            #     f.write(desc.text.replace("\n","").replace("\r","") + "\n\n")
            #     # print(desc.text.replace("\n","").replace("\r","") + "\n\n")
        print(demo_count)
        f.close()
            
            # print(thesoup.contents[1].text)
            # print(len(thesoup.contents))
            # if len(thesoup.contents) >= 3:
            #     print(thesoup.contents[3])
            # # name = thesoup.find('name')
            # print(name)