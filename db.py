import json

user_data = {}
with open("db.json", "r") as f:
    user_data = json.load(f)

class User:
  def __init__(self, id: int, language: str="de"):
    self.id = id
    self.language = language
  
  def create_user(self):
    new_data = {
      "reminders": {

      },
      "language": self.language
    }
  
    with open("db.json", "w") as f:
      user_data[self.id] = new_data
      json.dump(user_data, f, indent=4)