user = {
    "name": "Alice",
    "age": 25,
    "city": "New York"
}
print(user["age"])
user["email"] = "alice@example.com"
print(user)

user["name"] = "Alice bob"
print(user)

del user["email"]
print(user)

print("name" in user) # True
print("email" in user) # False

# Nested dictionary
agent_config = {
    "model": "gpt-4",
    "settings": {
        "temperature": {
            "value": 0.7,
            "description": "The temperature of the model"
        },
        "max_tokens": 2000
    },
    "tools": ["calculator", "web_search"]
}
print(agent_config["settings"]["temperature"]["value"])