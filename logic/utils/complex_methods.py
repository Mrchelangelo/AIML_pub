from base_classes import *
import pandas as pd
import itertools


class Environment:
    def __init__(self, name, kb=None, sym=None):
        self._name = name
        if not kb and not sym:
            raise AttributeError("At least one of kb or sym must be given")
        self._knowledge = kb if kb is not None else Knowledge()
        self._symbols = sym if sym is not None else []
        if kb:
            self._symbols = self._symbols + [ele for ele
                                             in self._knowledge.get_symbols() if not ele in self._symbols]
        self._truthtable_base = Truthtable(self._symbols)

    def __str__(self):
        symbols = ', '.join(str(op) for op in self._symbols) if self._symbols else "empty"
        return (f"Environment {self._name} contains:"
                f"\n\tSymbols: ({symbols})" 
                f"\n\tKnowledge: ({str(self._knowledge)})")

    def __repr__(self):
        return (f"Environment {self._name} contains:"
                f"\n\tSymbols: ({', '.join(repr(op) for op in self._symbols)})" 
                f"\n\tKnowledge: ({repr(self._knowledge)})")

    def get_truthtable_base(self):
        return self._truthtable_base

    def check_knowledge(self, kb=None):
        if kb:
            knowledge = kb
        else:
            knowledge = self._knowledge
        dummy = self._truthtable_base.check_query(knowledge._sentences)
        dummy["kb"] = dummy[knowledge._sentences].apply(lambda x: all(x), axis=1)
        dummy.columns = pd.MultiIndex.from_tuples(
            [("Symbols", symbol) if symbol in self._symbols else
             ("Knowledgebase", symbol) for symbol in dummy.columns]
        )
        return dummy

    def independent_entailment_check(self, entailment):
        if entailment.has_explosion():
            return "Explosive Entailment, always True"
        knowledge = entailment.knowledge
        statement = entailment.statement
        k_tt = self.check_knowledge(knowledge)
        k_tt.columns = k_tt.columns.droplevel(0)
        if isinstance(statement, Symbol):
            s_tt = self._truthtable_base._table
        else:
            s_tt = self._truthtable_base.check_query(statement)
        combine = pd.merge(k_tt, s_tt, on=self._symbols)
        if not isinstance(statement, list):
            statement = [statement]
        if all((k and s) for k, s in combine[combine["kb"]][["kb"] + statement].itertuples(index=False, name=None)):
            print("Entailment is True")
        else:
            print("Entailment is False")
        return combine

    def entailment_check(self, statement):
        entailment = Entailment(self._knowledge, statement)
        return self.independent_entailment_check(entailment)

class Truthtable:
    def __init__(self, symbols):
        if not isinstance(symbols, list) or len(symbols) < 2:
            raise ValueError("Symbols has to be a list of lenght at least 2.")
        self._symbols = symbols
        self._table = self._generate_truth_table()
        self._functions = {
            NotLogic: self._not_check,
            NotHyphen: self._not_check,
            And: self._and_check,
            Or: self._or_check,
            Conditional: self._cond_check,
            Biconditional: self._bicond_check,
            Symbol: self._symbol_check
        }

    def _generate_truth_table(self):
        num_symbols = len(self._symbols)
        rows = list(itertools.product([False, True], repeat=num_symbols))
        return pd.DataFrame(rows, columns=self._symbols)

    def _check_query_input(self, query):
        if not isinstance(query, (
            NotHyphen, NotLogic, Or,
            Conditional, Biconditional, And, Symbol
        )):
            raise AttributeError("query is of the wrong type.")
        if any(symbol not in self._symbols for symbol in query.get_symbols()):
            raise AttributeError("There are unkown Symbols in the query.")

    def check_query(self, query):
        if isinstance(query, list):
            for sentence in query:
                self._check_query_input(sentence)
            return self._multi_query(query)

        self._check_query_input(query)
        return self._single_query(query)

    def _multi_query(self, query):
        df = self._table.copy()
        for sentence in query:
            df = pd.merge(df, self._single_query(sentence), on=self._symbols)
        return df

    def _single_query(self, query):
        return self._functions.get(type(query))(query)

    def _not_check(self, query):
        df = self._table.copy()
        df[query] = ~df[query.get_symbols()[0]]
        return df

    def _and_check(self, query):
        df = self._table.copy()
        df[query] = df[query.get_symbols()].apply(lambda x: all(x[ele] if isinstance(ele, Symbol)
                                                                else ~x[ele.get_symbols()].values[0]
                                                    for ele in query.operands), axis=1)
        return df

    def _or_check(self, query):
        df = self._table.copy()
        df[query] = df[query.get_symbols()].apply(
            lambda x: any(x[ele] if isinstance(ele, Symbol) else ~x[ele.get_symbols()].values[0]
                                                    for ele in query.operands), axis=1)
        return df

    def _bicond_check(self, query):
        df = self._table.copy()

        def help(row, query):
            left = row[query.left.get_symbols()].values[0]
            right = row[query.right.get_symbols()].values[0]
            if not isinstance(query.left, Symbol):
                left = ~left
            if not isinstance(query.right, Symbol):
                right = ~right
            if (left and right) or (not left and not right):
                return True
            return False

        df[query] = df[query.get_symbols()].apply(
            lambda x: help(x, query), axis=1)
        return df

    def _cond_check(self, query):
        df = self._table.copy()
        def help(row, query):
            antecedent = row[query.antecedent.get_symbols()].values[0]
            consequent = row[query.consequent.get_symbols()].values[0]
            if not isinstance(query.antecedent, Symbol):
                antecedent = ~antecedent
            if not isinstance(query.consequent, Symbol):
                consequent = ~consequent
            if (antecedent and not consequent):
                return False
            return True

        df[query] = df[query.get_symbols()].apply(
            lambda x: help(x, query), axis=1)
        return df

    def _symbol_check(self, query):
        df = self._table.copy()
        df[str(query)+"_kb"] = df[query]
        return df

    def __str__(self):
        return str(self._table)

    def __repr__(self):
        return repr(self._table)


# Example usage
m = Symbol("mythical") #Mythical
i = Symbol("immortal") #immortal
h = Symbol("horned") #horned
ma = Symbol("magical") #magical

im = Biconditional(m, i) # iff mythical then immortal
cond_h = Conditional(Or(i, NotLogic(i)), h) #if immortal or mortal then horned
cond_ma = Conditional(h, ma) # if horned, then magical

kb = Knowledge(im, cond_ma)
kb.add(cond_h)

unicorn = Environment("unicorn", kb=kb)
print(unicorn.check_knowledge())
is_mythical = unicorn.entailment_check(m) # check if mythical entailed
#print(is_mythical)
is_horned = unicorn.entailment_check(h) # check if horned
is_magical = unicorn.entailment_check(ma) # check if horned
#[print(is_magical[is_magical["kb"]][ele]) for ele in is_magical.columns]
