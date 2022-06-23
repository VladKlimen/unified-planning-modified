# Copyright 2021 AIPlan4EU project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import unified_planning
from unified_planning.shortcuts import *
from unified_planning.test import TestCase


class TestInfixNotation(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def test_infix(self):
        i_1 = FluentExp(Fluent('i_1', IntType()))
        r_1 = FluentExp(Fluent('r_1', RealType()))
        i_2 = FluentExp(Fluent('i_2', IntType()))
        r_2 = FluentExp(Fluent('r_2', RealType()))
        b_1 = FluentExp(Fluent('b_1'))
        b_2 = Fluent('b_2')
        b_3 = FluentExp(Fluent('b_3'))

        expressions: List[Tuple[FNode, FNode]] = [
            (Plus(i_1, i_2)
            , i_1 + i_2),
            (Plus(i_1, 1)
            , i_1 + 1),
            (Plus(2, i_2)
            , 2 + i_2),
            (Plus(r_1, r_2)
            , r_1 + r_2),
            (Plus(r_1, 1)
            , r_1 + 1),
            (Plus(2, r_2)
            , 2 + r_2),
            (Minus(i_1, i_2)
            , i_1 - i_2),
            (Minus(i_1, 1)
            , i_1 - 1),
            (Minus(2, i_2)
            , 2 - i_2),
            (Times(i_1, i_2)
            , i_1 * i_2),
            (Times(i_1, 1)
            , i_1 * 1),
            (Times(2, i_2)
            , 2 * i_2),
            (Div(i_1, i_2)
            , i_1 / i_2),
            (Div(i_1, 1)
            , i_1 / 1),
            (Div(2, i_2)
            , 2 / i_2),
            (Div(i_1, i_2)
            , i_1 // i_2),
            (Div(i_1, 1)
            , i_1 // 1),
            (Div(2, i_2)
            , 2 // i_2),
            (GT(i_1, i_2)
            , i_1 > i_2),
            (GE(i_1, 1)
            , i_1 >= 1),
            (LT(2, i_2)
            , 2 < i_2),
            (LE(i_1, i_2)
            , i_1 <= i_2),
            (Minus(0, i_1)
            , -i_1),
            (Equals(i_1, 1)
            , i_1.Equals(1)),
            (Equals(r_1, r_2)
            , r_1.Equals(r_2)),
            (And(b_1, b_2)
            , b_1.And(b_2)),
            (And([b_1, b_2, b_3])
            , b_1.And([b_2, b_3])),
            (And([b_1, b_2, b_3])
            , b_1.And(b_2, b_3)),
            (Or(b_1, b_2)
            , b_1.Or(b_2)),
            (Or([b_1, b_2, b_3])
            , b_1.Or([b_2, b_3])),
            (Or([b_1, b_2, b_3])
            , b_1.Or(b_2, b_3)),
            (And(Or(b_1, b_2), Not(And(b_1, b_2)))
            , b_1.Xor(b_2)),
            (And(Or(b_1, b_2, b_3), Not(And(b_1, b_2, b_3)))
            , b_1.Xor([b_2, b_3])),
            (And(Or(b_1, b_2, b_3), Not(And(b_1, b_2, b_3)))
            , b_1.Xor(b_2, b_3)),
            (Implies(b_1, b_2)
            , b_1.Implies(b_2)),
            (Iff(b_1, b_2)
            , b_1.Iff(b_2)),
        ]
        for exp, tested_exp in expressions:
            self.assertEqual(exp, tested_exp)