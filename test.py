import sys
import re


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
        index = len(sys.argv)
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




init = Parsing()
init.parse_true_letters()
