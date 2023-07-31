from typing import Text, List, Any, Dict

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet

import logging
logger = logging.getLogger(__name__)

# def clean_name(name):
#     return "".join([c for c in name if c.isalpha()])


SLOTS = [('first_name', 'first name'),
         ('last_name', 'last name')]

class AskForFirstName(Action):
    def name(self) -> Text:
        return "action_ask_first_name"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(text="What is your first name?")
        return []


class AskForLastName(Action):
    def name(self) -> Text:
        return "action_ask_last_name"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(text="What is your last name?")
        return []

class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_name_form"
     
    async def run(
            self,
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[EventType]:

        # restore the form state from slots
        self.form_state = tracker.slots.get('form_state', {})
        if self.form_state is None:
            self.form_state = {}
        if 'asking_slots' not in self.form_state:
            self.asked_last_name = False
            self.asked_first_name= False
            self.count = 0
        # original form implementation for the run()
        events = await super(ValidateNameForm, self).run(dispatcher, tracker, domain)
        events = events + [SlotSet(key='form_state', value=self.form_state)]
        # persist the stats into slots
        logger.info('.....save form_state back to slot: {}'.format(self.form_state))    

        return events
    
    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        logger.info('inside required_slots')
        if 'asking_slots' not in self.form_state:
            # User just enters the form, return the default required slots
            logger.info('................user just entering the form')

            ask_slot = next_slot_to_ask(self.form_state)
            self.form_state['asking_slots'] = [ask_slot]
            if ask_slot is None:
                return []
            else:
                return [ask_slot]

        elif self.form_state.get('asking_slots') is None:
            # In the form state, it has all the required information and
            # validation method determine it's time to get out
            return []

        elif self.form_state.get('asking_slots') and self.asked_first_name and not self.asked_last_name and self.count !=2:
            return ['first_name']
        
        elif self.form_state.get('asking_slots') and self.asked_first_name and not self.asked_last_name and self.count ==2:
            return ['last_name']

        elif self.form_state.get('asking_slots'):
            # The from stats has slot names in 'asking_slots' field
            # if the the first one is an empty slot, continue ask user
            # otherwise, end the form
            slots_check = self.form_state['asking_slots']
            logger.info('checking slot {}'.format(slots_check))
            empty_ones = list(filter(lambda s: tracker.get_slot(s) is None, slots_check))
            if len(empty_ones) == 0:
                self.form_state['asking_slots'] = []
                logger.info('End the form!!!!')
                return []
            else:
                return self.form_state['asking_slots']
        else:
            return []


    def extract_first_name(
                self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
        ) -> Dict[Text, Any]:
        logger.info('inside extract_first_name')

        first_name = tracker.latest_message.get("text")

        logger.info('extracted first name {}'.format(first_name))
        if not self.asked_first_name:
            # self.form_state['asking_slots']=['first_ name']
            self.asked_first_name = True
            return {"first_name": None}

        return {"first_name": first_name}

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        logger.info('inside validate_first_name')
        """Validate `first_name` value."""
        self.count = self.count + 1
        return {"first_name": slot_value}

    def extract_last_name(
                self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
        ) -> Dict[Text, Any]:

        logger.info('inside extract_last_name')

        last_name = tracker.latest_message.get("text")

        logger.info('extracted last name {}'.format(last_name))
        return {"last_name": last_name}

    def validate_last_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""
        logger.info('inside validate_last_name')
        self.count =+ 1

        return {"last_name": slot_value}

def next_slot_to_ask(form_state):
    for s in SLOTS:
        if not form_state.get(s[0]):
            return s[0]
    return None
