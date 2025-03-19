import requests


def get(client_id, client_secret):
    global token
    load = open('Osubot/token.txt', 'r')
    token = load.read()
    token = token.strip() 
    url = "https://osu.ppy.sh/api/v2/me"
    headers = {
            "Authorization": f"Bearer {token}"
        }
    load.close()
    response = requests.get(url, headers=headers)
    data = response.json()

    if data == {'authentication': 'basic'}:
        token_url = "https://osu.ppy.sh/oauth/token"

        # 建立請求資料
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": "public"
        }
        # 發送 POST 請求取得 token
        response = requests.post(token_url, data=data)
        token_info = response.json()

        # 拿到 access token
        access_token = token_info.get("access_token")
        save = open('Osubot/token.txt', 'w')
        print(access_token, file=save)
        save.close()
        return access_token
    else:
        return token
