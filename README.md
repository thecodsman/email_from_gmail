# Email from Gmail

## How to use
create a `email_config.py` file and make a `user` variable and set it to your email address (eg. `user = johndoe@gmail.com`)
then make an app password for your gmail account if you dont already have one you can see how to do that [here](https://support.google.com/accounts/answer/185833?hl=en). Then set a `password` variable to your app password
then run `python manage.py runserver` then go to [http://127.0.0.1:8000/form/](http://127.0.0.1:8000/form/) and it should work

## General rules on how to edit the code
no more then 3 indents (the indent from declaring a function doesnt count) you can at the next section down on ways to do this
use `+=` rather than `a = a + b` and dont also you dont have to comment no literally everything just use good variable names and function names but if something isnt totally clear
then use a quick comment

## Ways to limit nesting
### Option number 1
one way to limit nesting is to "invert" if statements take this code for example
```python
for line in email:
    if line.startswith() != ">":
       emailstring.append(line) 
```

you can make it use less nesting like this
```python
for line in email:
    if line.startswith() == ">": continue
    emailstring.append(line)
```
**much better :)**

### Option number 2
**only do this if you cant do the first one**

take this code
```python
inputa = input('input some stuff')
inputb = input('input some stuff again')
inputs = [inputa, inputb]
for userinput in inputs:
    if userinput == inputa:
        if userinput.startswith("a"):
            print('blah blah blah')
        else:
            print('dooba')
    if userinput == inputb:
        for letter in userinput:
            if letter == 'a':
                print(f'dooba')
```
while this code has no actual use it proves that sometimes you cant do the first option 
so how would you get less nesting?
well you could do something like this:
```python
def get_inputs():
    inputa = input('input some stuff')
    inputb = input('input some stuff again')
    inputs = [inputa, inputb]
    return inputs, inputa, inputb

def print_inputs(userinput, inputa, inputb):
    if userinput == inputa:
        if not userinput.startswith("a"):
            print('dooba')
            continue
        print('blah blah blah')
        continue

    for letter in userinput: # inputb
        if letter != 'a': continue
        print('dooba')
                

inputs, inputa, inputb = get_inputs()
for userinput in inputs:
    print_inputs(userinput, inputa, inputb)
```
as you can see I also used the first method and that made it much more readable, also gave it less nesting.
While you are typing more lines of code, that isnt always the goal. You usually value readabilty over the amount of lines of code
and while the latter example might not look too much more readable then the first one now just imagine
what it would look like if you had 10 times the amount of code

