fruitsList = ["apple", "banana", "cherry", "orange", "mango", "apple", "banana"]
fruits = {"apple", "banana", "cherry", "orange", "mango", "apple", "banana"}
print(fruitsList)
print(fruits)

# Adding items
fruits.add("grape")
print(fruits)

# Removing items
fruits.remove("banana")
print(fruits)

# Check if item exists
print("apple" in fruits)     # True
print("banana" in fruits)    # False