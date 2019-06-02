import sys
import re

def make_a_dict(rules):
    """
    rules looks like this :
    ['G^H=>B', 'A+B+(C|D)=>E', 'E|C=>F', 'F+B+E=>Z']

    make_a_dict make it like this :
    {'B': ['G^H'], 'E': ['A+B+(C|D)'], 'F': ['E|C'], 'Z': ['F+B+E']}
    """
    print(rules)
    rules_in_dict = {}
    for elem in rules:
        if elem[-1] in rules_in_dict:
            rules_in_dict[elem[-1]].append(elem[:-3])
        else:
            rules_in_dict[elem[-1]] = [elem[:-3]]
    return rules_in_dict


class ShuntingYard:

    def __init__(self, expression):
        self.expression = expression
        self.final = []
        # self.operator = ["+", "|", "^", "!"]
        self.operator = ["+", "*", "/", "%", "-"]
        self.brackets = ["(", ")"]
        # self.priority = {")": 4, "+": 3, "|": 2, "^": 1, "(": 0}
        self.priority = {")": 3, "*": 2, "/": 2, "%": 2, "+": 1, "-": 1, "(": 0}

    def is_balanced(self):
        stack = []
        for letter in self.expression:
            if letter not in self.operator and not letter.isdigit():
                if letter not in self.brackets:
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
        for letter in self.expression:
            # print("expression : {}\nletter = {}\nstack : {}\nqueue : {}\n"\
            # .format(self.expression, letter, stack, queue))
            if letter not in self.operator and letter not in self.brackets:
                if not letter.isdigit():
                    raise SyntaxError("unknown letter: {}".format(letter))
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
        if self.rules_clean[index][0] != self.symbol[index]:
            raise SyntaxError("Need to have '{}' symbol".format(self.true_symbol))
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
        self.parse_true_letters()


    def solve(self, left, right, operator):
        print("The real one:{} {} {}".format(left, operator, right))
        if operator == "+":
            if left + right == 1:
                return True
            return False
        if operator == "|":
            return right or left
        if operator == "^":
            return right ^ left

    def take_part(self, part, equation):
        """
        This function return True or False.
        Check what is the bool() of the part sent in argument.
        """
        if part in self.true_letters:
            part = True
            if self.invert:
                part = False
        elif part in self.rules_clean:
            print("Not knowing this letter {}, go resolver".format(part))
            part = self.resolver(part)
        else:
            part = False
            if self.invert:
                part = True
        return part

    def parsing(self, equations):
        """
        The purpose of this function is to take two element of an equation(A+B):
        left part (A) and right part(B)
        """
        print("Beginning parsing with this equation: {}".format(equations[0]))
        equation = equations[0]
        self.left = equation[0]
        self.invert = 0
        if self.left == "!":
            """
            if equation type of !A + B
            """
            self.left = equation[1]
            equation = equation[1:]
            self.invert = 1

        self.left = self.take_part(self.left, equation)
        print("self.left is equal to {}".format(self.left))
        self.operator = equation[1]
        self.right = equation[2:]
        """
        self.right can be just "B" from equation "A + B" where "B" is the rigth
        part OR can be "B + C | D" from equation "A + B + C | D" where "A" is
        the left side and "B + C | D" the rigth side
        """
        print(self.right)
        if len(self.right) > 1:
            if self.right[0] == "!" and len(self.right) == 2:
                self.right = self.right[1]
                equation = equation[3:]
                self.invert = 1
            else:
                """
                if right part is "B + C | D", we need to parse it again so
                calling parsing again
                """
                t =  self.solve(self.left, self.parsing([equation[2:]]), self.operator)
                print(t)
                return t
        self.right = self.take_part(self.right, equation)
        print("self.right is equal to {}".format(self.right))
        t =  self.solve(self.left, self.right, self.operator)
        print(t)
        return t


    def resolver(self, letter):
        print("resolver active for this letter {}".format(letter))
        if letter in self.true_letters:
            return True
        if letter in self.rules_clean:
            self.equation = self.rules_clean[letter]
            t = self.parsing(self.rules_clean[letter])
            print(t)
            return t



def main():

    # exp = ExpertSystem()
    # print(exp.rules_clean)
    # result = []
    # for elem in exp.wanted_letters:
    #     result.append(exp.resolver(elem))
    # print("The result is: {}".format(result))

    sy = ShuntingYard("(5*4+3*)-1")
    sy.is_balanced()
    sy.converting()
    print(sy.final)
if __name__ == "__main__":
    main()
