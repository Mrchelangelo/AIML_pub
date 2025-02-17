from copy import deepcopy
class Symbol:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Symbol({self.name})"

    def get_symbols(self):
        return [self]


class NotLogic:
    """Uses the logical NOT symbol (¬)"""

    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f"¬{self.expr}"

    def __eq__(self, other):
        if isinstance(other, (NotLogic, NotHyphen)):  # Allow cross-class equality
            return self.expr == other.expr
        return False

    def __hash__(self):
        return hash(("NotHyphen", self.expr))

    def __repr__(self):
        return f"NotLogic({repr(self.expr)})"

    def get_symbols(self):
        return self.expr.get_symbols()


class NotHyphen:
    """Uses a hyphen (-) for negation"""

    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f"-{self.expr}"

    def __eq__(self, other):
        if isinstance(other, (NotLogic, NotHyphen)):  # Allow cross-class equality
            return self.expr == other.expr
        return False

    def __hash__(self):
        return hash(("NotHyphen", self.expr))

    def __repr__(self):
        return f"NotHyphen({repr(self.expr)})"

    def get_symbols(self):
        return self.expr.get_symbols()


class And:
    """Represents logical AND with multiple operands"""

    def __init__(self, *operands):
        if len(operands) < 2:
            raise ValueError("And must have at least two operands.")
        self.operands = operands

    def __str__(self):
        return f"({' ∧ '.join(str(op) for op in self.operands)})"

    def __repr__(self):
        return f"And({', '.join(repr(op) for op in self.operands)})"

    def get_symbols(self):
        return list(set(item for sublist in self.operands
                        for item in (sublist if isinstance(sublist, list) else sublist.get_symbols())))


class Or:
    """Represents logical OR with multiple operands"""

    def __init__(self, *operands):
        if len(operands) < 2:
            raise ValueError("Or must have at least two operands.")
        self.operands = operands

    def __str__(self):
        return f"({' ∨ '.join(str(op) for op in self.operands)})"

    def __repr__(self):
        return f"Or({', '.join(repr(op) for op in self.operands)})"

    def get_symbols(self):
        return list(set(item for sublist in self.operands
                        for item in (sublist if isinstance(sublist, list) else sublist.get_symbols())))


class Conditional:
    """Represents logical implication (A → B)"""

    def __init__(self, antecedent, consequent):
        self.antecedent = antecedent
        self.consequent = consequent

    def __str__(self):
        return f"({self.antecedent} → {self.consequent})"

    def __repr__(self):
        return f"Conditional({repr(self.antecedent)}, {repr(self.consequent)})"

    def get_symbols(self):
        return list(set(item for sublist in [self.antecedent, self.consequent]
                        for item in (sublist if isinstance(sublist, list) else sublist.get_symbols())))


class Biconditional:
    """Represents logical equivalence (A ↔ B)"""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def get_symbols(self):
        return list(set(item for sublist in [self.left, self.right]
                        for item in (sublist if isinstance(sublist, list) else sublist.get_symbols())))

    def __str__(self):
        return f"({self.left} ↔ {self.right})"

    def __repr__(self):
        return f"Biconditional({repr(self.left)}, {repr(self.right)})"


class Knowledge:
    """Define a class that holds the sentences to be known as
    true and allows to add additional sentences afterwards
    """

    def __init__(self, *operands):
        self._sentences = [operand for operand in operands] if operands else []
        self._tautology_detection()

    def add(self, operand):
        self._sentences.append(operand)
        self._tautology_detection()

    def get_symbols(self):
        return list(set(item for sublist in self._sentences
                        for item in (sublist if isinstance(sublist, list) else sublist.get_symbols())))

    def _tautology_detection(self):
    ##Not correct
        new_sentences = []
        for sentence in self._sentences:
            if isinstance(sentence, Conditional):
                antecedent = sentence.antecedent
                if isinstance(antecedent, Or):
                    operands = set(deepcopy(antecedent.operands))
                    for operand in operands:
                        if NotLogic(operand) in operands or NotHyphen(operand) in operands:
                            print(f"Tautology detected in {sentence}, updating Knowledge")
                            new_sentences.append(sentence.consequent)
                            break  # Stop checking this sentence, move to the next one

        self._sentences.extend(new_sentences)

    def __str__(self):
        if not self._sentences:
            return 'empty'
        return f"({' ∧ '.join(str(op) for op in self._sentences)})"

    def __repr__(self):
        if not self._sentences:
            return 'Knowledge(empty)'
        return f"Knowledge({', '.join(repr(op) for op in self._sentences)})"

class Entailment:
    """Represents logical entailment (KB ⊨ α)"""
    def __init__(self, knowledge, statement):
        if not isinstance(knowledge, Knowledge):
            raise TypeError("Knowledge must be an instance of the Knowledge class.")
        self.knowledge = knowledge
        self.statement = statement

    def __str__(self):
        return f"({self.knowledge} ⊨ {self.statement})"

    def __repr__(self):
        return f"Entailment({repr(self.knowledge)}, {repr(self.statement)})"

    def get_symbols(self):
        return list(set(self.knowledge.get_symbols() + self.statement.get_symbols()))

    def has_explosion(self):
        """Checks if the knowledge base contains a contradiction of the form And(a, NotLogic(a))."""
        for sentence in self.knowledge._sentences:
            if isinstance(sentence, And):
                # Extract symbols in the AND expression
                symbols = set(sentence.operands)

                for sym in symbols:
                    # Check if both a and NotLogic(a) exist
                    if any(isinstance(other, (NotLogic, NotHyphen)) and other.expr == sym for other in symbols):
                        return True  # Contradiction found → Explosion!

        return False  # No contradiction found



if __name__ == "__main__":
    # Example usage
    a = Symbol("A")
    b = Symbol("B")
    c = Symbol("C")

    not_logic = NotLogic(a)
    not_hyphen = NotHyphen(b)
    and_expr = And(a, b, c)
    or_expr = Or(not_logic, not_hyphen, c)
    conditional_expr = Conditional(a, b)
    biconditional_expr = Biconditional(a, c)

    print(not_logic)  # Output: ¬A
    print(not_hyphen)  # Output: -B
    print(and_expr)  # Output: (A ∧ B ∧ C)
    print(or_expr)  # Output: (¬A ∨ -B ∨ C)
    print(conditional_expr)  # Output: (A → B)
    print(biconditional_expr)  # Output: (A ↔ C)
    knowledge = Knowledge(or_expr)
    print(knowledge)
    knowledge.add(NotLogic(a))
    print(knowledge)
    print(type(not_logic))

    print([ele for ele in [["A", "B"], "A"]])
