import jellyfish as jf
import pandas as pd
import requests
import json


def getStates():
    url = "https://www.whizapi.com/api/v2/util/ui/in/indian-states-list"
    querystring = {"project-app-key": "sd6u15esx571r9kndndlib17"}
    headers = {
                'cache-control' : "no-cache",
                    'postman-token': "d23e64b1-f1c7-2459-eb6e-d77e4b2d20ff"
                        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    states = json.loads(response.text)
    states_df = pd.DataFrame(states['Data'])
    return states_df


def getCities(id):
    url = "https://www.whizapi.com/api/v2/util/ui/in/indian-city-by-state"
    querystring = {"stateid": str(id), "project-app-key": "sd6u15esx571r9kndndlib17"}
    headers = {
                'cache-control': "no-cache",
                    'postman-token': "3cd07f0b-425f-f021-68c6-ae5cc2d698d6"
                        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    resp = json.loads(response.text)
    cities_df = pd.DataFrame(resp['Data'])
    return cities_df

if __name__ == "__main__":
    states = getStates()
    # print states
    states.to_csv("states.csv")
    state_id_list = list(states['ID'])
    cities_list = []
    i = 1
    for sid in state_id_list:
        print "Processing state id - {}. {} of {} ".format(sid, i, len(state_id_list))
        df_tmp = getCities(sid)
        df_tmp['SID'] = pd.Series(sid, index=df_tmp.index)
        print df_tmp
        cities_list.append(df_tmp)

    cities_all = pd.concat(cities_list, ignore_index=True)
    # print cities_all
    cities_all.to_csv("cities_all.csv")