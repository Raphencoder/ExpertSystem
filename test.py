import sys
import re


class Parsing:

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



class Rule:

    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.operator = operator

    def solve(self):
        if self.operator == "+":
            if len(self.right) > 2:
                return solve(self.right) and solve(self.left)
        if self.operator == "|":
            return self.right or self.left
        if self.operator == "^":
            return self.right ^ self.left


class ExpertSystem(Parsing):

    def __init__(self, letter):
        super().__init__()
        self.seen_letters = []
        self.wanted_letter = letter


    def resolver(self):
        self.parse_true_letters()
        for i, elem in enumerate(self.rules_clean):
            if self.wanted_letter in elem:
                index = i


def main():
    p = Parsing()
    p.parse_true_letters()
    exp = ExpertSystem(p.wanted_letters[0])
    exp.resolver()

if __name__ == "__main__":
    main()
