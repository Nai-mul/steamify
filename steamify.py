import sys
import json
import time
import hmac
import hashlib
import requests
from datetime import datetime
from colorama import init, Fore, Style
from urllib.parse import unquote
import cloudscraper

init(autoreset=True)


class Data:
    def __init__(self, init_data, userid, username, secret):
        self.init_data = init_data
        self.userid = userid
        self.username = username
        self.secret = secret


class PixelTod:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.DEFAULT_COUNTDOWN = (2 * 3600) + (5 * 60)  # Интервал между повтором скрипта, 6 часов 5 минут дефолт
        self.INTERVAL_DELAY = 3  # Интервал между каждым аккаунтом, 3 секунды дефолт
        self.base_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "Host": "api.app.steamify.io",
            "X-Requested-With": "org.telegram.messenger",
            'origin': 'https://app.steamify.io',
            'referer': 'https://app.steamify.io',
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        }



    def get_secret(self, userid):
        rawr = "adwawdasfajfklasjglrejnoierjboivrevioreboidwa"
        secret = hmac.new(rawr.encode("utf-8"), str(userid).encode("utf-8"), hashlib.sha256).hexdigest()
        return secret

    def data_parsing(self, data):
        return {key: value for key, value in (i.split('=') for i in unquote(data).split('&'))}

    def main(self):
        with open("data.txt", "r") as file:
            datas = file.read().splitlines()

        self.log(f'{Fore.LIGHTYELLOW_EX}Обнаружено аккаунтов: {len(datas)}')
        if not datas:
            self.log(f'{Fore.LIGHTYELLOW_EX}Пожалуйста, введите свои данные в initdata.txt')
            sys.exit()
        print('-' * 50)
        while True:
            for no, data in enumerate(datas):
                self.log(f'{Fore.LIGHTYELLOW_EX}Номер аккаунта: {Fore.LIGHTWHITE_EX}{no + 1}')
                data_parse = self.data_parsing(data)
                user = json.loads(data_parse['user'])
                userid = str(user['id'])
                first_name = user.get('first_name')
                last_name = user.get('last_name')
                username = user.get('username')

                self.log(f'{Fore.LIGHTYELLOW_EX}Аккаунт: {Fore.LIGHTWHITE_EX}{first_name} {last_name}')
                secret = self.get_secret(userid)
                new_data = Data(data, userid, username, secret)
                self.process_account(new_data)
                print('-' * 50)
                self.countdown(self.INTERVAL_DELAY)
            self.countdown(self.DEFAULT_COUNTDOWN)

    def process_account(self, data):
        self.get_me(data)
        self.claim_farming(data)
        self.start_farming(data)
        self.get_friend(data)
        self.solve_task(data)
        self.checkin(data)
        self.solve_multiplier(data)
        self.sparks(data)
        #self.claim_ticket(data)

    def countdown(self, t):
        while t:
            one, two = divmod(t, 3600)
            three, four = divmod(two, 60)
            print(f"{Fore.LIGHTWHITE_EX}Ожидание до {one:02}:{three:02}:{four:02} ", flush=True, end="\r")
            t -= 1
            time.sleep(1)
        print("                          ", flush=True, end="\r")

    def api_call(self, url, data=None, headers=None, method='GET'):
        while True:
            try:
                if method == 'GET':
                    res = self.scraper.get(url, headers=headers)
                elif method == 'POST':
                    res = self.scraper.post(url, headers=headers, data=data)
                else:
                    raise ValueError(f'Не поддерживаемый метод: {method}')

                if res.status_code == 401:
                    self.log(f'{Fore.LIGHTRED_EX}{res.text}')

                open('.http.log', 'a', encoding='utf-8').write(f'{res.text}\n')
                return res
            except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
                self.log(f'{Fore.LIGHTRED_EX}Ошибка подключения соединения!')
                continue
            except requests.exceptions.JSONDecodeError:
                self.log(f'{Fore.LIGHTRED_EX}Ошибка чтения ответа')

    def get_me(self, data: Data):
        url = 'https://api.app.steamify.io/api/v1/user/me'
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.init_data}"
        res = self.api_call(url, headers=headers)

        if not res.text:
            self.log(f'{Fore.LIGHTRED_EX}Пустой ответ от API get_me.')
            return

        try:
            response_json = res.json()
            #self.log(f'{response_json}')
            balance = response_json.get('data', {}).get('points', 'N/A')
            self.log(f'{Fore.LIGHTYELLOW_EX}Общий баланс: {Fore.LIGHTWHITE_EX}{balance}')
            ref = response_json.get('data', {}).get('inviter')
            if ref == 'None':
                url_ref = 'https://api.app.steamify.io/api/v1/user/set-inviter'
                headers = self.base_headers.copy()
                headers["Authorization"] = f"Bearer {data.init_data}"
                payload = {'invite_code': "WsHOpV"}
                res = self.api_call(url_ref, headers=headers, json=payload)

        except json.JSONDecodeError:
            self.log(f'{Fore.LIGHTRED_EX}Не удалось декодировать JSON-ответ от API get_me. Ответ: {res.text}')

    def claim_farming(self, data: Data):
        url = "https://api.app.steamify.io/api/v1/farm/claim"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.init_data}"
        res = self.api_call(url, headers=headers)
        try:
            response_json = res.json()
            #self.log(f'{response_json}')
            farm = response_json.get('msg')
            balance = response_json.get('data', {}).get('points')
            if farm == 'claim is not available':
                if balance == 0:
                    self.log(f"{Fore.LIGHTRED_EX}Первый запуск клейма")
                else:
                    self.log(f"{Fore.LIGHTRED_EX}Еще не пришло время клейма")
            else:
                balance = response_json.get('data', {}).get('claim', {}).get('total_rewards')
                self.log(f"{Fore.LIGHTYELLOW_EX}Забрал с фарминга: {Fore.LIGHTWHITE_EX}{balance}")
            return

        except requests.exceptions.JSONDecodeError:
            self.log(f'{Fore.LIGHTRED_EX}Ошибка чтения ответа')

    def sparks(self, data: Data):
        url = "https://api.app.steamify.io/api/v1/game/case/inventory/claim"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.init_data}"
        res = self.api_call(url, headers=headers)
        try:
            response_json = res.json()
            self.log(f'{response_json}')
            farm = response_json.get('msg')
            if farm == 'too early to claim':
                self.log(f"{Fore.LIGHTRED_EX}Еще не пришло время клейма sparks")
            else:
                balance = response_json.get('data', {}).get('claimed_sparks', {})
                self.log(f"{Fore.LIGHTYELLOW_EX}Забрал sparks: {Fore.LIGHTWHITE_EX}{balance}")
            return
        except requests.exceptions.JSONDecodeError:
            self.log(f'{Fore.LIGHTRED_EX}Ошибка чтения ответа')
    def start_farming(self, data: Data):
        url = "https://api.app.steamify.io/api/v1/farm/start"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.init_data}"
        res = self.api_call(url, headers=headers)
        try:
            response_json = res.json()
            #self.log(f'{response_json}')
            farm_s = response_json.get('msg')
            if farm_s == 'farm already in progress':
                self.log(f"{Fore.LIGHTRED_EX}Фарминг уже запущен")
            else:
                self.log(f"{Fore.LIGHTYELLOW_EX}Запустил фарминг")
            return
        except requests.exceptions.JSONDecodeError:
            self.log(f'{Fore.LIGHTRED_EX}Ошибка чтения ответа')

    def get_friend(self, data: Data):
        url = "https://api.app.steamify.io/api/v1/user/invite"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.init_data}"
        res = self.api_call(url, headers=headers)
        try:
            response_json = res.json()
            #self.log(f'{response_json}')
            can_claim = response_json.get('data', {}).get('available_claim', 0)
            if can_claim > 0:
                url_claim = "https://api.app.steamify.io/api/v1/user/invite/claim"
                res = self.api_call(url_claim, headers=headers)
                response_json = res.json()
                #self.log(f'{response_json}')
                ref = response_json.get('data', {}).get('claimed_rewards', 'N/A')
                self.log(f"{Fore.LIGHTYELLOW_EX}Забрал реферальный бонус: {Fore.LIGHTWHITE_EX}{ref}")
            else:
                self.log(f"{Fore.LIGHTRED_EX}Нечего забирать с реферального бонуса")
            return
        except requests.exceptions.JSONDecodeError:
            self.log(f'{Fore.LIGHTRED_EX}Ошибка чтения ответа')

    def solve_task(self, data: Data):
        while True:
            url_task = "https://api.app.steamify.io/api/v1/user/task/list"
            headers = self.base_headers.copy()
            headers["Authorization"] = f"Bearer {data.init_data}"
            res = self.api_call(url_task, headers=headers)
            try:
                response_json = res.json()
                # self.log(f'{response_json}')

                tasks = response_json.get('data', {}).get('tasks', [])
                task_started = False

                for task in tasks:
                    task_id = task["id"]
                    task_title = task["name"]
                    task_status = task["user_state"]["status"]

                    if task_status == "available":
                        url_start = f"https://api.app.steamify.io/api/v1/user/task/{task_id}/start"
                        self.api_call(url_start, headers=headers)
                        task_started = True
                        break

                    elif task_status == "completed":
                        url_claim = f"https://api.app.steamify.io/api/v1/user/task/{task_id}/claim"
                        res = self.api_call(url_claim, headers=headers)
                        response_json = res.json()

                        if response_json.get("data") and response_json["data"]["user_state"]:
                            claim_status = response_json["data"]["user_state"]["status"]
                            if claim_status == "claimed":
                                self.log(f"{Fore.LIGHTYELLOW_EX}Выполнил задание {task_title}!")
                                continue

                if not task_started:
                    break
            except requests.exceptions.JSONDecodeError:
                self.log(f'{Fore.LIGHTRED_EX}Ошибка чтения ответа')

    def checkin(self, data:Data):
        url = "https://api.app.steamify.io/api/v1/user/daily/claim"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.init_data}"
        res = self.api_call(url, headers=headers)
        try:
            response_json = res.json()
            check = response_json.get('msg', [])
            if check == 'already claimed':
                self.log(f"{Fore.LIGHTRED_EX}Уже делал чекин сегодня")
                return

            if res.status_code == 200 or res.status_code == 201:
                self.log(f"{Fore.LIGHTYELLOW_EX}Сделал чекин")
                return
            return
        except requests.exceptions.JSONDecodeError:
            self.log(f'{Fore.LIGHTRED_EX}Ошибка чтения ответа')

    def solve_multiplier(self, data: Data):
        url_mult = "https://api.app.steamify.io/api/v1/user/multiplier/list"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.init_data}"
        res = self.api_call(url_mult, headers=headers)
        try:
            response_json = res.json()
            #self.log(f'{response_json}')
            mult = response_json.get('data', {}).get('multipliers', [])
            for multipliers in mult:
                mult_id = multipliers["id"]
                mult_title = multipliers["name"]
                mult_status = multipliers["status"]

                if mult_status == "available":

                    url_mult_claim = f"https://api.app.steamify.io/api/v1/user/multiplier/{mult_id}/claim"
                    res = self.api_call(url_mult_claim, headers=headers)
                    response_json = res.json()

                    if response_json.get("data"):
                        claim_status = response_json["data"].get("status")
                        if claim_status == "active":
                            self.log(f"{Fore.LIGHTYELLOW_EX}Забрал буст {mult_title}!")
                            continue
        except requests.exceptions.JSONDecodeError:
            self.log(f'{Fore.LIGHTRED_EX}Ошибка чтения ответа')

    def claim_ticket(self, data: Data):
        url = "https://api.app.steamify.io/api/v1/user/task/video"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.init_data}"

        res = self.api_call(url, headers=headers)
        try:
            response_json = res.json()
            #print(f'{response_json}')

            if response_json.get('success') and response_json.get('data'):
                watched = response_json['data'].get('watched', 0)
                max_tasks = response_json['data'].get('max', 0)
                num_claims = max_tasks - watched
                if num_claims > 1:
                    self.log(f'{Fore.LIGHTYELLOW_EX}Начал сбор билетов: {Fore.LIGHTWHITE_EX}{num_claims} {Fore.LIGHTRED_EX}Жди {num_claims*3} секунд ')

                    successful_claims = 0

                    for _ in range(num_claims):
                        url_claim = "https://api.app.steamify.io/api/v1/user/task/video/claim"
                        payload = {
                            "X-reCAPTCHA-Resp": 1
                        }

                        res_claim = self.api_call(url_claim, headers=headers, data=json.dumps(payload), method='POST')
                        response_claim_json = res_claim.json()
                        print(f'Claim response: {response_claim_json}')

                        if response_claim_json.get('success'):
                           successful_claims += 1
                        else:
                           self.log(f"{Fore.LIGHTRED_EX}Ошибка при выполнении запроса на клейм")

                        time.sleep(3)

                    self.log(f'{Fore.LIGHTYELLOW_EX}Забрал билетов: {Fore.LIGHTWHITE_EX}{successful_claims}')
                else:
                    return
        except requests.exceptions.JSONDecodeError:
            self.log(f'{Fore.LIGHTRED_EX}Ошибка чтения ответа')
    def log(self, message):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{Fore.LIGHTBLACK_EX}[{now}]{Style.RESET_ALL} {message}")



if __name__ == "__main__":
    try:
        app = PixelTod()
        app.main()
    except KeyboardInterrupt:
        sys.exit()
