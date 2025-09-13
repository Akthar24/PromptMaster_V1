class UserMessage:
    def __init__(self, text: str):
        self.text = text

class LlmChat:
    def __init__(self, api_key=None, session_id=None, system_message=None):
        self.api_key = api_key
        self.session_id = session_id
        self.system_message = system_message
        self.model_name = None

    def with_model(self, provider: str, model: str):
        self.model_name = f"{provider}/{model}"
        return self

    async def send_message(self, user_message: UserMessage):
        # Fake response just for local dev
        return f"[MOCKED OPTIMIZED PROMPT]\nOriginal: {user_message.text}\n"
