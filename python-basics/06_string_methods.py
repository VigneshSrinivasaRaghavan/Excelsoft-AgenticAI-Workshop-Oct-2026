text = "hello world"
print(text.upper())        # HELLO WORLD
print(text.lower())        # hello world
print(text.capitalize())   # Hello world
print(text.title())        # Hello World

# Stripping whitespace
text = "   hello world   "
formatted_text = text.strip()
print(formatted_text) # hello world

# Replacing text
sentence = "I like cats"
print(sentence)
formatted_sentence = sentence.replace("cats", "dogs")
print(formatted_sentence)

# Splitting text
words = "apple,banana,cherry"
print(words.split(",")) # ['apple', 'banana', 'cherry']

# checking if a string contains a substring
text = "python is fun"
print("fun" in text) # True
print("vignesh" in text) # False

# String formatting - Using f-strings (modern way)
name = "Vignesh"
age = 30
height = 5.8
city = "Chennai"
print("Hi I am " + name + " and I am " + str(age) + " years old and I live in " + city + " and my height is " + str(height))
print(f"Hi I am {name} and I am {age} years old and I live in {city} and my height is {height}")

# F-strings with expressions
price = 19.99
quantity = 3
total = price * quantity
print("The total price is $" + str(total))
print(f"The total price is ${price * quantity}")