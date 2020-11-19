import configparser
import os
from utils import zomatopy
import json
from utils.soundex import get_soundex
import pandas as pd


class RestaurantSearch:
    def __init__(self):
        cfg = configparser.ConfigParser()
        cfgPath = os.path.dirname(__file__)
        cfgFileName = os.path.join(cfgPath, 'config.ini')
        cfg.read(cfgFileName)

        config={ "user_key":cfg['zomato']['user_key']}
        self.zomato = zomatopy.initialize_app(config)
        self.cuisines_dict={'american':1,'chinese':25,
                            'mexican':73,'italian':55,'north indian':50,
                            'south indian':85}
        self.soundex_dct={get_soundex(value):value for value in self.cuisines_dict.keys()}
        self.df = None

    def priceMapper(self, price):
        return "> 700"

    def getRestaurantDetails(self, location, cuisine, price):
        location_detail= self.zomato.get_location(location, 1)

        if get_soundex(cuisine) in self.soundex_dct.keys():
            cuisine= self.soundex_dct[get_soundex(cuisine)]

        d1 = json.loads(location_detail)
        lat=d1["location_suggestions"][0]["latitude"]
        lon=d1["location_suggestions"][0]["longitude"]

        data_lst = []
        for startIdx in range(0,200,20):
            results=self.zomato.restaurant_search("", lat, lon, str(self.cuisines_dict.get(cuisine)),20, startIdx)
            d = json.loads(results)
            if d['results_found'] == 0:
                raise Exception('Results not found')


            for restaurant in d['restaurants']:
                data_lst.append((restaurant['restaurant']['name'],restaurant['restaurant']['location']['address'],
                                 float(restaurant['restaurant']['average_cost_for_two']),
                                 float(restaurant['restaurant']['user_rating']['aggregate_rating'])))

        # sort the data by ratings
        self.df = pd.DataFrame(data_lst, columns=['Restaurant Name', 'Address', 'avg_cost2', 'Rating'])

        prc = self.priceMapper(price)

        if prc == "< 300":
            self.df = self.df[self.df['avg_cost2'] < 300]
        elif prc == "300 to 700":
            self.df = self.df[(self.df['avg_cost2'] >= 300) & (self.df['avg_cost2'] <= 700)]
        elif prc == "> 700":
            self.df = self.df[self.df['avg_cost2'] > 700]

        self.df = self.df.sort_values(by=['Rating'], ascending=False)
        total_filtered_data = len(self.df)

        self.df.to_csv('restaurantSearch.csv')

        return total_filtered_data

    def getdisplayContent(self):
        data_format = '{}. Restaurant Name: {}\n Restaurant locality address: {}\n Average budget for two people: {}\n Zomato user rating: {}\n\n'
        final_str = ""
        for i in range(min(len(self.df), 10)):
            data = self.df.loc[i]
            final_str += data_format.format(i+1, data['Restaurant Name'], data['Address'], data['avg_cost2'], data['Rating'])
        return final_str



if __name__ == '__main__':
    resSearchI = RestaurantSearch()
    resSearchI.getRestaurantDetails('bengaluru', 'italian', '')
    print(resSearchI.getdisplayContent())
