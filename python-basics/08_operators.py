# Arithmetic Operators
x = 10
y = 3
print(x + y)    # Addition: 13
print(x - y)    # Subtraction: 7
print(x * y)    # Multiplication: 30
print(x / y)    # Division: 3.333... (float)
print(x // y)   # Floor Division: 3 (integer)
print(x % y)    # Modulus (remainder): 1
print(x ** y)   # Power: 1000

# Comparison Operators --> always return a boolean value
a = 10
b = 20


print(a == b)   # Equal to: False
print(a != b)   # Not equal to: True
print(a > b)    # Greater than: False
print(a < b)    # Less than: True
print(a >= b)   # Greater or equal: False
print(a <= b)   # Less or equal: True

# Logical Operators
age = 25
age2 = 10
has_license = True
can_drink = False

print(age >= 18 and has_license)  # True
print(age2 >= 18 and has_license)  # False

print(age >= 18 or has_license)  # True
print(age2 >= 18 or has_license)  # True
print(age2 >= 18 or can_drink)  # False

print(not has_license)  # False
print(not can_drink)  # True