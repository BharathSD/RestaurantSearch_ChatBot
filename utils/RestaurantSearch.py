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
        self.supported_cuisines_dict={'american':1, 'chinese':25,
                            'mexican':73,'italian':55,'north indian':50,
                            'south indian':85}
        self.soundex_dct={get_soundex(value):value for value in self.supported_cuisines_dict.keys()}
        self.df = None

    def validate_cuisine(self, cuisine):
        rettVal = False
        val = get_soundex(cuisine)
        if val in self.soundex_dct.keys():
            rettVal = True
            cuisine = self.soundex_dct[val]
        return rettVal, cuisine


    def priceMapper(self, price):
        return "> 700"

    def getRestaurantDetails(self, location, cuisine, budget):

        retVal = True

        if not location:
            retVal = False
        else:
            # retrieve location details
            response = self.zomato.get_location(location)
            location_details = {}
            if response is not None:
                response_json = json.loads(response)
                if response_json["status"] == "success":
                    # fetch location details and store 'city_id'
                    location_details = response_json["location_suggestions"][0]
                    city_id = location_details["city_id"]
                    city_name = location_details["city_name"]
                    # Validate if the location details is of the requested location
                    if location.lower() == city_name.lower():
                        response_cuisine = self.zomato.get_cuisines(city_id)

                        # filter only supported cuisines
                        filtered_cuisine = {
                            key:value
                            for key,value in response_cuisine.items()
                            if self.validate_cuisine(value)[0]
                        }

                        if cuisine is not None:
                            cuisine_list = [ value for key, value in filtered_cuisine.items()
                                if str(value).lower() == cuisine.lower()]
                        else:
                            cuisine_list = [ value for key, value in filtered_cuisine.items()]

                        restaurants_found = self.search_restaurant( location, location_details, cuisine_list)

                        if len(restaurants_found) > 0:
                            restaurant_filtered_budget = self.filter_restaurant_by_budget(budget, restaurants_found)
                            # sort the data by ratings
                            self.df = pd.DataFrame(restaurant_filtered_budget,
                                                   columns=['Restaurant Name', 'Address', 'avg_cost2', 'Rating'])

                            self.df.sort_values(by=['Rating'], ascending=False, inplace=True, ignore_index=True)
                        else:
                            retVal = False
                    else:
                        retVal = False
                else:
                    retVal = False
            else:
                retVal = False

        return retVal

    def search_restaurant( self, location="", location_details={}, cuisine_list=[] ) -> list:
        restaurants_found = []

        for startIdx in range(0,200,20):
                results=self.zomato.restaurant_search(location, location_details["latitude"],
                                                      location_details["longitude"],
                                                      ",".join(cuisine_list) ,20, startIdx)
                d = json.loads(results)
                if d['results_found'] > 0:
                    for restaurant in d['restaurants']:
                        restaurants_found.append((restaurant['restaurant']['name'],restaurant['restaurant']['location']['address'],
                                 float(restaurant['restaurant']['average_cost_for_two']),
                                 float(restaurant['restaurant']['user_rating']['aggregate_rating'])))
                else:
                    break

        return restaurants_found

    def filter_restaurant_by_budget(self, budget, restaurant_list) -> list:
        filtered_restaurant_list = []
        # Set the budget range based on input
        rangeMin = 0
        rangeMax = 999999

        if budget == "299":
            rangeMax = 299
        elif budget == "700":
            rangeMin = 300
            rangeMax = 700
        elif budget == "701":
            rangeMin = 701
        else:
            """
                Default budget
            """
            rangeMin = 0
            rangeMax = 9999

        for restaurant in restaurant_list:
            avg_cost = int(restaurant[2])

            if avg_cost >= rangeMin and avg_cost <= rangeMax:
                filtered_restaurant_list.append(restaurant)

        return filtered_restaurant_list


    def getdisplayContent(self):
        data_format = '{}. Restaurant Name: {}\n Restaurant locality address: {}\n Average budget for two people: {}\n Zomato user rating: {}\n\n'
        final_str = ""
        try:
            for i in range(min(len(self.df), 10)):
                data = self.df.loc[i]
                final_str += data_format.format(i+1, data['Restaurant Name'], data['Address'], data['avg_cost2'], data['Rating'])
        except:
            pass
        return final_str



if __name__ == '__main__':
    location = "mumbai"
    resSearchI = RestaurantSearch()
    resSearchI.getRestaurantDetails('bengaluru', 'chinese', '700')
    print(resSearchI.getdisplayContent())
