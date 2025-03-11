import requests
import urllib3
import json
from base64 import b64encode
from time import sleep
import os
import sys
import psutil
from colorama import Fore, Back, Style
import threading  # Import threading
import keyboard  # Thư viện để lắng nghe phím

def find_game_directory():
    possible_executables = [
        'RiotClientServices.exe',
        'LeagueClient.exe',
        'LeagueClientUxRender.exe'
    ]

    for process in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if process.info['name'] in possible_executables:
                exe_path = process.info['exe']
                if exe_path:
                    return os.path.dirname(exe_path)
        except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
            continue

    return None

gamedir = find_game_directory()

if gamedir is None:
    print('Không tìm thấy đường dẫn trò chơi. Vui lòng đảm bảo rằng trò chơi đang chạy.')
    sys.exit(1)

championLock = True
championsPrio = [35]  # ID của Shaco

stopWhenMatchStarts = False

champions = {
    "1": "Annie",
    "2": "Olaf",
    "3": "Galio",
    "4": "Twisted Fate",
    "5": "Xin Zhao",
    "6": "Urgot",
    "7": "LeBlanc",
    "8": "Vladimir",
    "9": "Fiddlesticks",
    "10": "Kayle",
    "11": "Master Yi",
    "12": "Alistar",
    "13": "Ryze",
    "14": "Sion",
    "15": "Sivir",
    "16": "Soraka",
    "17": "Teemo",
    "18": "Tristana",
    "19": "Warwick",
    "20": "Nunu",
    "21": "Miss Fortune",
    "22": "Ashe",
    "23": "Tryndamere",
    "24": "Jax",
    "25": "Morgana",
    "26": "Zilean",
    "27": "Singed",
    "28": "Evelynn",
    "29": "Twitch",
    "30": "Karthus",
    "31": "Cho'Gath",
    "32": "Amumu",
    "33": "Rammus",
    "34": "Anivia",
    "35": "Shaco",
    "36": "Dr. Mundo",
    "37": "Sona",
    "38": "Kassadin",
    "39": "Irelia",
    "40": "Janna",
    "41": "Gangplank",
    "42": "Corki",
    "43": "Karma",
    "44": "Taric",
    "45": "Veigar",
    "48": "Trundle",
    "50": "Swain",
    "51": "Caitlyn",
    "53": "Blitzcrank",
    "54": "Malphite",
    "55": "Katarina",
    "56": "Nocturne",
    "57": "Maokai",
    "58": "Renekton",
    "59": "Jarvan IV",
    "60": "Elise",
    "61": "Orianna",
    "62": "Wukong",
    "63": "Brand",
    "64": "Lee Sin",
    "67": "Vayne",
    "68": "Rumble",
    "69": "Cassiopeia",
    "72": "Skarner",
    "74": "Heimerdinger",
    "75": "Nasus",
    "76": "Nidalee",
    "77": "Udyr",
    "78": "Poppy",
    "79": "Gragas",
    "80": "Pantheon",
    "81": "Ezreal",
    "82": "Mordekaiser",
    "83": "Yorick",
    "84": "Akali",
    "85": "Kennen",
    "86": "Garen",
    "89": "Leona",
    "90": "Malzahar",
    "91": "Talon",
    "92": "Riven",
    "96": "Kog'Maw",
    "98": "Shen",
    "99": "Lux",
    "101": "Xerath",
    "102": "Shyvana",
    "103": "Ahri",
    "104": "Graves",
    "105": "Fizz",
    "106": "Volibear",
    "107": "Rengar",
    "110": "Varus",
    "111": "Nautilus",
    "112": "Viktor",
    "113": "Sejuani",
    "114": "Fiora",
    "115": "Ziggs",
    "117": "Lulu",
    "119": "Draven",
    "120": "Hecarim",
    "121": "Kha'Zix",
    "122": "Darius",
    "126": "Jayce",
    "127": "Lissandra",
    "131": "Diana",
    "133": "Quinn",
    "134": "Syndra",
    "136": "Aurelion Sol",
    "141": "Kayn",
    "142": "Zoe",
    "143": "Zyra",
    "145": "Kai'Sa",
    "150": "Gnar",
    "154": "Zac",
    "157": "Yasuo",
    "161": "Vel'Koz",
    "163": "Taliyah",
    "164": "Camille",
    "201": "Braum",
    "202": "Jhin",
    "203": "Kindred",
    "222": "Jinx",
    "223": "Tahm Kench",
    "236": "Lucian",
    "238": "Zed",
    "240": "Kled",
    "234": "Viego",
    "245": "Ekko",
    "254": "Vi",
    "266": "Aatrox",
    "267": "Nami",
    "268": "Azir",
    "412": "Thresh",
    "420": "Illaoi",
    "421": "Rek'Sai",
    "427": "Ivern",
    "429": "Kalista",
    "432": "Bard",
    "497": "Rakan",
    "498": "Xayah",
    "516": "Ornn",
    "555": "Pyke"
}

championNames = {name: id for id, name in champions.items()}
championIds = [int(id) for id in champions.keys()]

for argv in reversed(sys.argv[1:]):
    for champion in champions:
        if champions[champion] == argv:
            championsPrio.insert(0, int(champion))
            break

priostr = []
for champion in championsPrio:
    if champion not in championIds:
        print(Back.RED + Fore.WHITE + 'Invalid champion ID', champion, Style.RESET_ALL)
        exit()
    priostr.append('%s (%d)' % (champions[str(champion)], champion))

print('Pick priority: %s ..' % (', '.join(priostr)))

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def request(method, path, query='', data=''):
    if not query:
        url = '%s://%s:%s%s' % (protocol, host, port, path)
    else:
        url = '%s://%s:%s%s?%s' % (protocol, host, port, path, query)

    print('%s %s %s' % (method.upper().ljust(7, ' '), url, data))

    fn = getattr(s, method)

    if not data:
        r = fn(url, verify=False, headers=headers)
    else:
        r = fn(url, verify=False, headers=headers, json=data)

    return r

lockfile = None
print('Waiting for League of Legends to start ..')

while not lockfile:
    lockpath = os.path.join(gamedir, 'lockfile')

    if os.path.isfile(lockpath):
        print('Found running League of Legends, dir', gamedir)
        lockfile = open(lockpath, 'r')
    else:
        sleep(1)

lockdata = lockfile.read()
lockfile.close()

lock = lockdata.split(':')

procname = lock[0]
pid = lock[1]
port = lock[2]
password = lock[3]
protocol = lock[4]

host = '127.0.0.1'
username = 'riot'

userpass = b64encode(bytes(f'{username}:{password}', 'utf-8')).decode('ascii')
headers = {'Authorization': f'Basic {userpass}'}
print(headers['Authorization'])

s = requests.session()

while True:
    sleep(1)
    r = request('get', '/lol-login/v1/session')

    if r.status_code != 200:
        print(r.status_code)
        continue

    if r.json()['state'] == 'SUCCEEDED':
        break
    else:
        print(r.json()['state'])

summonerId = r.json()['summonerId']

championsOwned = []
championsOwnedIds = []
while not championsOwned:
    sleep(1)
    r = request('get', '/lol-champions/v1/owned-champions-minimal')

    if r.status_code != 200:
        continue

    championsOwned = r.json()

for champion in championsOwned:
    if champion['active']:
        championsOwnedIds.append(champion['id'])

prios = [championId for championId in championsPrio if championId in championsOwnedIds]
championsPrio = prios

picks = [champions[str(championId)] for championId in championsPrio]
pickstr = ' or '.join(picks)

if championLock:
    print('Will try to pick', pickstr, '..')
else:
    print('Will try to lock-in', pickstr, '..')

championIdx = 0

# Tạo sự kiện dừng
stop_event = threading.Event()

def listen_for_exit():
    keyboard.wait('ctrl+c')  # Chờ cho đến khi nhấn Ctrl + C
    stop_event.set()  # Đặt cờ dừng

# Khởi động luồng lắng nghe cho Ctrl + C
exit_thread = threading.Thread(target=listen_for_exit)
exit_thread.start()

setPriority = False

while True:
    if stop_event.is_set():  # Kiểm tra cờ dừng
        print("Đang dừng chương trình...")
        break

    if championIdx >= len(championsPrio):
        championIdx = 0

    r = request('get', '/lol-gameflow/v1/gameflow-phase')

    if r.status_code != 200:
        print(Back.BLACK + Fore.RED + str(r.status_code) + Style.RESET_ALL, r.text)
        continue
    print(Back.BLACK + Fore.GREEN + str(r.status_code) + Style.RESET_ALL, r.text)

    phase = r.json()

    if championIdx != 0 and phase != 'ChampSelect':
        championIdx = 0

    if phase == 'ReadyCheck':
        r = request('post', '/lol-matchmaking/v1/ready-check/accept')
        sleep(5)

    elif phase == 'ChampSelect':
        r = request('get', '/lol-champ-select/v1/session')
        if r.status_code != 200:
            continue

        cs = r.json()
        actorCellId = next((member['cellId'] for member in cs['myTeam'] if member['summonerId'] == summonerId), -1)

        if actorCellId == -1:
            continue

        for action in cs['actions'][0]:
            if action['actorCellId'] != actorCellId:
                continue

            if action['championId'] == 0:
                championId = championsPrio[championIdx]
                championIdx += 1

                url = f'/lol-champ-select/v1/session/actions/{action["id"]}'
                data = {'championId': championId}

                championName = champions[str(championId)]
                print('Picking', championName, '(%d)' % championId, '..')

                r = request('patch', url, '', data)
                print(r.status_code, r.text)

                if championLock and not action['completed']:
                    r = request('post', url + '/complete', '', data)
                    print(r.status_code, r.text)

    elif phase == 'InProgress':
        if not setPriority:
            for p in psutil.process_iter():
                name, exe, cmdline = '', '', []
                try:
                    name = p.name()
                    cmdline = p.cmdline()
                    exe = p.exe()
                    if p.name() == 'League of Legends.exe' or os.path.basename(p.exe()) == 'League of Legends.exe':
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                        print('Set high process priority!')
                        break
                except (psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                except psutil.NoSuchProcess:
                    continue
            setPriority = True

        if stopWhenMatchStarts:
            break
        else:
            sleep(9)

    elif phase in ['Matchmaking', 'Lobby', 'None']:
        setPriority = False

    sleep(1)

# Khi kết thúc, đợi cho luồng thoát
exit_thread.join()  # Chờ luồng thoát
