import os

from pyformlang.cfg import Variable, Terminal
from pyformlang.cfg.llone_parser import LLOneParser
from pyformlang.cfg.parse_tree import ParseTree

from dangie import utils
from dangie.function import Function


class Solver:

    def __init__(self, functions, uids=None, relations=None):
        self.word = None
        self.regex = ""
        self.functions = functions
        linear_paths = utils.get_all_linear_paths(functions)
        self.uids = uids
        if self.uids is None:
            self.uids = utils.get_full_nicoleta_assumption_uids(linear_paths)
        self.relations = relations
        if self.relations is None:
            self.relations = sorted(utils.get_all_relations(functions))
        self.fst = utils.get_transducer_parser(functions)

    def solve(self, query_relation, filename="latest"):
        if query_relation not in self.relations:
            return None
        query = Function()
        query.add_atom(query_relation, "x", "y")
        deter = utils.get_dfa_from_functions(self.functions, query_relation)
        self.regex = str(deter.to_regex())
        cfg = query.get_longest_query_grammar(self.relations, self.uids)
        cfg_inter = cfg.intersection(deter)
        if not cfg_inter.is_empty():
            for word in cfg_inter.get_words():
                llone_parser = LLOneParser(cfg)
                if llone_parser.is_llone_parsable():
                    parse_tree = llone_parser.get_llone_parse_tree(word)
                    parse_tree.write_as_dot(filename + ".dot")
                else:
                    parse_tree = self.construct_parse_tree(
                        [x.value for x in word],
                        query_relation,
                        "S")
                    parse_tree.write_as_dot(filename + ".dot")
                os.system("dot -Tsvg " + filename + ".dot -o " +
                          filename + ".svg")
                os.system("rm " + filename + ".dot")
                self.word = ".".join([x.value for x in word])
                return utils.get_translation(self.fst, word)
        return None

    def construct_parse_tree(self, word, query, non_terminal):
        if non_terminal == "S":
            return self._process_s(word, query)
        elif non_terminal[0] == "B":
            return self.process_b(word, query, non_terminal)
        elif non_terminal[0] == "L":
            return self.process_l(word, query, non_terminal)

    def process_l(self, word, query, non_terminal):
        parse_tree = ParseTree(Variable(non_terminal))
        parse_tree.sons.append(ParseTree(Terminal(non_terminal[1:])))
        parse_tree.sons.append(
            self.construct_parse_tree(
                word[1:-1],
                query,
                "B" + utils.get_inverse_relation(non_terminal[1:])
            )
        )
        parse_tree.sons.append(
            ParseTree(
                Terminal(utils.get_inverse_relation(non_terminal[1:]))
            )
        )
        return parse_tree

    def process_b(self, word, query, non_terminal):
        parse_tree = ParseTree(Variable(non_terminal))
        if len(word) == 0:
            #parse_tree.sons.append(ParseTree(Terminal("")))
            return parse_tree
        cut_pos = self._find_cut_pos(word)
        parse_tree = ParseTree(Variable(non_terminal))
        parse_tree.sons.append(
            self.construct_parse_tree(
                word[:cut_pos],
                query,
                non_terminal
            )
        )
        parse_tree.sons.append(
            self.construct_parse_tree(
                word[cut_pos:],
                query,
                "L" + word[cut_pos]
            )
        )
        return parse_tree

    def _process_s(self, word, query):
        parse_tree = ParseTree(Variable("S"))
        if word[-1] == query:
            parse_tree.sons.append(
                self.construct_parse_tree(word[:-1], query, "B" + query)
            )
            parse_tree.sons.append(ParseTree(Terminal(query)))
        else:
            cut_pos = self._find_cut_pos(word)
            parse_tree.sons.append(
                self.construct_parse_tree(word[:cut_pos],
                                          query,
                                          "B" + query)
            )
            parse_tree.sons.append(ParseTree(Terminal(query)))
            inverse_query = utils.get_inverse_relation(query)
            parse_tree.sons.append(
                self.construct_parse_tree(word[cut_pos + 1:-1],
                                          query,
                                          "B" +
                                          inverse_query)
            )
            parse_tree.sons.append(ParseTree(Terminal(inverse_query)))
        return parse_tree

    @staticmethod
    def _find_cut_pos(word):
        stack = [word[-1]]
        for i in range(len(word) - 2, -1, -1):
            if word[i] == utils.get_inverse_relation(stack[-1]):
                stack.pop()
            else:
                stack.append(word[i])
            if not stack:
                return i
        return -1
