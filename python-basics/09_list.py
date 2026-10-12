# List in python is nothign but a array in other languages

# Create a list
fruits = ["apple", "banana", "cherry", "orange", "mango"]
numbers = [1, 2, 3, 4, 5]
mixed = ["apple", 1, True, 3.14]

# Accessing elements in a list
print(fruits[1])  # banana
print(numbers[2])  # 3
print(fruits[2])  # cherry
print(fruits[-1])  # cherry

# Slicing a List
print(fruits[0:2]) # ["apple", "banana"]
print(fruits[:2]) # ["apple", "banana"]
print(fruits[1:3]) # ["banana", "cherry"]
print(fruits[3:]) # ["orange", "mango"]
print(fruits[0:-2]) # ["apple", "banana", "cherry"]

# Add an item to the list
fruits.append("pineapple") # At the end of the list
print(fruits)

fruits.insert(0, "watermelon") # At the index 0
fruits.insert(1, "grape") # At the index 1
fruits.insert(3, "strawberry") # At the index 3
print(fruits)

# Remove an item
fruits.remove("banana") # Remove the first occurrence of "banana"
print(fruits)

fruits.pop() # Remove the last item
print(fruits)

# Checking if an item is in the list --> always returns a boolean value
print("strawberry" in fruits) # True
print("banana" in fruits) # False

# Changing the value of an item
fruits[-1] = "kiwi"
print(fruits)