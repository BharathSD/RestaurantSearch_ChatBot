import configparser
import os
from actions import zomatopy
import json
from actions.soundex import get_soundex


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

    def getRestaurantDetails(self, location, cuisine, price):
        try:
            location_detail= self.zomato.get_location(location, 1)

            if get_soundex(cuisine) in self.soundex_dct.keys():
                cuisine= self.soundex_dct[get_soundex(cuisine)]

            d1 = json.loads(location_detail)
            lat=d1["location_suggestions"][0]["latitude"]
            lon=d1["location_suggestions"][0]["longitude"]

            results=self.zomato.restaurant_search("", lat, lon, str(self.cuisines_dict.get(cuisine)),20)
            d = json.loads(results)
            print(d)
        except:
            pass


if __name__ == '__main__':
    resSearchI = RestaurantSearch()
    resSearchI.getRestaurantDetails('Bengaluru', 'italian', '')
