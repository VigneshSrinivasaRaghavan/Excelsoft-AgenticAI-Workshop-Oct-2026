# No indentation is required
age = 18

# Regular indentation
if age >= 18:
    print("You are an adult")
    print("You can vote")

# Multple level of indentation
if age >= 18:
    print("Adult check passed")
    if age >= 21:
        print("You can drink")
        if age >= 25:
            print("You can vote")
    else:
        print("Not old enough to drink")