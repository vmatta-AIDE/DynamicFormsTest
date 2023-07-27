from typing import Text, List, Any, Dict

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import EventType, SlotSet

import logging
logger = logging.getLogger(__name__)

# def clean_name(name):
#     return "".join([c for c in name if c.isalpha()])

class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_name_form"
     
    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        additional_slots = ["first_name", "last_name"]

        logger.info('inside required_slots')
        return additional_slots

    async def extract_first_name(
                self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
        ) -> Dict[Text, Any]:
        logger.info('inside extract_first_name')

        first_name = tracker.latest_message.get("text")

        logger.info('extracted first name {}'.format(first_name))
        return {"first_ame": first_name}

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        # If the name is super short, it might be wrong.
        return {"first_name": slot_value}

    async def extract_last_name(
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

    
        return {"last_name": slot_value}
