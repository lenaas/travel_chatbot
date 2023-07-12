# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk.events import AllSlotsReset
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import os
from dotenv import load_dotenv
import openai 



class ActionGetDestinations(Action):

    def name(self) -> Text:
        return "action_get_destinations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        openAI = tracker.get_slot("use_GPT")
        slots = [f'question_{i}' for i in range(1, 6)]
        slot_values = [tracker.get_slot(i) for i in slots]
        if openAI=="Yes":
            load_dotenv()
            openai.api_key = os.getenv('OPENAI_API_KEY')
            assert openai.api_key!=None, "API_KEY is not set"
            output = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user",
                    "content":
                            f"""Imagine you are a Travel Agent. \n
                            I will list you some criteria and you should give me the top 5 travel destinations based on the criteria as a bulletpoint list.\n
                            1. Budget: {slot_values[0]}\n
                            2. Activity Level: {slot_values[1]}\n
                            3. Climate and Weather: {slot_values[2]}\n
                            4. Interests: {slot_values[3]}\n
                            5. Travel Duration: {slot_values[4]}\n
                            """
                    }])
            dispatcher.utter_message(text="I consulted ChatGPT and it recommends the following destinations: \n"+str(output["choices"][0]["message"]["content"]))
        else:
            dispatcher.utter_message(text="I consulted my database and i can recommend you the following destinations: \n"+str(slot_values))

        
        return []
class Reset_Slots(Action):
    def name(self) -> Text:
        return "action_reset_slots"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        return [AllSlotsReset()]
