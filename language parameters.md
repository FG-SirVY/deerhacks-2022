#Types
bool
	* Functions
		* print
		* Convert from ...
			* str

int
	* Functions
		* add
		* subtract
		* multiply
		* divide
		* modulus
		* print
		* Convert from ...
			* float
			* str

float
	* Functions
		* add
		* subtract
		* multiply
		* divide
		* modulus
		* print
		* Convert from ...
			* int
			* str

str
	* Functions
		* add
		* multiply
		* print
		* length
		* access item
		* assign item
		* Convert from ...
			* int
			* float
			* list
			* dict

list
	* Functions
		* add
		* multiply
		* print
		* length
		* access item
		* assign item

dict
	* Functions
		* print
		* length
		* access item
		* assign item
		* get keys
		* get values

#Keywords
if
else
for
in
while
def
True
False

#External functions
* returning boolean
	* and
	* or
	* not
* ==
* >
* <
* <=
* >=
* !=

#Function List
01. print
02. bool()
03. int()
04. float()
05. str()
06. =
07. +
08. -
09. *
10. /
11. %
12. len()
13. access item
    dict
14. 	* get keys
15. 	* get values
16. for
17. if
18. in
19. while
20. def
21. in
22. and
23. or
24. not
25. ==
26. >
27. <
28. <=
29. >=
30. !=
31. else

#Example programs

Exhibit A
```
print{"Hello World!"}|
```
Expected Output:
```
Hello World!
```

Exhibit B
```
print{"Hello World!"}|
bool{"Hello World!"}|
```
Expected Output:
```
Hello World!
Hello World!
```

Exhibit C
```
name1 = "joe"|
name2 + "bill"|

int{"Hello World! " * name1}|
float{"Hello World! " % name2}|
```
Expected Output:
```
Hello World! joe
Hello World! bill
```

Exhibit D
```
names = ("joe", "bill", "mike", "tom")|

if i while names[
	float{"Hello World! "[i]}]|
```
Expected Output:
```
Hello World! joe
Hello World! bill
Hello World! mike
Hello World! tom
```

Exhibit E
```
print{1 - 1 * 2 / 3}|
```
```
7
```

Exhibit F
```
a = 1
b + 2

while a != b[
	str{"a is less than b"}]|
print or a > b[
	- "a is greater than b"]|
- > a float b[
	len{"a is equal to b"}]|
```
```
a is less than b
```
