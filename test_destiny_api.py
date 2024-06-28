import unittest
import destiny_api
from destiny_api import *
import mock # pip install this
from unittest.mock import patch, Mock
import builtins

class TestDestiny_project(unittest.TestCase):

    @patch('requests.get') 
    def test_get_data(self, mock_get): 
        """ 
        Test that get_data() returns the correct data  
        demonstrating the use of the mock library 
        """
  
        mock_response = Mock() 
        response_dict = {'name': 'John', 'email': 'john@example.com'}
        mock_response.json.return_value = response_dict
  
        mock_get.return_value = mock_response
        #mock_get.return_value.status_code = 200

        apiCall = get_item_info(111)
        mock_get.assert_called_with("https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/111/", data={}, 
                                    headers = {'X-API-Key': 'ecc0e5e526e44bbbb89b0e77dc399a1c'})
        self.assertEqual(apiCall, response_dict)

    def test_create_row(self):
        test_dict = {
                'Response':{
                'inventory': {
                    'tierTypeName': 'legendary'
                },
                'unwantedInfo1': 3,
                'displayProperties': {
                    'name': 'grace'
                },
                'itemTypeDisplayName': 'scout rifle',
                'stats': {
                    'unwantedInfo2': 'f',
                    'stats': {
                        '3555269338': {'value':8}, 
                        '4284893193': {'value':93, 'unantedData3':'4'},
                        '4043523819': {'value':0},
                        '111111111': {'value':9}, # this is unwanted data
                        '1240592695': {'value':4},
                        '155624089': {'value':5},  
                        '3871231066': {'value':2},  
                        '4188031367': {'value':3},
                        '943549884':  {'value':4, 'unwantedData4':4}, 
                        '1345609583': {'value':5}, 
                        '2715839340': {'value':6} 
                    }
                },
                'unwantedInfo5': 'l'
            }
        }

        correctResult = {
            'Name': 'grace',
            'Type': 'scout rifle',
            'Tier': 'legendary',
            'Zoom': 8, 
            'Rounds_Per_Minute': 93,
            'Impact': 0,
            'Reload_Speed': 4,
            'Stability': 5,  
            'Magazine': 2,  
            'Range': 3,
            'Handling':  4, 
            'Aim_Assistance': 5, 
            'Recoil': 6 
        }

        self.assertEqual(create_row(test_dict), correctResult)
    

    #self.assertEqual(expected_result, mock_table_data.method_calls[0][1])

    #@patch('destiny_api.MASTER_DF')
    def test_add_row(self):#, mock_masterdf):
        add_row({
            "name": "bloke",
            "number": 5,
            "rank": 4
            }
        )
        add_row({
            "name": "ryan",
            "number": 15,
            "rank": 0
            }
        )
        #print(mock_masterdf.method_calls[0][1])
        data = {'name': ['ryan', 'bloke'],
                'number': [15, 5],
                'rank': [0, 4]
                }

        df = pd.DataFrame(data)
        self.assertTrue(df.equals(destiny_api.MASTER_DF))


    def test_get_choice(self):
        
        with mock.patch.object(builtins, 'input', lambda _: 'd'):
            assert get_choice() == 'd'
        with mock.patch.object(builtins, 'input', lambda _: '1'):
            assert get_choice() == 0
        with mock.patch.object(builtins, 'input', lambda _: '13'):
            assert get_choice() == 'Error. Enter a number 1-12, "d" when done or "q" to quit: '
    


