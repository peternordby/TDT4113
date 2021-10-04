import math
import numbers
import re
import unittest
import numpy

__author__ = "Peter Skaar Nordby"


class Container():
    def __init__(self):
        self._items = []

    def size(self):
        return len(self._items)

    def is_empty(self):
        return len(self._items) == 0

    def push(self, item):
        self._items.append(item)

    def pop(self):
        raise NotImplementedError

    def peek(self):
        raise NotImplementedError


class Stack(Container):
    def pop(self):
        assert not self.is_empty()
        return self._items.pop(-1)

    def peek(self):
        assert not self.is_empty()
        return self._items[-1]


class Queue(Container):
    def pop(self):
        assert not self.is_empty()
        return self._items.pop(0)

    def peek(self):
        assert not self.is_empty()
        return self._items[0]


class TestCalculator(unittest.TestCase):
    def test_stack(self):
        stack = Stack()
        stack.push(1)
        stack.push(2)
        stack.push(3)
        last_in = stack.pop()
        self.assertEqual(last_in, 3)
        on_top = stack.peek()
        self.assertEqual(on_top, 2)

    def test_queue(self):
        queue = Queue()
        queue.push(1)
        queue.push(2)
        queue.push(3)
        first_in = queue.pop()
        self.assertEqual(first_in, 1)
        fist_in_line = queue.peek()
        self.assertEqual(fist_in_line, 2)

    def test_function(self):
        exponential_function = Function(numpy.exp)
        sin_func = Function(numpy.sin)
        self.assertEqual(exponential_function.execute(
            sin_func.execute(0)), math.exp(math.sin(0)))

    def test_operator(self):
        add_op = Operator(numpy.add, 0)
        multiply_op = Operator(numpy.multiply, 1)
        self.assertEqual(add_op.execute(
            1, multiply_op.execute(2, 3)), 1+2*3)

    def test_calculator(self):
        calc = Calculator()
        self.assertEqual(calc.functions['EXP'].execute(
            calc.operators['ADD'].execute(1, calc.operators['MULTIPLY'].execute(2, 3))), math.exp((1+(2*3))))

    def test_rpn(self):
        calc = Calculator()
        calc.output_queue.push(1)
        calc.output_queue.push(2)
        calc.output_queue.push(3)
        calc.output_queue.push(calc.operators['MULTIPLY'])
        calc.output_queue.push(calc.operators['ADD'])
        calc.output_queue.push(calc.functions['EXP'])
        self.assertEqual(calc.evaluate_rpn(calc.output_queue), math.exp(1+2*3))

    def test_notation(self):
        calc = Calculator()
        notation = Queue()
        notation.push(calc.functions['EXP'])
        notation.push('(')
        notation.push(1)
        notation.push(calc.operators['ADD'])
        notation.push(2)
        notation.push(calc.operators['MULTIPLY'])
        notation.push(3)
        notation.push(')')
        self.assertEqual(calc.evaluate_notation(
            notation).peek(), calc.output_queue.peek())

    def test_parser(self):
        calc = Calculator()
        expected = Queue()
        expected.push(2)
        expected.push(calc.operators['ADD'])
        expected.push(1)
        expected.push(calc.operators['SUBTRACT'])
        expected.push(3)
        self.assertEqual(calc.parser(
            "2 add 1 subtract 3").peek(), expected.peek())

    def test_calculate_expression(self):
        calc = Calculator()
        self.assertEqual(calc.calculate_expression(
            "exp (1 add 2 multiply 3)"), math.exp(1+2*3))
        self.assertEqual(calc.calculate_expression(
            "((15 divide (7 subtract  (1 add 1))) multiply 3) subtract (2 add (1 add 1))"), 5)


class Function:
    def __init__(self, func):
        self.func = func

    def execute(self, element, debug=False):
        if not isinstance(element, numbers.Number):
            raise TypeError("The element must be a number")
        result = self.func(element)

        if debug:
            print("Function: " + self.func.__name__
                  + "\n{:f} = {:f}\n".format(element, result))

        return result


class Operator:
    def __init__(self, operator, strength):
        self.operator = operator
        self.strength = strength

    def execute(self, element1, element2, debug=False):
        if not isinstance(element1, numbers.Number) or not isinstance(element2, numbers.Number):
            raise TypeError("The element must be a number")
        result = self.operator(element1, element2)

        if debug:
            print("Operator: " + self.operator.__name__
                  + "\n{:f}, {:f} = {:f}\n".format(element1, element2, result))

        return result


class Calculator():
    def __init__(self):
        self.functions = {'EXP': Function(numpy.exp),
                          'LOG': Function(numpy.log),
                          'SIN': Function(numpy.sin),
                          'COS': Function(numpy.cos),
                          'SQRT': Function(numpy.sqrt)}

        self.operators = {'ADD': Operator(numpy.add, 0),
                          'MULTIPLY': Operator(numpy.multiply, 1),
                          'DIVIDE': Operator(numpy.divide, 1),
                          'SUBTRACT': Operator(numpy.subtract, 0)}

        self.output_queue = Queue()

    def evaluate_rpn(self, rpn):
        stack = Stack()
        while not rpn.is_empty():
            item = rpn.pop()
            if isinstance(item, numbers.Number):
                stack.push(item)
            elif isinstance(item, Function):
                stack.push(item.execute(stack.pop()))
            elif isinstance(item, Operator):
                num_2 = stack.pop()
                num_1 = stack.pop()
                stack.push(item.execute(num_1, num_2))
        return stack.pop()

    def evaluate_notation(self, notation):
        op_stack = Stack()
        while not notation.is_empty():
            item = notation.pop()
            if isinstance(item, numbers.Number):
                self.output_queue.push(item)
            elif isinstance(item, Function):
                op_stack.push(item)
            elif item == '(':
                op_stack.push(item)
            elif item == ')':
                while op_stack.peek() != '(':
                    self.output_queue.push(op_stack.pop())
                if op_stack.peek() == '(':
                    op_stack.pop()
                else:
                    self.output_queue.push(op_stack.pop())
            elif isinstance(item, Operator):
                while not op_stack.is_empty():
                    if op_stack.peek() == "(":
                        break
                    if isinstance(op_stack.peek(), Operator):
                        if op_stack.peek().strength < item.strength:
                            break
                    self.output_queue.push(op_stack.pop())
                op_stack.push(item)
        while not op_stack.is_empty():
            self.output_queue.push(op_stack.pop())

        return self.output_queue

    def parser(self, text):
        output = Queue()
        text = text.replace(' ', '').upper()
        func_targets = '|'.join(['^' + func for func in self.functions.keys()])
        op_targets = '|'.join(['^' + op for op in self.operators.keys()])
        while len(text) > 0:

            number = re.search("^[-0123456789.]+", text)
            if number is not None:
                output.push(float(number.group(0)))
                text = text[number.end(0):]

            func = re.search(func_targets, text)
            if func is not None:
                output.push(self.functions[func.group(0)])
                text = text[func.end(0):]

            operator = re.search(op_targets, text)
            if operator is not None:
                output.push(self.operators[operator.group(0)])
                text = text[operator.end(0):]

            parentheses = re.search("^[()]", text)
            if parentheses is not None:
                output.push(parentheses.group(0))
                text = text[parentheses.end(0):]

        return output

    def calculate_expression(self, text):
        return self.evaluate_rpn(self.evaluate_notation(self.parser(text)))


def test():
    print("Testing...")
    unittest.main()

def main():
    calc = Calculator()
    while True:
        try:
            expression = input("Enter expression: ")
            print("The answer is", calc.calculate_expression(expression))
        except KeyboardInterrupt:
            print("\nBye!")
            break

main()