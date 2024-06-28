import requests
import json
import re
import sqlalchemy as db
import pandas as pd


# Manifest/DestinyInventoryItemDefinition/4017959782/
BASE_URL = "https://www.bungie.net/Platform/Destiny2/"
MASTER_DF = pd.DataFrame()


stats_ids = {
    # Gun stats with their associated IDS
    3555269338: 'Zoom',
    4284893193: 'Rounds_Per_Minute',
    4043523819: 'Impact',
    1240592695: 'Reload_Speed',
    155624089: 'Stability',
    3871231066: 'Magazine',
    4188031367: 'Range',
    943549884:  'Handling',
    1345609583: 'Aim_Assistance',
    2715839340: 'Recoil'
}

guns = {

    # Recommended guns with their associated IDS
    # Kings Fall Raid Weapons
    'Doom of Chelchis': 1937552980,
    'Qullims Terminus': 1321506184,
    'Smite of Merain': 2221264583,
    'Defiance of Yasmin': 3228096719,
    'Midhas Reckoning': 3969066556,
    'Zaoulis Bane': 431721920,

    # Crotas End Raid Weapons
    'Song of Ir Yût': 2828278545,
    'Fang of Ir Yût': 1432682459,
    'Abyss Defiant': 833898322,
    'Swordbreaker': 3163900678,
    'Oversoul Edict': 1098171824,
    'Word of Crota': 120706239
}


def get_item_info(id):
    payload = {}
    headers = {'X-API-Key': 'ecc0e5e526e44bbbb89b0e77dc399a1c'}
    request = requests.get(
        BASE_URL + f"Manifest/DestinyInventoryItemDefinition/{str(id)}/",
        headers=headers, data=payload
    )
    # Returns json with only the weapon stats (large dataset)
    return request.json()


def create_row(item_json):
    weapon_info = item_json['Response']

    # obtain name, type, and tier for current weapon
    name = weapon_info['displayProperties']['name']
    item_type = weapon_info['itemTypeDisplayName']
    tier = weapon_info['inventory']['tierTypeName']

    # obtaining dictionary with neccesary data and making a copy
    stats_json = weapon_info['stats']['stats']
    stats_copy = stats_json.copy()
    keys = list(stats_copy.keys())

    # adding name, type, and tier
    stats_copy['Name'] = name
    stats_copy['Type'] = item_type
    stats_copy['Tier'] = tier

    # print(json.dumps(stats_copy, indent=3))

    # keys for stats are displayed as numbers
    # here we convert keys from numbers to words, and remove uneccesary keys
    for key in keys:
        string_header = stats_ids.get(int(key))
        if string_header:
            stats_copy[string_header] = stats_copy[key]['value']
        del stats_copy[key]

    # returns a dictionary with the desired info
    return stats_copy


# adds a row to the MASTER_DF for the specified weapon
def add_row(weapon_stats_dic):
    global MASTER_DF
    MASTER_DF = pd.concat(
        [pd.DataFrame.from_dict([weapon_stats_dic]), MASTER_DF],
        ignore_index=True
    )
# SORTING FUNCTIONALITY
def sorting_functionality():
    # ask if the user wants to sort the table
    print("would you like to sort the table?")
    choice = -1

    while True:
        print('1) Yes')
        print('2) No')
        choice = input('> ')
        if choice not in ['1', '2']:
            print('Please enter either 1 or 2')
        else:
            print()
            break

    # if the user does not want to sort the table, return None
    if choice == '2':
        return None
    
    # if the user does want to sort, proceed
    # create a list of possible stats the user can sort by 
    stats = list(stats_ids.values()) + ['Name', 'Type', 'Tier']
    retval = ''

    # user will specify what stat they want to sort by
    print("please select the stat you would like to sort by")
    print("(note: names are case sensitive)")

    while True:
        retval = input('>')
        if retval not in stats:
            print('please type a stat listed in the table')
        else:
            break

    return retval

# ############################################# #
# #USE THIS PART TO GENERATE TABLE IN TERMINAL# #
# ############################################# #

# function that prints the intro for the user
def print_choices(d):
    print('\nEnter a #1-12 to choose a gun, "d" once done or "q" to quit:  ')
    for index, value in enumerate(d):
        print(f'{index + 1}) {value}')


# THE VALUES THAT WORK AND CAN BE INPUTTED
values = list(guns.keys())  # <- VALUES TRANSLATED
correct_input = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']


# Function gets the choice from the user and
# saves it as a value for the main function
def get_choice():
    while True:
        the_choice = input('> ')
        if the_choice == 'q':
            return 'q'
        # If the user is done inputting choices they select d to compare
        elif the_choice == 'd':
            return 'd'
        elif the_choice in correct_input:
            return int(the_choice) - 1
        else:
            # Makes sure input is between 1-12 and nothing else
            print('Error. Enter a number 1-12, "d" when done or "q" to quit: ')


# List of all choices used
max_choices = []

# Makes sure that there is a max of 12 choices
while len(max_choices) < 12:
    print_choices(values)
    print('Please pick your gun')
    choice = get_choice()
    if choice == 'q':
        print('Thanks for looking')
        break
    if choice == 'd':
        break
    if choice not in max_choices:
        max_choices.append(choice)
    else:
        # Does not allow repeated choices
        print('You have already choosen this option. Try again')

# Goes through the choices and puts them into rows
# with their proper data displayed, unless q was called
if choice != 'q':
    for index in max_choices:
        ex = values[index]
        ex_id = guns[ex]
        ex_info = get_item_info(ex_id)
        ex_row = create_row(ex_info)
        add_row(ex_row)

    def convert_master_df():
        engine = db.create_engine('sqlite:///weapon_info.db')
        MASTER_DF.to_sql('info_displayed', con=engine, if_exists='replace', index=False)

        with engine.connect() as connection:
            query_result = connection.execute(
                db.text("SELECT * FROM info_displayed;")).fetchall()
            display_pd = pd.DataFrame(query_result)

            # Set the index for each row as the name for the gun
            display_pd.set_index('Name', inplace=True)

            # Add a column with just lines to make the graph look nicer
            display_pd.insert(0, "----------", '-----------')

        # Rotate graph 90 degrees so columns
        # and rows are switched, and print to terminal
        print()
        print(display_pd.transpose())
        print()

        sort_by = sorting_functionality()
        if sort_by:
            display_pd.sort_values(by=[sort_by], ascending=False, inplace=True)
            print()
            print(display_pd.transpose())
            print()
    convert_master_df()
