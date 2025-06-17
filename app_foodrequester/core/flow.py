from ..nlp.extractor import extract_structured_data

class FlowManager:
    def __init__(self, flow_name: str, context: str, expected_fields: list[str]):
        self.flow_name = flow_name
        self.context = context
        self.expected_fields = expected_fields

    def process_message(self, user_message: str, user_number:str) -> dict:
        return extract_structured_data(user_message, self.expected_fields, self.context, user_number)