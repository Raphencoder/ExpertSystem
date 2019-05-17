import sys
import re

def make_a_dict(rules):
    rules_in_dict = {}
    for elem in rules:
        rules_in_dict[elem[-1]] = elem[:-3]
    return rules_in_dict

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
        self.rules_clean = make_a_dict(self.rules_clean)
        print(self.rules_clean)

def parse_equation(eq):
    left = eq[0]
    op = eq[1]
    right = eq[2]
    return left, right, op



class Rule:

    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.operator = operator

    def solve(self):
        if self.operator == "+":
            return self.left + self.right
        if self.operator == "|":
            return self.right or self.left
        if self.operator == "^":
            return self.right ^ self.left

grid = {}

class ExpertSystem(Parsing):

    def __init__(self, letter):
        super().__init__()
        self.seen_letters = []
        self.wanted_letter = letter
        self.knowed_letters = []
        self.parse_true_letters()

    def resolver(self, letter, blacklist=-1):
        for i, elem in enumerate(self.rules_clean):
            if letter in elem and i != blacklist:
                index = i
        eq = self.rules_clean[i]
        tup = parse_equation(eq)
        if tup[0] in grid:
            tup[0] = grid[tup[0]].solve()
        else:
            print(self.rules_clean, eq, blacklist)
            self.resolver(tup[0], index)
        if tup[1] in grid:
            tup[1] = grid[tup[1]].solve()
        else:
            self.resolver(tup[1], index)
        print(self.rules_clean)



def main():
    p = Parsing()
    p.parse_true_letters()
    # exp = ExpertSystem(p.wanted_letters[0])
    # exp.resolver(p.wanted_letters[0])

if __name__ == "__main__":
    main()
