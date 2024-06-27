import requests
import json
import re
import sqlalchemy as db
import pandas as pd


BASE_URL = "https://www.bungie.net/Platform/Destiny2/"#Manifest/DestinyInventoryItemDefinition/4017959782/"
MASTER_DF = pd.DataFrame()

stats_ids = {
#stats
      3555269338: 'Zoom', 
      4284893193: 'Rounds_Per_Minute',
      4043523819: 'Impact'  ,
      1240592695:'Reload_Speed',
      155624089: 'Stability',  
      3871231066: 'Magazine',  
      4188031367: 'Range',
      943549884:  'Handling', 
      1345609583: 'Aim_Assistance', 
      2715839340: 'Recoil' 
}

guns = {
#Kings Fall
    'Doom of Chelchis'   : 1937552980,
    'Qullims Terminus'   : 1321506184,
    'Smite of Merain'    : 2221264583,
    'Defiance of Yasmin' : 3228096719,
    'Midhas Reckoning'   : 3969066556,
    'Zaoulis Bane'       : 431721920,

#Crotas End
    'Song of Ir Yût'  : 2828278545,
    'Fang of Ir Yût'  : 1432682459,
    'Abyss Defiant'   : 833898322,
    'Swordbreaker'    : 3163900678,
    'Oversoul Edict'  : 1098171824,
    'Word of Crota'   : 120706239
}


def get_item_info(id):
  payload = {}
  headers = {'X-API-Key': 'ecc0e5e526e44bbbb89b0e77dc399a1c'}
  return requests.get(BASE_URL + f"Manifest/DestinyInventoryItemDefinition/{str(id)}/", 
                      headers=headers, 
                      data=payload
                      )


def create_row(item_info):
  
  weapon_info = item_info.json()['Response']

  #obtain name, type, and tier for current weapon
  name = weapon_info['displayProperties']['name']
  item_type = weapon_info['itemTypeDisplayName']
  tier = weapon_info['inventory']['tierTypeName']
  
  # obtaining dictionary with neccesary data and making a copy
  stats_json = weapon_info['stats']['stats']
  stats_copy = stats_json.copy()
  keys = list(stats_copy.keys())

  # adding name, type, and tier
  stats_copy['name'] = name
  stats_copy['type'] = item_type
  stats_copy['tier'] = tier

  #print(json.dumps(stats_copy, indent=3))

  # keys for stats are displayed as numbers
  # here we convert keys from numbers to words, and remove uneccesary keys
  for key in keys:
    string_header = stats_ids.get(int(key))
    if string_header:
      stats_copy[string_header] = stats_copy[key]['value']
    del stats_copy[key]
  
  # returns a dictionary with the desired info
  return stats_copy


#loggg = 3
def add_row(weapon_stats_dic):
  #loggg += 4
  #print(loggg)   
  global MASTER_DF
  MASTER_DF = pd.concat([pd.DataFrame.from_dict([weapon_stats_dic]), MASTER_DF], ignore_index=True)
 
ex = 431721920
ex2 = 1937552980
ex_info = get_item_info(ex)
ex2_info = get_item_info(ex2)
ex_row = create_row(ex_info)
ex2_row = create_row(ex2_info)


add_row(ex_row)
add_row(ex2_row)
mlb = MASTER_DF


engine = db.create_engine('sqlite:///mlb.db')
mlb.to_sql('trymlb', con=engine, if_exists='replace', index=False)

with engine.connect() as connection:
    query_result = connection.execute(db.text("SELECT * FROM trymlb;")).fetchall()
    pp = pd.DataFrame(query_result)
    pp.set_index('name', inplace=True)
    pp.insert(0, "----------", '-----------')
    print(pp.transpose())

