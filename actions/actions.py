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

class ActionValidateCity(Action):

    def __init__(self):
        self.TierCitiesI = TierCities()
        Action.__init__(self)

    def name(self) -> Text:
        return "action_validate_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        loc=tracker.get_slot('location')
        loc,val = InstanceManagerI.TierCitiesI.validate_city(loc)

        return [SlotSet('location',loc),SlotSet('is_location_valid',val)]

class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurant'

    def run(self, dispatcher, tracker, domain):
        cuisine = tracker.get_slot('cuisine')
        location = tracker.get_slot('location')
        price = tracker.get_slot('price')
        response = InstanceManagerI.RestaurantSearchI.getRestaurantDetails(location, cuisine, price)
        if response != 0:
            # get the data contents to display
            display_data = InstanceManagerI.RestaurantSearchI.getdisplayContent()
        else:
            display_data = "No Results found"

        dispatcher.utter_message(display_data)

        return [SlotSet('cuisine',cuisine), SlotSet('is_result_found',response!=0)]

class ActionSendMail(Action):

    def name(self):
        return "action_send_mail"

    def run(self, dispatcher, tracker, domain):
        retVal = InstanceManagerI.EmailI.sendMail(tracker.get_slot('emailId'),
                                                  tracker.get_slot("location").title(),
                                                  InstanceManagerI.RestaurantSearchI.getdisplayContent())

        if retVal is 0:
            dispatcher.utter_template("utter_email_Sent", tracker)
        else:
            dispatcher.utter_template("utter_email_error", tracker)
        return []

class ActionResetSlots(Action):
    def name(self):
        return 'action_perform_reset'

    def run(self, dispatcher, tracker, domain):
        #AllSlotsReset()
        return [AllSlotsReset()]

class ActionRestarted(Action):
    def name(self):
        return 'action_restarted'

    def run(self, dispatcher, tracker, domain):
        return[Restarted()]
