import ast
import sys
from _ast import Expr
from typing import Any


def compare(a: str, b: str):
    a = normalize_code(a)
    b = normalize_code(b)

    dl = damerau_levenshtein(a, b)
    return round(1 - dl/max(len(a), len(b)), 3)


class AnnotationRemover(ast.NodeTransformer):
    def visit_Expr(self, node: Expr) -> Any:
        if node.value.__class__ == ast.Constant:
            return ''
        else:
            return node


def normalize_code(code: str):
    code_tree = ast.parse(code)
    code_tree = AnnotationRemover().visit(code_tree)
    return ast.unparse(code_tree)


def damerau_levenshtein(a: str, b: str):
    d = {}
    len_a = len(a)
    len_b = len(b)
    for i in range(-1, len_a + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len_b + 1):
        d[(-1, j)] = j + 1

    for i in range(len_a):
        for j in range(len_b):
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,  # удаление
                d[(i, j - 1)] + 1,  # вставка
                d[(i - 1, j - 1)] + (a[i] != b[j]),  # замена
            )
            if i > 1 and j > 1 and a[i] == b[j - 1] and a[i - 1] == b[j]:
                d[(i, j)] = min(
                    d[(i, j)],
                    d[(i - 2, j - 2)] + 1,  # перестановка
                )

    return d[len_a - 1, len_b - 1]


if __name__ == '__main__':
    scores = []
    f = open(sys.argv[1], 'r')
    for line in f:
        a, b = line.split()

        f_a = open(a, 'r', encoding='utf-8')
        code_a = f_a.read()
        f_a.close()

        f_b = open(b, 'r', encoding='utf-8')
        code_b = f_b.read()
        f_b.close()

        scores.append(compare(code_a, code_b))
    f.close()

    f = open(sys.argv[2], 'w')
    result = ''
    for x in scores:
        result += str(x) + '\n'
    f.write(result)
    f.close()
