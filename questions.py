"""Curated questions. Cards have explicit outputs; gameplay never executes code."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Card:
    code: str
    output: str
    explanation: str
    concept: str = ""

@dataclass(frozen=True)
class Question:
    id: str
    topic: str
    difficulty: str
    target: str
    cards: tuple

# Output uses repr-style notation: quotes distinguish strings from numbers.
def question(id, topic, difficulty, target, rows):
    return Question(id, topic, difficulty, target, tuple(Card(*row) for row in rows))

QUESTIONS = [
question('arithmetic', 'Arithmetic', 'Beginner', '6', [
('2 * 3','6','Multiplication gives six.'),('12 // 2','6','Floor division gives an integer.'),('3 ** 2','9','Exponentiation means 3 multiplied by itself.'),('14 % 8','6','The remainder after dividing 14 by 8 is six.'),('12 / 2','6.0','True division produces a float, not an integer.'),('2 + 3 * 2','8','Multiplication happens before addition.')]),
question('variables', 'Variables', 'Beginner', '8', [
('x = 4\nx * 2','8','Substitute four for x.'),('x = 3\nx + 5','8','Three plus five is eight.'),('x = 8\nx == 8','True','Comparison produces a Boolean.'),('x = 2\nx ** 3','8','Two cubed is eight.'),('x = "8"\nx',"'8'",'Quotation marks make this a string.'),('x = 8\nx - 1','7','Subtracting one gives seven.')]),
question('strings', 'Strings', 'Beginner', "'py'", [
('"python"[:2]',"'py'",'The stop index two is excluded.'),('"p" + "y"',"'py'",'The plus operator joins strings.'),('"PY".lower()',"'py'",'Lower converts letters to lowercase.'),('"python"[2:]',"'thon'",'This starts at index two.'),('len("py")','2','Length returns an integer.'),('"py" * 2',"'pypy'",'Multiplication repeats a string.')]),
question('lists', 'Lists', 'Intermediate', '3', [
('[1, 2, 3][-1]','3','Negative one selects the final item.'),('len([4, 5, 6])','3','There are three elements.'),('[3, 6, 9][0]','3','The first index is zero.'),('[1, 2, 3][1]','2','Index one is the second item.'),('[3]','[3]','A one-item list is not an integer.'),('sum([1, 3])','4','The sum is four.')]),
question('slicing', 'Slicing', 'Intermediate', '[2, 4]', [
('[0, 2, 4, 6][1:3]','[2, 4]','Indices one and two are included.'),('[2, 4, 6][:2]','[2, 4]','Take the first two elements.'),('[2, 4, 6][:-1]','[2, 4]','Everything before the last element.'),('[0, 2, 4, 6][::2]','[0, 4]','A step of two skips alternate elements.'),('[2, 4][::-1]','[4, 2]','A negative step reverses the list.'),('[2, 4, 6][1:]','[4, 6]','Start at index one.')]),
question('boolean', 'Boolean logic', 'Intermediate', 'True', [
('3 < 5 and 2 == 2','True','Both conditions are true.'),('not False','True','Not reverses the Boolean value.'),('False or True','True','Or needs at least one true operand.'),('bool([])','False','An empty list is falsey.'),('3 > 5','False','Three is smaller than five.'),('1','1','An integer is not a Boolean, even though Python equality can equate them.')]),
question('functions', 'Functions', 'Advanced', '9', [
('def square(x):\n    return x * x\nsquare(3)','9','The function returns three squared.'),('max(2, 9, 4)','9','Max returns the largest argument.'),('sum([4, 5])','9','Sum adds the list elements.'),('len("nine")','4','There are four characters.'),('abs(-3)','3','Absolute value removes the minus sign.'),('round(8.2)','8','This rounds to the nearest integer.')]),
question('nested', 'Nested expressions', 'Advanced', '4', [
('len(str(1234))','4','Convert to a four-character string, then find its length.'),('max([min([4, 8]), 2])','4','The inner minimum is four; the outer maximum is four.'),('abs(min(-4, 2))','4','The minimum is negative four; its absolute value is four.'),('len([1, [2, 3]])','2','Only outer elements count.'),('sum([len("ab"), 1])','3','Two plus one gives three.'),('int("4") + 1','5','Conversion gives four, then add one.')]),
question('comprehensions', 'List comprehensions', 'Advanced', '[0, 2, 4]', [
('[x * 2 for x in range(3)]','[0, 2, 4]','Range produces zero, one, two; double each.'),('[x for x in range(5) if x % 2 == 0]','[0, 2, 4]','Keep the even numbers.'),('[x - 1 for x in [1, 3, 5]]','[0, 2, 4]','Subtract one from each item.'),('[x for x in range(3)]','[0, 1, 2]','No doubling is performed.'),('[x * 2 for x in range(1, 3)]','[2, 4]','The range starts at one.'),('[2 for x in range(3)]','[2, 2, 2]','The constant two is repeated.')]),
]

# Two additional authored variants per topic. Values change, concepts stay focused.
for value in (4, 5):
    n = value
    QUESTIONS.extend([
        question(f'arithmetic-{n}', 'Arithmetic', 'Beginner', str(n), [
            (f'{n-1} + 1',str(n),'Addition gives the target integer.'),
            (f'{n*2} // 2',str(n),'Floor division returns an integer.'),
            (f'{n*2} / 2',str(float(n)),'True division returns a float, not an integer.'),
            (f'{n+3} % 3',str((n+3)%3),'Modulo returns the division remainder.'),
            (f'2 + {n-2}',str(n),'Add the two integers.'),
            (f'{n} ** 2',str(n*n),'The exponent squares the number.')]),
        question(f'variables-{n}', 'Variables', 'Beginner', str(n), [
            (f'x = {n-1}\nx + 1',str(n),'Substitute the value of x before adding.'),
            (f'x = {n}\nx',str(n),'The expression returns the assigned integer.'),
            (f'x = {n}\nx == {n}','True','Comparison returns a Boolean, not a number.'),
            (f'x = "{n}"\nx',repr(str(n)),'The variable contains a string.'),
            (f'x = {n*2}\nx // 2',str(n),'The variable is divided using floor division.'),
            (f'x = {n}\nx + 2',str(n+2),'Two is added to the variable.')]),
        question(f'strings-{n}', 'Strings', 'Beginner', repr('a'*n), [
            (f'"a" * {n}',repr('a'*n),'Multiplication repeats the string.'),
            (f'"{"A"*n}".lower()',repr('a'*n),'Lower changes every letter to lowercase.'),
            (f'"{"a"*(n+1)}"[:-1]',repr('a'*n),'The final character is excluded.'),
            (f'len("{"a"*n}")',str(n),'Length is an integer, not a string.'),
            (f'"a" * {n-1}',repr('a'*(n-1)),'This repeats the character one fewer time.'),
            (f'"{"a"*n}".upper()',repr('A'*n),'Upper changes letters to uppercase.')]),
        question(f'lists-{n}', 'Lists', 'Intermediate', str(n), [
            (f'[{n}, 8, 9][0]',str(n),'Index zero selects the first item.'),
            (f'[1, 2, {n}][-1]',str(n),'Index minus one selects the last item.'),
            (f'len({list(range(n))})',str(n),'Count the elements in the outer list.'),
            (f'[{n}]',repr([n]),'A list containing a number is not that number.'),
            (f'[{n}, 8, 9][1]','8','Index one is the second item.'),
            (f'sum([{n}, 1])',str(n+1),'Sum adds all list elements.')]),
        question(f'slicing-{n}', 'Slicing', 'Intermediate', repr([n,n+1]), [
            (f'{[0,n,n+1,9]}[1:3]',repr([n,n+1]),'The start is included; the stop is excluded.'),
            (f'{[n,n+1,9]}[:2]',repr([n,n+1]),'Keep the first two elements.'),
            (f'{[n,n+1,9]}[:-1]',repr([n,n+1]),'Exclude the final element.'),
            (f'{[n,n+1]}[::-1]',repr([n+1,n]),'The negative step reverses order.'),
            (f'{[n,n+1,9]}[1:]',repr([n+1,9]),'Start at the second element.'),
            (f'{[n,n+1,9]}[::2]',repr([n,9]),'A step of two takes alternate items.')]),
        question(f'boolean-{n}', 'Boolean logic', 'Intermediate', 'False', [
            (f'{n} > {n+1}','False','The first number is smaller.'),
            ('not True','False','Not reverses True.'),
            ('True and False','False','And requires both operands to be true.'),
            ('True or False','True','Or requires only one true operand.'),
            (f'{n} == {n}','True','Equal numbers compare as true.'),
            ('0','0','Integer zero is not the Boolean False target.')]),
        question(f'functions-{n}', 'Functions', 'Advanced', str(n*n), [
            (f'def square(x):\n    return x * x\nsquare({n})',str(n*n),'The returned value is x squared.'),
            (f'pow({n}, 2)',str(n*n),'Pow raises its first argument to the second power.'),
            (f'max(1, {n*n}, 2)',str(n*n),'Max returns the largest argument.'),
            (f'abs(-{n})',str(n),'Absolute value returns the positive magnitude.'),
            (f'len("{n*n}")',str(len(str(n*n))),'Length counts characters.'),
            (f'sum([{n}, 1])',str(n+1),'Sum adds the numbers, rather than squaring.')]),
        question(f'nested-{n}', 'Nested expressions', 'Advanced', str(n), [
            (f'abs(min(-{n}, 2))',str(n),'Find the negative minimum, then its magnitude.'),
            (f'len(str({10**(n-1)}))',str(n),'Convert the number to a string and count its digits.'),
            (f'max(min({n}, {n+2}), 1)',str(n),'The inner minimum is larger than one.'),
            (f'sum([len("ab"), {n}])',str(n+2),'The string length is two; add it to the number.'),
            ('len([1, [2, 3]])','2','Nested elements do not add to the outer length.'),
            (f'int(str({n+1}))',str(n+1),'Converting to string and back preserves the number.')]),
        question(f'comprehensions-{n}', 'List comprehensions', 'Advanced', repr([0,n,2*n]), [
            (f'[x * {n} for x in range(3)]',repr([0,n,2*n]),'Multiply zero, one and two by the factor.'),
            (f'[x for x in range({2*n+1}) if x % {n} == 0]',repr([0,n,2*n]),'Keep multiples of the factor, including zero.'),
            (f'[x - 1 for x in {[1,n+1,2*n+1]}]',repr([0,n,2*n]),'Subtract one from every element.'),
            (f'[x * {n} for x in range(1, 3)]',repr([n,2*n]),'Starting at one excludes zero.'),
            (f'[{n} for x in range(3)]',repr([n,n,n]),'A constant expression repeats the same value.'),
            ('[x for x in range(3)]','[0, 1, 2]','The values are not multiplied.')]),
    ])

TOPICS = list({q.topic: q for q in QUESTIONS[:9]}.values())
STUDY_TIPS = {
'Arithmetic':'Review operator precedence, // versus /, and remainders (%).',
'Variables':'Trace assignments and substitute values; distinguish numbers, strings and comparisons.',
'Strings':'Practise concatenation, repetition, case conversion and string slices.',
'Lists':'Review zero-based indexing, negative indices, list length and sums.',
'Slicing':'Practise start:stop:step; the stop index is excluded.',
'Boolean logic':'Review AND, OR and NOT; distinguish Booleans from integers.',
'Functions':'Trace arguments and return values; review built-in functions.',
'Nested expressions':'Work from the innermost expression outwards.',
'List comprehensions':'Trace the range, filter condition and expression separately.',
}

# Broader variations: methods, precedence, negative indices, short-circuit logic,
# return values, comprehensions with filters, and multi-step expressions.
QUESTIONS.extend([
question('arithmetic-precedence','Arithmetic','Beginner','14',[
('2 + 3 * 4','14','Multiply three by four before adding two.'),('(2 + 3) * 4','20','Parentheses change the order of operations.'),('2 ** 3 + 6','14','Eight plus six is fourteen.'),('29 // 2','14','Floor division discards the fractional part.'),('29 / 2','14.5','True division keeps a fractional result.'),('29 % 2','1','Modulo returns the remainder, not the quotient.')]),
question('arithmetic-negative','Arithmetic','Beginner','-2',[
('3 - 5','-2','Subtracting five from three gives negative two.'),('-7 // 3','-3','Floor division rounds down, toward negative infinity.'),('-(6 // 3)','-2','Divide first, then apply the minus sign.'),('4 - 2 * 3','-2','Multiplication happens before subtraction.'),('(-2) ** 2','4','Squaring a negative number gives a positive value.'),('-2.0','-2.0','A float is not the target integer type.')]),
question('arithmetic-remainder','Arithmetic','Beginner','1',[
('10 % 3','1','Ten divided by three leaves one.'),('7 // 4','1','The integer quotient is one.'),('5 ** 0','1','A nonzero number raised to zero gives one.'),('10 / 10','1.0','True division returns a float.'),('10 // 3','3','The integer quotient is three.'),('True','True','A Boolean is a different target type.')]),
question('variables-reassign','Variables','Beginner','7',[
('x = 2\nx = x + 5\nx','7','The second assignment replaces x with seven.'),('x = 7\ny = x\ny','7','Copying the integer value gives seven.'),('x = 3\nx += 4\nx','7','Augmented assignment adds four.'),('x = 2\ny = x + 5\nx','2','Assigning y does not change x.'),('x = "7"\nx',"'7'",'This variable contains a string.'),('x = 7\nx == 7','True','Equality produces a Boolean.')]),
question('variables-swap','Variables','Beginner','3',[
('x, y = 3, 8\nx, y = y, x\ny','3','After swapping, y has the old value of x.'),('a = 3\nb = a\na = 9\nb','3','Reassigning a does not reassign b.'),('x = 6\nx //= 2\nx','3','Floor-dividing six by two gives integer three.'),('x = 6\nx /= 2\nx','3.0','True division produces a float.'),('x, y = 3, 8\nx, y = y, x\nx','8','After swapping, x is eight.'),('x = 3\nx > 0','True','A comparison returns a Boolean.')]),
question('variables-string','Variables','Beginner',"'12'",[
('x, y = "1", "2"\nx + y',"'12'",'The plus operator concatenates strings.'),('x = 12\nstr(x)',"'12'",'Str converts the integer to a string.'),('x = "012"\nx[1:]',"'12'",'Slicing removes the first character.'),('x, y = 1, 2\nx + y','3','Numeric addition differs from concatenation.'),('x = "12"\nlen(x)','2','Len returns an integer count.'),('x = "12"\nint(x)','12','Int converts to the number twelve.')]),
question('strings-strip','Strings','Beginner',"'code'",[
('" code ".strip()',"'code'",'Strip removes whitespace from both ends.'),('"Code".lower()',"'code'",'Lower changes uppercase letters.'),('"coding".replace("ing", "e")',"'code'",'Replace substitutes the matching substring.'),('"code".upper()',"'CODE'",'Upper changes letters to uppercase.'),('" code ".lstrip()',"'code '",'Lstrip leaves the trailing space.'),('"code".find("o")','1','Find returns a zero-based index.')]),
question('strings-methods','Strings','Beginner','True',[
('"python".startswith("py")','True','The string begins with py.'),('"123".isdigit()','True','All characters are digits.'),('"Code".istitle()','True','The word has title casing.'),('"python".endswith("py")','False','The string ends with on, not py.'),('"code".find("c")','0','Find returns an index rather than a Boolean.'),('"False"',"'False'",'This is text, not a Boolean.')]),
question('strings-join','Strings','Beginner',"'a-b'",[
('"-".join(["a", "b"])',"'a-b'",'Join inserts the separator between items.'),('"a" + "-" + "b"',"'a-b'",'Concatenation joins the three strings.'),('"A-B".lower()',"'a-b'",'Lower preserves the punctuation.'),('"a-b".split("-")',"['a', 'b']",'Split returns a list, not a string.'),('"ab"',"'ab'",'There is no hyphen.'),('len("a-b")','3','Length counts all three characters.')]),
question('lists-methods','Lists','Intermediate','2',[
('[1, 2, 2, 3].count(2)','2','Two appears twice.'),('[8, 6, 4].index(4)','2','The value four is at index two.'),('[1, 2].pop()','2','Pop returns the removed last item.'),('[1, 2].append(3)','None','Append changes the list and returns None.'),('len([[1, 2], [3, 4], [5]])','3','Only the three outer items are counted.'),('[2, 4][0:1]','[2]','A slice returns a list.')]),
question('lists-alias','Lists','Intermediate','[1, 2, 3]',[
('a = [1, 2]\nb = a\nb.append(3)\na','[1, 2, 3]','Both names refer to the same mutable list.'),('[1, 2] + [3]','[1, 2, 3]','Plus concatenates the two lists.'),('list(range(1, 4))','[1, 2, 3]','The stop value four is excluded.'),('a = [1, 2]\nb = a.copy()\nb.append(3)\na','[1, 2]','A copy is a separate outer list.'),('[1, 2, 3].reverse()','None','Reverse changes the list and returns None.'),('sorted([3, 1, 2], reverse=True)','[3, 2, 1]','Reverse sorting produces descending order.')]),
question('lists-nested','Lists','Intermediate','4',[
('[[1, 2], [3, 4]][1][1]','4','Select the second row, then the second item.'),('sum([1, 3])','4','Sum adds the elements.'),('len([0, 1, 2, 3])','4','There are four list elements.'),('len([[1, 2], [3, 4]])','2','The outer list has two rows.'),('[[1, 2], [3, 4]][0][1]','2','The first row, second item is two.'),('[4]','[4]','A list and an integer are different types.')]),
question('slicing-negative','Slicing','Intermediate',"'hon'",[
('"python"[-3:]',"'hon'",'Start three characters from the end.'),('"python"[3:6]',"'hon'",'Indices three, four and five are included.'),('"python"[3:]',"'hon'",'Omitting the stop continues to the end.'),('"python"[-3:-1]',"'ho'",'The final character is excluded.'),('"python"[::-1]',"'nohtyp'",'A negative step reverses the whole string.'),('"python"[2:]',"'thon'",'Index two starts at t.')]),
question('slicing-step','Slicing','Intermediate','[0, 2, 4]',[
('list(range(6))[::2]','[0, 2, 4]','A step of two selects even indices.'),('[0, 1, 2, 3, 4][0:5:2]','[0, 2, 4]','The start is zero and the step is two.'),('[0, 2, 4, 6][:-1]','[0, 2, 4]','Everything before the final element is retained.'),('list(range(6))[1::2]','[1, 3, 5]','Starting at index one selects odd indices.'),('[0, 2, 4][::-1]','[4, 2, 0]','Reversal changes the order.'),('list(range(6))[:2]','[0, 1]','The stop value is an index, not a step.')]),
question('slicing-bounds','Slicing','Intermediate',"''",[
('"code"[4:]',"''",'A slice can start at the string length and be empty.'),('"code"[2:2]',"''",'Equal start and stop bounds produce an empty slice.'),('"code"[8:20]',"''",'Out-of-range slice bounds are clipped safely.'),('"code"[:20]',"'code'",'A large stop still includes the existing characters.'),('"code"[-1:]',"'e'",'The final character is included.'),('"code"[0:1]',"'c'",'The first character is included.')]),
question('boolean-truthy','Boolean logic','Intermediate',"'ready'",[
('"" or "ready"',"'ready'",'Or returns the first truthy operand.'),('True and "ready"',"'ready'",'And returns its second operand when the first is truthy.'),('"ready" or "later"',"'ready'",'The first operand is already truthy.'),('bool("ready")','True','Bool returns a Boolean, not the string.'),('False and "ready"','False','And short-circuits on a falsey operand.'),('"" and "ready"',"''",'And returns the falsey empty string.')]),
question('boolean-precedence','Boolean logic','Intermediate','True',[
('not False and False or True','True','Not comes before and, then or.'),('False or True and True','True','And is evaluated before or.'),('1 < 2 < 3','True','Both comparisons in the chain are true.'),('not (False or True)','False','The parentheses evaluate to True first.'),('True and False','False','Both operands must be truthy.'),('1','1','The integer is not a Boolean target.')]),
question('boolean-membership','Boolean logic','Intermediate','False',[
('4 in [1, 2, 3]','False','Four is absent from the list.'),('"py" not in "python"','False','Py is present, so not in is false.'),('bool(0)','False','Numeric zero is falsey.'),('bool("False")','True','A nonempty string is truthy regardless of its words.'),('2 in [1, 2, 3]','True','Two is in the list.'),('0','0','Integer zero is a different type.')]),
question('functions-default','Functions','Advanced','5',[
('def add(x, y=2):\n    return x + y\nadd(3)','5','The default value of y is two.'),('def add(x, y=2):\n    return x + y\nadd(2, 3)','5','The supplied second argument overrides the default.'),('max([2, 5, 3])','5','Max returns the largest list element.'),('def add(x, y=2):\n    return x + y\nadd(3, 3)','6','Both explicit arguments are three.'),('len("five")','4','The word has four characters.'),('round(5.7)','6','Rounding gives six.')]),
question('functions-return','Functions','Advanced','None',[
('def change(x):\n    x + 1\nchange(2)','None','Without return, a function returns None.'),('[1, 2].append(3)','None','Append changes the list and returns None.'),('def nothing():\n    return\nnothing()','None','A bare return returns None.'),('def change(x):\n    return x + 1\nchange(2)','3','An explicit return provides the calculated value.'),('str(None)',"'None'",'This is a string representation, not None itself.'),('bool(None)','False','The Boolean conversion of None is False.')]),
question('functions-scope','Functions','Advanced','10',[
('x = 10\ndef f():\n    return 3\nx','10','Returning three does not reassign x.'),('def twice(x):\n    return x * 2\ntwice(5)','10','The argument five is doubled.'),('(lambda x: x + 4)(6)','10','The lambda returns its argument plus four.'),('x = 10\ndef f(x):\n    return x + 1\nf(x)','11','The returned expression adds one.'),('len([10])','1','The list has one item.'),('str(10)',"'10'",'A string is not the target integer.')]),
question('nested-conversion','Nested expressions','Advanced','3',[
('len(str(abs(-123)))','3','Take the magnitude, convert to text, then count digits.'),('min(max(1, 3), 9)','3','The inner max gives three; the outer min keeps it.'),('int("2") + len("x")','3','Two plus one is three.'),('str(len("abc"))',"'3'",'The final conversion changes the type to string.'),('len(str([1, 2]))','6','The representation includes brackets, a comma and a space.'),('abs(min(-4, -3))','4','The minimum is negative four.')]),
question('nested-collections','Nested expressions','Advanced','2',[
('len(sorted(set([1, 1, 2])))','2','Set removes duplicates before sorting and counting.'),('min([len("ab"), len("abcd")])','2','The string lengths are two and four.'),('sum([1, len("x")])','2','One plus one is two.'),('len(str(20)) + 1','3','The string has two characters, then add one.'),('max(min(3, 4), 2)','3','The inner minimum is three.'),('str(len([1, 2]))',"'2'",'The outer str returns text.')]),
question('nested-rounding','Nested expressions','Advanced','4',[
('round(abs(-3.8))','4','The magnitude rounds to four.'),('int(max("2", "4"))','4','Max selects the larger character, then int converts it.'),('sum([min(1, 2), max(2, 3)])','4','One plus three equals four.'),('len(str(4.0))','3','The string 4.0 contains three characters.'),('int(3.8)','3','Int truncates the fractional part.'),('str(round(3.8))',"'4'",'The final result is text.')]),
question('comp-filter','List comprehensions','Advanced','[4, 16]',[
('[x*x for x in range(1, 5) if x % 2 == 0]','[4, 16]','Filter to two and four, then square them.'),('[x**2 for x in [2, 4]]','[4, 16]','Square each listed item.'),('[x for x in [4, 9, 16] if x % 2 == 0]','[4, 16]','Keep the even values.'),('[x*2 for x in [2, 4]]','[4, 8]','Doubling is different from squaring.'),('[x*x for x in range(2, 4)]','[4, 9]','Range includes two and three.'),('[4, 16][::-1]','[16, 4]','Reversing changes the order.')]),
question('comp-strings','List comprehensions','Advanced',"['A', 'B']",[
('[x.upper() for x in "ab"]',"['A', 'B']",'Each character becomes an uppercase list item.'),('[x for x in "ABC" if x != "C"]',"['A', 'B']",'The filter removes C.'),('list("AB")',"['A', 'B']",'List splits the string into characters.'),('"ab".upper()',"'AB'",'This is one string rather than a list.'),('[x for x in "ab"]',"['a', 'b']",'No uppercase conversion occurs.'),('[len(x) for x in "ab"]','[1, 1]','Each character has length one.')]),
question('comp-conditional','List comprehensions','Advanced','[0, 1, 0]',[
('[x % 2 for x in range(3)]','[0, 1, 0]','The remainder alternates even, odd, even.'),('[1 if x == 1 else 0 for x in range(3)]','[0, 1, 0]','Only the middle value produces one.'),('[x for x in [0, 1, 0]]','[0, 1, 0]','The comprehension copies the values.'),('[x for x in range(3) if x % 2]','[1]','The filter removes even numbers instead of producing zeroes.'),('[x % 2 for x in range(1, 4)]','[1, 0, 1]','Starting at one reverses the pattern.'),('[0 for x in range(3)]','[0, 0, 0]','The expression is a constant zero.')]),
])

def concept_for(topic,code):
    if '.append(' in code or '.reverse(' in code:return 'In-place methods return None'
    if 'copy()' in code or 'b = a' in code:return 'Aliasing versus copying'
    if 'return' in code and topic=='Functions':return 'Function return values'
    if '// ' in code or '/ ' in code:return 'Division and result types'
    if '%' in code:return 'Remainders and filters'
    if '[::' in code or ':-' in code or '[-' in code:return 'Slice steps and negative indices'
    if '[' in code and ':' in code:return 'Exclusive slice stop'
    if 'for ' in code and 'if ' in code:return 'Comprehension filters and expressions'
    if 'for ' in code:return 'Comprehension iteration'
    if ' and ' in code or ' or ' in code:return 'Boolean operands and short-circuiting'
    if 'len(' in code:return 'Length and outer collections'
    if 'str(' in code or 'int(' in code:return 'Type conversion'
    if '.lower(' in code or '.upper(' in code:return 'String case methods'
    return topic

from dataclasses import replace as _replace
QUESTIONS=[_replace(q,cards=tuple(_replace(c,concept=concept_for(q.topic,c.code)) for c in q.cards)) for q in QUESTIONS]
