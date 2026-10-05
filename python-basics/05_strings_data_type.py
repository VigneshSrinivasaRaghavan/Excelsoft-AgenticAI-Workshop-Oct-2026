# Create a string
first_name = "Vignesh"
last_name = 'Srinivasan'

# String indexing
text = "Python"
print(text[0]) # P
print(text[1]) # y
print(text[5]) # n
print(text[-1]) # n
print(text[-2]) # o

# String slicing
word = "Programming"
print(word[0:3]) # Pro
print(word[3:7]) # gram
print(word[:3]) # Pro
print(word[4:]) # ramming
print(word[-3:]) # ing

# String length
message = "Hello"
print(len(message))   # 5

# String concatenation (joining strings)
full_name = first_name + " " + last_name
print(full_name) # Vignesh Srinivasan

# String repetition
laugh = "Ha" * 3
print(laugh) # HaHaHa