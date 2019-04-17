import re
import csv
import os

from lexical_analyzer.regex_patterns import regex_patterns
from tokens.tokens import *


class LexicalAnalyzer:
    """
    Class that makes lexical analyse using diagram of states method
    YOU NEED TO USE ONLY __call__ METHOD OF CLASS TO LEXICAL ANALYSE
    Usage:
    lexical_analyzer = LexicalAnalyzer()
    tokens = lexical_analyzer(program_file_path + program_file_name)
    """
    def __init__(self):
        """
        Initialise all attributes
        """
        self.program: list = ...
        self.announcements_block: bool = ...
        self.has_to_read: bool = ...
        self.state: int = ...
        self.i: int = ...
        self.line: int = ...
        self.token: str = ...
        self.char: str = ...
        self.tokens: Tokens = ...

    def __call__(self, program_file_path):
        """
        Run all required methods
        :param program_file_path:
        :return:
        """
        self.root_dir = './'
        self.tables_path = self.root_dir + 'tables/'
        self.program_file_path = program_file_path
        self.program_file_name = self.program_file_path.split('/')[-1]
        self.program = None
        self.announcements_block = True
        self.line = 0
        self.token = ''
        self.i = 0
        self.state = 1
        self.has_to_read = False
        self.char = ''
        self.tokens = Tokens()

        self.read_program_from_file()
        self.create_tables_dir()
        self.generate_tokens()
        self.write_tables_to_files()
        return self.tokens

    def raise_exception(self, msg=None):
        """
        Function, that helps to raise exceptions with error message, that contains all information about error
        :param msg:
        :return:
        """
        err = self.token if self.token else self.program[self.line][self.i]
        self.write_tables_to_files()
        raise Exception(('line: {}\n'
                         'position: {}\n'
                         'token: {}\n\n'
                         '{}'
                         ).format(
                                str(self.line),
                                str(self.i),
                                repr(err),
                                msg
        ))

    def read_program_from_file(self):
        """
        Function, thar reads program text from input .txt file
        :return:
        """
        with open(self.program_file_path, 'r') as f:
            self.program = [row.strip(' ') for row in f]

    def write_tokens_to_file(self):
        """
        Function, that writes tokens to output file
        :return:
        """
        with open(self.tables_path + self.program_file_name + '/tokens.csv', 'w', newline='') as f:
            for token in self.tokens:
                csv.writer(f).writerow([
                    token.count, token.line_number, token.token,
                    token.idn_id, token.con_id, token.lab_id, token.token_id
                ])

    def write_idns_to_file(self):
        """
        Function, that writes identifiers to output file
        :return:
        """
        with open(self.tables_path + self.program_file_name + '/IDN.csv', 'w', newline='') as f:
            for identifier in self.tokens.identifiers:
                csv.writer(f).writerow([
                    identifier.count, identifier.token, identifier.value, identifier.idn_type
                ])

    def write_cons_to_file(self):
        """
        Function, that writes identifiers to output file
        :return:
        """
        with open(self.tables_path + self.program_file_name + '/CONST.csv', 'w', newline='') as f:
            for const in self.tokens.constants:
                csv.writer(f).writerow([
                    const.count, const.token, const.con_type
                ])

    def write_labs_to_file(self):
        """
        Function, that writes labels to output file
        :return:
        """
        with open(self.tables_path + self.program_file_name + '/LAB.csv', 'w', newline='') as f:
            for label in self.tokens.labels:
                csv.writer(f).writerow([
                    label.count, label.token
                ])

    def write_tables_to_files(self):
        """
        Function, that runs all functions, that writes to files
        :return:
        """
        self.write_tokens_to_file()
        self.write_idns_to_file()
        self.write_cons_to_file()
        self.write_labs_to_file()

    def create_tables_dir(self):
        """
        Function, that creates directory for output tables
        :return:
        """
        program_tables_path = self.tables_path + self.program_file_name
        if not os.path.isdir(self.tables_path):
            try:
                os.mkdir(self.tables_path)
            except OSError:
                self.raise_exception("Creation of the directory %s failed" % self.tables_path)
        if not os.path.isdir(program_tables_path):
            try:
                os.mkdir(program_tables_path)
            except OSError:
                self.raise_exception("Creation of the directory %s failed" % program_tables_path)

    def add_token(self, token_type=None):
        """
        Function, that adds token to self.tokens array, depending on its type
        :param token_type:
        :return:
        """
        if token_type == 'IDN':
            identifiers_temp = [identifier.token for identifier in self.tokens.identifiers]
            self.tokens.append(Token(self.line, self.token, idn_id=identifiers_temp.index(self.token)))
        elif token_type == 'CON':
            constants_temp = [float(constant.token) for constant in self.tokens.constants]
            self.tokens.append(Token(self.line, self.token, con_id=constants_temp.index(float(self.token))))
        elif token_type == 'LAB':
            labels_temp = [label.token for label in self.tokens.labels]
            self.tokens.append(Token(self.line, self.token, lab_id=labels_temp.index(self.token)))
        else:
            self.tokens.append(Token(self.line, self.token))

    def add_idn(self):
        """
        Function, that adds token with type identifier to self.identifiers array
        :return:
        """
        if self.token == 'begin':
            self.announcements_block = False

        if self.token in tokens_identifiers:
            self.add_token()
        else:
            idns_temp = [idn.token for idn in self.tokens.identifiers]
            if self.announcements_block and self.token in idns_temp:
                self.raise_exception('re-announcement of identifier')
            elif not self.announcements_block and self.token not in idns_temp:
                self.raise_exception('use of undeclared identifier')

            # add IDN
            if self.announcements_block:
                self.tokens.identifiers.append(Idn(self.token))
            self.add_token('IDN')

    def add_con(self):
        """
        Function, that adds token with type constant to self.constants array
        :return:
        """
        const_temp = [float(const.token) for const in self.tokens.constants]
        if not float(self.token) in const_temp:
            # define const type
            con_type = 'float' if '.' in self.token else 'int'
            self.tokens.constants.append(Con(self.token, con_type))
        self.add_token('CON')

    def add_lab(self):
        """
        Function, that adds token with type label to self.labels array
        :return:
        """
        lab_temp = [lab.token for lab in self.tokens.labels]
        if self.token not in lab_temp:
            self.tokens.labels.append(Lab(self.token))
        self.add_token('LAB')

    def generate_tokens(self):
        """
        Function, that generates tokens using diagram of states method
        :return:
        """
        while True:
            # if we reached EOF
            if self.line >= len(self.program):
                if self.token == '':
                    break

            # if we reached EOL or blank line
            while len(self.program[self.line]) == 0 or self.i >= len(self.program[self.line]):
                self.i = 0
                self.line += 1
                # if we reached EOF
                if self.line >= len(self.program):
                    break

            # if we reached EOF
            if self.line >= len(self.program):
                if self.token == '':
                    break

            # if there's need to start new token when we end previous
            if self.has_to_read:
                self.i += 1
                # if we reached EOL or blank line
                while len(self.program[self.line]) == 0 or self.i >= len(self.program[self.line]):
                    self.i = 0
                    self.line += 1
                    # if we reached EOF
                    if self.line >= len(self.program):
                        break
                # if we reached EOF
                if self.line >= len(self.program):
                    break
                self.token = ''
                self.has_to_read = False

            self.char = self.program[self.line][self.i] if self.line < len(self.program) else ''

            if self.state == 1:
                if re.match(regex_patterns['character'], self.char):
                    self.token += self.char
                    self.state = 2
                    self.i += 1
                elif re.match(regex_patterns['number_sign'], self.char):
                    self.token += self.char
                    self.state = 3
                    self.i += 1
                elif re.match(regex_patterns['digit'], self.char):
                    self.token += self.char
                    self.state = 5
                    self.i += 1
                elif re.match(regex_patterns['dot'], self.char):
                    self.token += self.char
                    self.state = 7
                    self.i += 1
                elif re.match(regex_patterns['single_separator'], self.char):
                    self.token += self.char
                    self.add_token()
                    self.state = 1
                    self.has_to_read = True
                elif re.match(regex_patterns['more'], self.char):
                    self.token += self.char
                    self.state = 8
                    self.i += 1
                elif re.match(regex_patterns['less'], self.char):
                    self.token += self.char
                    self.state = 9
                    self.i += 1
                elif re.match(regex_patterns['equal'], self.char):
                    self.token += self.char
                    self.state = 10
                    self.i += 1
                elif re.match(regex_patterns['not_equal'], self.char):
                    self.token += self.char
                    self.state = 11
                    self.i += 1
                # if next char is white separator
                elif re.match(regex_patterns['white_separator'], self.char) and self.i < len(self.program[self.line]):
                    while re.match(regex_patterns['white_separator'],
                                   self.program[self.line][self.i]) and self.i < len(self.program[self.line]):
                        self.i += 1
                        if self.i >= len(self.program[self.line]):
                            break
                else:
                    self.state = 1
                    self.has_to_read = True
                    self.raise_exception()

            elif self.state == 2:
                if re.match(regex_patterns['identifier'], self.char) or re.match(regex_patterns['digit'], self.char):
                    self.token += self.char
                    self.i += 1
                else:
                    self.add_idn()
                    self.state = 1
                    self.token = ''

            elif self.state == 3:
                if re.match(regex_patterns['identifier'], self.char):
                    self.token += self.char
                    self.i += 1
                    self.state = 4
                else:
                    self.state = 1
                    self.has_to_read = True
                    self.raise_exception()

            elif self.state == 4:
                if re.match(regex_patterns['identifier'], self.char):
                    self.token += self.char
                    self.i += 1
                else:
                    self.add_lab()
                    self.state = 1
                    self.token = ''

            elif self.state == 5:
                if re.match(regex_patterns['digit'], self.char):
                    self.token += self.char
                    self.i += 1
                elif re.match(regex_patterns['dot'], self.char):
                    self.token += self.char
                    self.i += 1
                    self.state = 6
                else:
                    self.add_con()
                    self.state = 1
                    self.token = ''

            elif self.state == 6:
                if re.match(regex_patterns['digit'], self.char):
                    self.token += self.char
                    self.i += 1
                else:
                    self.add_con()
                    self.state = 1
                    self.token = ''

            elif self.state == 7:
                if re.match(regex_patterns['digit'], self.char):
                    self.token += self.char
                    self.i += 1
                    self.state = 6
                else:
                    self.state = 1
                    self.has_to_read = True
                    self.raise_exception()

            elif self.state == 8:
                if re.match(regex_patterns['more'], self.char):
                    self.token += self.char
                    self.i += 1
                    self.add_token()
                    self.state = 1
                    self.token = ''
                elif re.match(regex_patterns['equal'], self.char):
                    self.token += self.char
                    self.add_token()
                    self.state = 1
                    self.has_to_read = True
                else:
                    self.add_token()
                    self.state = 1
                    self.token = ''

            elif self.state == 9:
                if re.match(regex_patterns['less'], self.char):
                    self.token += self.char
                    self.i += 1
                    self.add_token()
                    self.state = 1
                    self.token = ''
                elif re.match(regex_patterns['equal'], self.char):
                    self.token += self.char
                    self.add_token()
                    self.state = 1
                    self.has_to_read = True
                else:
                    self.add_token()
                    self.state = 1
                    self.token = ''

            elif self.state == 10:
                if re.match(regex_patterns['equal'], self.char):
                    self.token += self.char
                    self.add_token()
                    self.state = 1
                    self.has_to_read = True
                else:
                    self.add_token()
                    self.state = 1
                    self.token = ''

            elif self.state == 11:
                if re.match(regex_patterns['equal'], self.char):
                    self.token += self.char
                    self.add_token()
                    self.state = 1
                    self.has_to_read = True
                else:
                    self.state = 1
                    self.has_to_read = True
                    self.raise_exception()
