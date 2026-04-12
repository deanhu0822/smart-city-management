import ollama
from pydantic import BaseModel

# 1. Define your data structure
class UserProfile(BaseModel):
    name: str
    age: int
    interests: list[str]



# 2. Request structured output
response = ollama.chat(
    model='qwen3.5',
    messages=[{'role': 'user', 'content': 'Extract info: John is 25 and likes golf and coding.'}],
    # Passing the schema enforces the structure
    format=UserProfile.model_json_schema()
)

# 3. Use the data
user = UserProfile.model_validate_json(response.message.content)
print(f"Name: {user.name}, Interests: {', '.join(user.interests)}")