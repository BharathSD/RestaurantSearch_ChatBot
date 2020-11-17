# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, Restarted
from actions.extractTierCities import TierCities
from actions.eMail import Email


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
        loc,val = self.TierCitiesI.validate_city(loc)

        return [SlotSet('location',loc),SlotSet('is_location_valid',val)]

class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurant'

    def run(self, dispatcher, tracker, domain):
        cuisine = tracker.get_slot('cuisine')
        response="no results"

        # todo: the logic of searching restaurants goes here
        return [SlotSet('cuisine',cuisine),SlotSet('is_result_found',response!="no results")]

class ActionSendMail(Action):

    def name(self):
        return "action_send_mail"

    def run(self, dispatcher, tracker, domain):
        EmailI = Email('Body.txt', tracker.get_slot("location").title())
        retVal = EmailI.sendMail(tracker.get_slot('emailId'))

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
