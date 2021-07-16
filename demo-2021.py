import requests, json

url = "https://api-melupufoagt.stackpathdns.com/api/space_orders?specials=1&key=b0a264a7-7b5e-4a55-acde-16cb630bfe6d&category=4689&search_term="

res = requests.get(url)
if res.status_code == 200:
    data = json.loads(res.content)

    game_list = []
    for exhibitor in data["space_orders"]:
        # print(exhibitor["company"])

        if "specials" in exhibitor:
            for game in exhibitor["specials"]:
                # if "steampowered" in game["link"] and game["price"] is None and game["title"] not in game_list:
                if game["price"] is None and game["title"] not in game_list:
                    print(f"{exhibitor['company']} -- {game['title']} - {game['link']}")
                    game_list.append(game["title"])
