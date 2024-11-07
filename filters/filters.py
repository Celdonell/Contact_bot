from aiogram.filters import BaseFilter
from aiogram.types import Message

class EntityFilter(BaseFilter):  # [1]
    def __init__(self, entity_types: list[str]): # [2]
        self.entity_types = entity_types
        
    async def __call__(self, message: Message) -> bool:  # [3]
        entities = message.entities or []
        detected = []
        for item in entities:
            if item.type in self.entity_types:
                detected.append(item.type)
        if isinstance(self.entity_types, list):
            return detected == self.entity_types
        