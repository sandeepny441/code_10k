# Base class
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        print(f"Hi, I'm {self.name} and I'm {self.age} years old.")

# Derived class (inherits from Person)
class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)  # Call parent constructor
        self.student_id = student_id

    def study(self):
        print(f"{self.name} is studying. Student ID: {self.student_id}")

# Using the classes
p1 = Person("Alice", 30)
p1.greet()

s1 = Student("Bob", 20, "S123")
s1.greet()     # inherited method
s1.study()     # student-specific method
