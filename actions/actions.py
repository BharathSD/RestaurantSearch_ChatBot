# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, Restarted
from utils.extractTierCities import TierCities
from utils.eMail import Email
from utils.RestaurantSearch import RestaurantSearch

class InstanceManager:
    def __init__(self):
        self.TierCitiesI = TierCities()
        self.RestaurantSearchI =RestaurantSearch()
        self.EmailI = Email()

InstanceManagerI = InstanceManager()

class ActionValidateLocation(Action):

    def __init__(self):
        self.TierCitiesI = TierCities()
        Action.__init__(self)

    def name(self) -> Text:
        return "action_location_valid"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        loc=tracker.get_slot('location')
        location_validity = "valid"

        if not loc:
            location_validity = "invalid"
        else:
            val, loc = InstanceManagerI.TierCitiesI.validate_city(loc)
            if not val:
                location_validity = "invalid"

        return [SlotSet("location_validity", location_validity), SlotSet("location", loc)]

class ActionValidateCuisine(Action):
    def name(self):
        return "action_cuisine_valid"

    def run(self, dispatcher, tracker, domain):

        cuisine = tracker.get_slot("cuisine")
        cuisine_validity = "valid"

        if not cuisine:
            cuisine_validity = "invalid"
        else:
            val, cuisine = InstanceManagerI.RestaurantSearchI.validate_cuisine(cuisine)
            if not val:
                cuisine_validity = "invalid"

        return [SlotSet("cuisine_validity", cuisine_validity), SlotSet("cuisine", cuisine)]


class ActionRestarted(Action):
    def name(self):
        return 'action_restart'

    def run(self, dispatcher, tracker, domain):
        return[AllSlotsReset(), Restarted()]

class ActionSendMail(Action):

    def name(self):
        return "action_send_mail"

    def run(self, dispatcher, tracker, domain):
        InstanceManagerI.EmailI.sendMail(tracker.get_slot('email'),
                                         tracker.get_slot("location").title(),
                                         tracker.get_slot("cuisine"),
                                         InstanceManagerI.RestaurantSearchI.getdisplayContent())

        return []

class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_restaurant'

    def run(self, dispatcher, tracker, domain):
        cuisine = tracker.get_slot('cuisine')
        location = tracker.get_slot('location')
        budget = tracker.get_slot('budget')
        response = InstanceManagerI.RestaurantSearchI.getRestaurantDetails(location, cuisine, budget)
        if response:
            # get the data contents to display
            display_data = InstanceManagerI.RestaurantSearchI.getdisplayContent()
            search_validity = "valid"
        else:
            display_data = "No Results found"
            search_validity = "invalid"

        dispatcher.utter_message(display_data)

        return [SlotSet("search_validity", search_validity)]
