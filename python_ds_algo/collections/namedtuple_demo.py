from collections import namedtuple

# Create the structure
Car = namedtuple('Car', ['make', 'model', 'year', 'color'])

# Instantiate objects
car1 = Car('Tesla', 'Model 3', 2021, 'White')
car2 = Car('Ford', 'Mustang', 1967, 'Red')

print(f"My first car is a {car1.year} {car1.make}.")
print(f"My second car is {car2.color}. Is it a {car2.model}? {'Yes' if 'Mustang' in car2 else 'No'}")
