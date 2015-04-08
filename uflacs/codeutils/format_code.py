# Copyright (C) 2011-2015 Martin Sandve Alnes
#
# This file is part of UFLACS.
#
# UFLACS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UFLACS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with UFLACS. If not, see <http://www.gnu.org/licenses/>.

"""Tools for representing and formatting source code.

This file currently contains both utilities for stitching together code snippets
and a limited scope set of AST node classes for an intermediate high-level
representation of source code. To be refactored into something richer for a
nicer external API.
"""

from six import iteritems
from six.moves import zip
from six.moves import xrange as range

from ffc.log import error


def strip_trailing_whitespace(s):
    return '\n'.join(l.rstrip() for l in s.split('\n'))


def format_float(x):
    eps = 1e-12  # FIXME: Configurable threshold
    if abs(x) < eps:
        return "0.0"

    precision = 12  # FIXME: Configurable precision
    fmt = "%%.%de" % precision
    return fmt % x


def indent(text, level):
    if level == 0:
        return text
    ind = ' ' * (4 * level)
    return '\n'.join(ind + line for line in text.split('\n'))


def build_separated_list(values, sep):
    "Make a list with sep inserted between each value in values."
    items = []
    if len(values):
        for v in values[:-1]:
            items.append((v, sep))
        items.append(values[-1])
    return items


def build_initializer_list(values, begin="{ ", sep=", ", end=" }"):
    "Build a value initializer list."
    return [begin] + build_separated_list(values, sep) + [end]


def build_recursive_initializer_list(values, sizes):
    r = len(sizes)
    assert r > 0
    assert len(values) == sizes[0]

    if r == 1:
        initializer_list = tuple(build_initializer_list(values))

    elif r == 2:
        assert len(values[0]) == sizes[1]
        inner = []
        for i0 in range(sizes[0]):
            inner.append(tuple(build_initializer_list(values[i0])))
        initializer_list = ["{", Indented([build_separated_list(inner, ","), "}"])]

    elif r == 3:
        assert len(values[0]) == sizes[1]
        assert len(values[0][0]) == sizes[2]
        outer = []
        for i0 in range(sizes[0]):
            inner = []
            for i1 in range(sizes[1]):
                inner.append(tuple(build_initializer_list(values[i0][i1])))
            outer.append(Indented(["{", build_separated_list(inner, ","), "}"]))
        initializer_list = ["{", Indented([build_separated_list(outer, ","), "}"])]

    else:
        error("TODO: Make recursive implementation of initializer_list formatting.")

    return initializer_list


# TODO: This design mixes formatting and semantics. Splitting out the formatting would be better design.


class ASTNode(object):
    pass

class ASTOperator(ASTNode):
    pass

class ASTStatement(ASTNode):
    pass

class Indented(ASTNode): # TODO: Should be part of formatting.
    def __init__(self, code):
        self.code = code

    def format(self, level):
        return format_code(self.code, level + 1)

class Comment(ASTNode): # TODO: Make it a Commented(code, comment) instead? Add Annotated(code, annotation)?
    def __init__(self, comment):
        self.comment = comment

    def format(self, level):
        code = ("// ", self.comment)
        return format_code(code, level)

class Block(ASTNode): # TODO: Rename to Scope?
    def __init__(self, body, start='{', end='}'):
        self.start = start
        self.body = body
        self.end = end

    def format(self, level):
        code = [self.start, Indented(self.body), self.end]
        return format_code(code, level)


class TemplateArgumentList(ASTNode):
    singlelineseparators = ('<', ', ', '>')
    multilineseparators = ('<\n', ',\n', '\n>')

    def __init__(self, args, multiline=True):
        self.args = args
        self.multiline = multiline

    def format(self, level):
        if self.multiline:
            container = Indented
            start, sep, end = self.multilineseparators
        else:
            container = tuple
            start, sep, end = self.singlelineseparators
            # Add space to avoid >> template issue
            last = self.args[-1]
            if isinstance(last, TemplateArgumentList) or (
                    isinstance(last, Type) and last.template_arguments):
                end = ' ' + end
        code = [sep.join(format_code(arg) for arg in self.args)]
        code = (start, container(code), end)
        return format_code(code, level)


class Type(ASTNode):
    def __init__(self, name, template_arguments=None, multiline=False):
        self.name = name
        self.template_arguments = template_arguments
        self.multiline = multiline

    def format(self, level):
        code = self.name
        if self.template_arguments:
            code = code, TemplateArgumentList(self.template_arguments, self.multiline)
        return format_code(code, level)


class TypeDef(ASTNode):
    def __init__(self, type_, typedef):
        self.type_ = type_
        self.typedef = typedef

    def format(self, level):
        code = ('typedef ', self.type_, " %s;" % self.typedef)
        return format_code(code, level)


class Namespace(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def format(self, level):
        code = ['namespace %s' % self.name, Block(self.body)]
        return format_code(code, level)


class VariableDecl(ASTStatement):
    def __init__(self, typename, name, value=None):
        self.typename = typename
        self.name = name
        self.value = value

    def format(self, level):
        sep = " "
        code = (self.typename, sep, self.name)
        if self.value is not None:
            code += (" = ", self.value)
        code += (";",)
        return format_code(code, level)

# TODO: Add variable access type to replace explicit str instances all over the place.


class ArrayDecl(ASTStatement):
    def __init__(self, typename, name, sizes, values=None):
        self.typename = typename
        self.name = name
        self.sizes = (sizes,) if isinstance(sizes, int) else tuple(sizes)
        self.values = values

    def format(self, level):
        sep = " "
        brackets = tuple("[%d]" % n for n in self.sizes)
        if self.values is None:
            valuescode = ""
        else:
            # if any(sz == 0 for sz in self.sizes):
            #    initializer_list = "{}"
            # else:
            initializer_list = build_recursive_initializer_list(self.values, self.sizes)
            valuescode = (" = ", initializer_list)
        code = (self.typename, sep, self.name, brackets, valuescode, ";")
        return format_code(code, level)


class ArrayAccess(ASTOperator):
    def __init__(self, arraydecl, indices):
        if isinstance(arraydecl, ArrayDecl):
            self.arrayname = arraydecl.name
        else:
            self.arrayname = arraydecl

        if isinstance(indices, (list, tuple)):
            self.indices = indices
        else:
            self.indices = (indices,)

        # Early error checking of array dimensions
        if any(isinstance(i, int) and i < 0 for i in self.indices):
            raise ValueError("Index value < 0.")

        # Additional checks possible if we get an ArrayDecl instead of just a name
        if isinstance(arraydecl, ArrayDecl):
            if len(self.indices) != len(arraydecl.sizes):
                raise ValueError("Invalid number of indices.")
            if any((isinstance(i, int) and isinstance(d, int) and i >= d)
                   for i, d in zip(self.indices, arraydecl.sizes)):
                raise ValueError("Index value >= array dimension.")

    def format(self, level):
        brackets = tuple(("[", n, "]") for n in self.indices)
        code = (self.arrayname, brackets)
        return format_code(code, level)



class UnOp(ASTOperator):
    def __init__(self, arg):
        self.arg = arg

    def format(self, level):
        # TODO: Handle precedence at this level instead of in the ExprFormatter stuff?
        code = (type(self).op, self.arg)
        return format_code(code, level)

class BinOp(ASTOperator):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def format(self, level):
        # TODO: Handle precedence at this level instead of in the ExprFormatter stuff?
        #if self.lhs.precedence < self.precedence:
        #    lhs = ('(', self.lhs, ')')
        #else:
        #    lhs = self.lhs

        #if self.rhs.precedence <= self.precedence:
        #    rhs = ('(', self.rhs, ')')
        #else:
        #    rhs = self.rhs

        #code = (lhs, self.op, rhs)

        code = (self.lhs, type(self).op, self.rhs)

        return format_code(code, level)

class NOp(ASTOperator):
    def __init__(self, ops):
        self.ops = ops

    def format(self, level):
        # TODO: Handle precedence at this level instead of in the ExprFormatter stuff?
        code = []
        for op in self.ops:
            code.append(op)
            code.append(type(self).op)
        code = tuple(code[:-1])
        return format_code(code, level)


class Eq(BinOp):
    op = " == "

class Ne(BinOp):
    op = " != "

class Lt(BinOp):
    op = " < "

class Gt(BinOp):
    op = " > "

class Le(BinOp):
    op = " <= "

class Ge(BinOp):
    op = " >= "

class Not(UnOp):
    op = "!"

class And(BinOp):
    op = " && "

class Or(BinOp):
    op = " || "

class Conditional(ASTOperator):
    def __init__(self, condition, true, false):
        self.condition = condition
        self.true = false
        self.false = false

    def format(self, level):
        # TODO: Handle precedence at this level instead of in the ExprFormatter stuff?
        code = (self.condition, " ? ", self.true, " : ", self.false)
        return format_code(code, level)


class Negative(UnOp): # TODO: Negate?
    op = "-"

class Add(BinOp):
    op = " + "

class Sub(BinOp):
    op = " - "

class Mul(BinOp):
    op = " * "

class Div(BinOp):
    op = " / "


class Sum(NOp):
    op = " + "

class Product(NOp):
    op = " * "


class AssignBase(ASTStatement):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def format(self, level):
        code = (self.lhs, type(self).op, self.rhs, ";")
        return format_code(code, level)

class Assign(AssignBase):
    op = " = "

class AssignAdd(AssignBase):
    op = " += "

class AssignSub(AssignBase):
    op = " -= "

class AssignMul(AssignBase):
    op = " *= "

class AssignDiv(AssignBase):
    op = " /= "


class Return(ASTStatement):
    def __init__(self, value):
        self.value

    def format(self, level):
        code = ("return ", self.value, ";")
        return format_code(code, level)


# TODO: IfElseChain

# TODO: Switch

# TODO: Call, i.e. f(x,y) = Call("f", ("x", "y"))


class WhileLoop(ASTStatement):
    def __init__(self, check, body=None):
        self.check = check
        self.body = body

    def format(self, level):
        code = ("while (", self.check, ")")
        if self.body is not None:
            code = [code, Block(self.body)]
        return format_code(code, level)


class ForLoop(ASTStatement):
    def __init__(self, init, check, increment, body=None):
        self.init = init
        self.check = check
        self.increment = increment
        self.body = body

    def format(self, level):
        code = ("for (", self.init, "; ", self.check, "; ", self.increment, ")")
        if self.body is not None:
            code = [code, Block(self.body)]
        return format_code(code, level)


class ForRange(ASTStatement):
    def __init__(self, name, lower, upper, body=None):
        self.name = name
        self.lower = lower
        self.upper = upper
        self.body = body

    def format(self, level):
        init = ("int ", self.name, " = ", self.lower)
        check = (self.name, " < ", self.upper)
        increment = ("++", self.name)
        code = ForLoop(init, check, increment, body=self.body)
        return format_code(code, level)


class Class(ASTStatement):
    def __init__(self, name, superclass=None, public_body=None,
                 protected_body=None, private_body=None,
                 template_arguments=None, template_multiline=False):
        self.name = name
        self.superclass = superclass
        self.public_body = public_body
        self.protected_body = protected_body
        self.private_body = private_body
        self.template_arguments = template_arguments
        self.template_multiline = template_multiline

    def format(self, level):
        code = []
        if self.template_arguments:
            code += [('template', TemplateArgumentList(self.template_arguments,
                                                       self.template_multiline))]
        if self.superclass:
            code += ['class %s: public %s' % (self.name, self.superclass)]
        else:
            code += ['class %s' % self.name]
        code += ['{']
        if self.public_body:
            code += ['public:', Indented(self.public_body)]
        if self.protected_body:
            code += ['protected:', Indented(self.protected_body)]
        if self.private_body:
            code += ['private:', Indented(self.private_body)]
        code += ['};']
        return format_code(code, level)



def format_code(code, level=0):
    """Format code by stitching together snippets.

    The code can be built recursively using the following types:

    - str: Returned unchanged.

    - tuple: Concatenate items in tuple with no chars in between.

    - list: Concatenate items in tuple with newline in between.

    - Indented: Indent the code within this object one level.

    - Block: Wrap code in {} and indent it.

    - Namespace: Wrap code in a namespace.

    - Class: Piece together a class definition.

    - TemplateArgumentList: Format a template argument list, one line or one per type.

    - Type: Format a typename with or without template arguments.

    - TypeDef: Format a typedef for a type.

    - VariableDecl: Declaration of a variable.

    - ArrayDecl: Declaration of an array.

    - ArrayAccess: Access element of array.

    - Return: Return statement with value.

    - Assign: = statement.

    - AssignAdd: += statement.

    - AssignSub: -= statement.

    - AssignMul: *= statement.

    - AssignDiv: /= statement.

    See the respective classes for usage.
    """
    if isinstance(code, str):
        if level:
            return indent(code, level)
        else:
            return code

    if isinstance(code, list):
        return "\n".join(format_code(item, level) for item in code)

    if isinstance(code, tuple):
        joined = "".join(format_code(item, 0) for item in code)
        return format_code(joined, level)

    if isinstance(code, ASTNode):
        return code.format(level)

    if isinstance(code, int):
        return indent(str(code), level)

    if isinstance(code, float):
        return indent(format_float(code), level)

    raise RuntimeError("Unexpected type %s:\n%s" % (type(code), str(code)))
