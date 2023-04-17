import pandas as pd
import datetime as dt
import requests
from typing import List, Tuple


FILE_NAME = 'Clicker.xlsx'


def get_clan_data(name: str) -> List[Tuple[str, str]]:
    link = 'https://guilds.clickerheroes.com/clans/findGuild.php'
    data = {
        'uid': '0',
        'passwordHash': '0',
        'highestZoneReached': '0',
        'guildName': name
    }

    response = requests.post(link, params=data).json()

    if not response.get('success', False):
        raise RuntimeError('ERROR: Invalid clan name:', name)

    result = []

    for member in response['result']['guildMembers'].values():
        result.append((member['nickname'], member['highestZone']))

    return result


today = dt.datetime.today().strftime("%m-%d-%Y")

df = pd.read_excel(FILE_NAME, index_col=0, sheet_name='Data',
                   usecols=['Date', 'Name', 'Categories', 'Image', 'Zones'])


clans = df['Categories'].dropna().unique()
for clan in clans:
    print('Getting data for', clan)
    data = get_clan_data(clan)

    for (user, zone) in data:
        filter = (df['Name'] == user) & \
            (df['Categories'] == clan) & \
            (df.index == today)

        if len(df.loc[filter]) == 0:
            print(
                f'{user:>15} {"(" + zone + ")":<9} does not have a row for {today}')
            continue

        df.loc[
            filter,
            'Zones'
        ] = float(zone)

    print()

# Saving data
with pd.ExcelWriter(FILE_NAME, if_sheet_exists='replace', mode='a') as writer:
    df.to_excel(writer, sheet_name='Data', index=True)