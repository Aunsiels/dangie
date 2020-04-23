from dangie import utils
from dangie.function import Function


class Solver:

    def __init__(self, functions, uids=None, relations=None):
        self.functions = functions
        linear_paths = utils.get_all_linear_paths(functions)
        self.uids = uids
        if self.uids is None:
            self.uids = utils.get_full_nicoleta_assumption_uids(linear_paths)
        self.relations = relations
        if self.relations is None:
            self.relations = sorted(utils.get_all_relations(functions))
        self.fst = utils.get_transducer_parser(functions)

    def solve(self, query_relation):
        if query_relation not in self.relations:
            return None
        query = Function()
        query.add_atom(query_relation, "x", "y")
        deter = utils.get_dfa_from_functions(self.functions, query_relation)
        cfg = query.get_longest_query_grammar(self.relations, self.uids)
        cfg = cfg.intersection(deter)
        if not cfg.is_empty():
            for word in cfg.get_words():
                return utils.get_translation(self.fst, word)
        return None