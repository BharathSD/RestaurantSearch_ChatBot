from bs4 import BeautifulSoup
import requests
import re
from utils.soundex import get_soundex

class TierCities:
    def __init__(self):
        self.url="https://en.wikipedia.org/wiki/Classification_of_Indian_cities"
        self.tier_cities = None
        self. synonym_names = {}
        self.soundex_dict_tier = {}
        self.prepareValidCityList()
        self.find_synonym()

    def prepareValidCityList(self):
        r = requests.get(self.url,verify=False)
        soup = BeautifulSoup(r.text, "html.parser")

        tier_cities=list(map(lambda x:x.text.lower(),soup.find('table',class_='wikitable').find_all('a')))

        self.soundex_dict_tier={get_soundex(name):name for name in tier_cities}

    def find_synonym(self):
        url = 'https://www.scoopwhoop.com/news/whats-in-a-name/#.45rdcz1m2'
        r=requests.get(url,verify=False)
        containers=BeautifulSoup(r.text,'html.parser').find('div',class_='article-body').find_all('h2')

        for container in containers:
            if re.search(r'^[0-9]{1,2}.+', container.text.strip()):
                self.synonym_names[container.text.strip().split()[1].lower()] = container.text.strip().split()[-1].lower()

        self.soundex_dict_syn={get_soundex(key):self.synonym_names[key] for key in self.synonym_names}

    def validate_city(self, city_name):
        city_name = city_name.lower()
        loc_soundex=get_soundex(city_name)
        val=False
        if loc_soundex in self.soundex_dict_tier.keys():
            val=True
            city_name= self.soundex_dict_tier[loc_soundex]
        if loc_soundex in self.soundex_dict_syn.keys() and not val:
            val=True
            city_name= self.soundex_dict_syn[loc_soundex]

        return val, city_name



if __name__ == '__main__':
    I = TierCities()
    I.find_synonym()
