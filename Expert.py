import sys
import re


"""
TODO :
    - Multiple rules for one letter
"""


def make_a_dict(rules):
    """
    rules looks like this :
    ['G^H=>B', 'A+B+(C|D)=>E', 'E|C=>F', 'F+B+E=>Z']

    make_a_dict make it like this :
    {'B': ['G^H'], 'E': ['A+B+(C|D)'], 'F': ['E|C'], 'Z': ['F+B+E']}
    """
    rules_in_dict = {}
    for elem in rules:
        if elem[-1] in rules_in_dict:
            rules_in_dict[elem[-1]].append(elem[:-3])
        else:
            shunt_yard = ShuntingYard(elem[:-3])
            shunt_yard.is_balanced()
            shunt_yard.converting()
            rules_in_dict[elem[-1]] = shunt_yard.final
    return rules_in_dict

def check_data(rules):
    equal = "=>"
    symbol = ["!", "*", "+", "^", "|"]
    parenth = ["(", ")"]
    flag = 0
    for elem in rules:
        if equal not in elem:
            raise SyntaxError("Not what expected")
        for letter in elem:
            if letter not in symbol and\
            not letter.isupper() and\
            letter not in parenth and\
            (letter != "=" and letter != ">"):
                print(letter)
                raise SyntaxError("Not what expected")
            if letter == "=":
                flag = 1
            elif flag and letter != ">":
                print(letter)
                raise SyntaxError("Not what expected")
            else:
                flag = 0


class ShuntingYard:

    def __init__(self, expression):
        self.expression = expression
        self.final = []
        self.operator = ["+", "|", "^"]
        self.brackets = ["(", ")"]
        self.priority = {")": 4, "+": 3, "|": 2, "^": 1, "(": 0}

    def is_balanced(self):
        stack = []
        for letter in self.expression:
            if letter not in self.operator and not letter.isupper():
                if letter not in self.brackets and letter != "!":
                    raise SyntaxError("unknown letter: {}".format(letter))
                if letter == "(":
                    stack.append(letter)
                elif letter == ")":
                    if str(stack[-1:]) == "['(']":
                        stack.pop()
                    else:
                        raise SyntaxError("The expression is not balanced")
        if stack:
            raise SyntaxError("The expression is not balanced")
        return True

    def converting(self):
        stack = []
        queue = []
        flag = 0
        for letter in self.expression:
            print("expression : {}\nletter = {}\nstack : {}\nqueue : {}\n"\
            .format(self.expression, letter, stack, queue))
            if letter not in self.operator and letter not in self.brackets:
                if not letter.isupper() and letter != "!":
                    raise SyntaxError("unknown letter: {}".format(letter))
                if flag:
                    queue.append("!" + letter)
                    flag = 0
                elif letter == "!":
                    flag = 1
                else:
                    queue.append(letter)
            elif letter in self.brackets:
                if letter == "(":
                    stack.append(letter)
                else:
                    while str(stack[-1:]) != "['(']":
                        queue.append(stack[-1])
                        stack.pop()
                    stack.pop()
            elif letter in self.operator and letter != "!":
                while stack and \
                self.priority[stack[-1]] >= self.priority[letter]:
                    queue.append(stack[-1])
                    stack.pop()
                stack.append(letter)
        stack.reverse()
        for elem in stack:
            queue.append(elem)
        self.final = queue


class Parsing:
    """
    This class parse the text into a structured dict and parse the
    wanted_letters, the true_letters ...
    """

    def __init__(self):

        self.rules = []
        self.rules_clean = []
        self.wanted_letters = []
        self.true_letters = []
        self.wanted_letters_index = -1
        self.true_letters_index = -2
        self.symbol = ["=", "?"]
        self.minimal_length = 2


    def parse(self, index):
        parses = []
        if not self.rules_clean[index] or self.rules_clean[index][0] != self.symbol[index]:
            raise SyntaxError("Need to have '{}' symbol. Newline not accepted"\
                            .format(self.symbol[index]))
        for idx, letter in enumerate(self.rules_clean[index]):
            if idx == 0:
                continue
            if letter.isupper() and letter.isalpha():
                parses.append(letter)
            else:
                raise SyntaxError("invalid syntax {}".format(letter))
        return parses

    def take_the_data(self):
        """
        First fonction called
        """
        index = 0
        for elem in sys.argv:
            index += 1
        if index != 2:
            raise OSError("Need one argument")
        self.filename = sys.argv[1]
        try:
            with open(self.filename, 'r') as f:
                self.rules = f.readlines()
        except FileNotFoundError:
            print("[Errno 2] No such file or directory: '{}'".format(sys.argv[1]))

    def clean(self):
        self.take_the_data()
        for elem in self.rules:
            self.rules_clean.append(re.sub("[ \t\n]", '', elem))
        if len(self.rules_clean) < self.minimal_length:
            raise SyntaxError("wrong file format")

    def parse_wanted_letters(self):
        self.clean()
        self.wanted_letters = self.parse(self.wanted_letters_index)

    def parse_true_letters(self):
        self.parse_wanted_letters()
        self.true_letters = self.parse(self.true_letters_index)
        self.rules_clean = self.rules_clean[:-2]
        if check_data(self.rules_clean):
            raise SyntaxError("Not the rules expected")
        self.rules_clean = make_a_dict(self.rules_clean)


class ExpertSystem(Parsing):
    """
    ExpertSystem is a class allow to resolve boolean equation.
    It will take the equation and resolve it from left to right, searching
    for unknown letter everytime it seen one.
    """


    def __init__(self):
        super().__init__()
        self.seen_letters = []
        self.knowed_letters = []
        self.operators = ["+", "|", "^"]
        self.parse_true_letters()
        self.left = []
        self.invert = 0

    def solve(self, left, right, operator):
        print("The real one:{} {} {}".format(left, operator, right))
        if operator == "+":
            print(left and right)
            return left and right
        if operator == "|":
            return right or left
        if operator == "^":
            return right ^ left

    def take_part(self, part):
        """
        This function return True or False.
        Check what is the bool() of the part sent in argument.
        """
        flag = 0
        if part == True or part == False:
            return part
        if part[0] == "!":
            flag = 1
            part = part[1]
            print("OK")
        if part in self.true_letters:
            part = True
            if self.invert:
                part = False
        elif part in self.rules_clean:
            print("Not knowing this letter {}, go resolver".format(part))
            part = self.resolver(part)
            print("ending here the result {}".format(part))
        else:
            part = False
            if self.invert:
                part = True
        if flag:
            return not part
        return part

    def parsing(self, equation):
        """
        The purpose of this function is to take two element of an equation(A+B):
        left part (A) and right part(B)
        """
        print("Beginning parsing with this equation: {}".format(equation))
        if len(equation) == 1:
            return self.take_part(equation[0])
        flag = 0
        stack = []
        need_to_parse = 0
        for idx, letter in enumerate(equation):
            print(stack)
            if letter == True or letter == False:
                stack.append(letter)
            elif letter in self.operators:
                left = stack[-2]
                right = stack[-1]
                operator = letter
                if idx + 1 < len(equation):
                    need_to_parse = idx + 1
                break
            elif letter.isupper() or letter == "!":
                if letter == "!":
                    stack.append(letter + equation[idx+1])
                    self.invert = 1
                    flag = 1
                else:
                    if not flag:
                        stack.append(letter)
                    else:
                        flag = 0
        print("left: {}\nright: {}\noperator: {}\nstack: {}\nequation: {}".format(left, right, operator, stack, equation))
        left = self.take_part(left)
        right = self.take_part(right)
        if need_to_parse:
            print("stack", stack)
            if len(stack) > 2:
                equation = stack[:-2] + [self.solve(left, right, operator)] + equation[need_to_parse:]
            else:
                equation = [self.solve(left, right, operator)] + equation[need_to_parse:]
            print("the new equation {}".format(equation))
            return self.parsing(equation)
        return self.solve(left, right, operator)


    def resolver(self, letter):
        print("resolver active for this letter {}".format(letter))
        if letter in self.true_letters:
            return True
        if letter not in self.rules_clean.keys():
            return False
        if letter in self.rules_clean:
            self.equation = self.rules_clean[letter]
            t = self.parsing(self.equation)
            print(t)
            return t



def main():

    exp = ExpertSystem()
    print(exp.rules_clean)
    result = {}
    for elem in exp.wanted_letters:
        result[elem] = exp.resolver(elem)
        print("FOR THIS LETTER {} THE RESULT IS: {}".format(elem, result[elem]))
    print("The result is: {}".format(result))

    # sy = ShuntingYard("(5*4+3*)-1")
    # sy.is_balanced()
    # sy.converting()
    # print(sy.final)
if __name__ == "__main__":
    main()
