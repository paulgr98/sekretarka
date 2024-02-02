from enum import Enum

from components.openai_models import ChatGPT4Free


class GptRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message:
    def __init__(self, content, role=GptRole.USER):
        self.content: str = content
        self.role: str = role.value

    def __str__(self):
        return f"{self.role}: {self.content}"

    def __repr__(self):
        return f"{self.role}: {self.content}"

    def __eq__(self, other):
        return self.role == other.role and self.content == other.content

    def __ne__(self, other):
        return self.role != other.role or self.content != other.content

    def __hash__(self):
        return hash((self.role, self.content))

    def __len__(self):
        return len(self.content)

    def __dict__(self):
        return {"role": self.role, "content": self.content}

    def to_dict(self):
        return {"role": self.role, "content": self.content}


class ChatHistory:
    def __init__(self, max_history=50):
        self.history = {}
        self.max_history = max_history

    def add(self, user_id, message: Message):
        if user_id not in self.history:
            self.history[user_id] = []
            self.history[user_id].append(ChatGPT4Free.system_message)
        self.history[user_id].append(message.to_dict())
        if len(self.history[user_id]) > self.max_history:
            self.history[user_id].pop(0)

    def get(self, user_id):
        if user_id not in self.history:
            return None
        return self.history[user_id]

    def clear(self, user_id):
        if user_id in self.history:
            self.history.pop(user_id)

    def clear_all(self):
        self.history = {}


def main():
    chat_history = ChatHistory()
    user_id = "123"
    chat_history.add(user_id, Message("Hello"))
    chat_history.add(user_id, Message("Hello! How are you?", GptRole.ASSISTANT))
    chat_history.add(user_id, Message("I'm fine, thank you!"))
    chat_history.add(user_id, Message("That's great!", GptRole.ASSISTANT))
    chat_history.add(user_id, Message("Bye!"))
    chat_history.add(user_id, Message("Goodbye!", GptRole.ASSISTANT))

    print(chat_history.get(user_id))


if __name__ == '__main__':
    main()
