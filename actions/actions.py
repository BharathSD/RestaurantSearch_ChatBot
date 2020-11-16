# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_core.events import SlotSet
from actions.extractTierCities import TierCities


class ActionHelloWorld(Action):

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
