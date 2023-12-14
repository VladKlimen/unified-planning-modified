# Copyright 2021-2023 AIPlan4EU project
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


from functools import partial
from typing import Dict, List
import typing
import unified_planning as up
import unified_planning.model.walkers
from unified_planning.io.utils import set_parse_action, set_results_name, Located

import pyparsing
from pyparsing import ParseResults
from pyparsing import CharsNotIn, Empty
from pyparsing import Word, alphanums, alphas, ZeroOrMore, OneOrMore
from pyparsing import Suppress, Group, Optional, Forward

if pyparsing.__version__ < "3.0.0":
    from pyparsing import oneOf as one_of
    from pyparsing import restOfLine as rest_of_line
else:
    from pyparsing import one_of
    from pyparsing import rest_of_line


Object = "object"
TypesMap = Dict[str, unified_planning.model.Type]


def nested_expr():
    """
    A hand-rolled alternative to pyparsing.nested_expr() that substantially improves its performance in our case.
    """
    cnt = Empty() + CharsNotIn("() \n\t\r")
    nested = Forward()
    nested <<= Group(
        Located(
            Suppress("(") + ZeroOrMore(Group(Located(cnt)) | nested) + Suppress(")")
        )
    )
    return nested


def set_unique(grammar: "PDDLGrammar", attribute_name: str, s, loc, toks):

    value = getattr(grammar, attribute_name)
    if value is not None:
        assert isinstance(value, ParseResults)
        raise SyntaxError(
            f"The {attribute_name} in the PDDL file is defined more than once with the string:\n{s}."
        )
    setattr(grammar, attribute_name, toks)


NAME = Word(alphas, alphanums + "_" + "-")
VARIABLE = Suppress("?") + NAME
PARAMETERS = set_results_name(
    ZeroOrMore(
        Group(Located(Group(OneOrMore(VARIABLE)) + Optional(Suppress("-") + NAME)))
    ),
    "params",
)


class PDDLGrammar:
    def __init__(self):
        # Domain data structures to populate while parsing
        self.name: str = ""
        self.requirements: typing.Optional[ParseResults] = None
        self.types: typing.Optional[ParseResults] = None
        self.constants: typing.Optional[ParseResults] = None
        self.predicates: typing.Optional[ParseResults] = None
        self.functions: typing.Optional[ParseResults] = None
        self.tasks: List[ParseResults] = []
        self.methods: List[ParseResults] = []
        self.actions: List[ParseResults] = []

        # Problem data structures to populate while parsing
        self.htn: typing.Optional[ParseResults] = None
        self.problem_requirements: typing.Optional[ParseResults] = None
        self.objects: typing.Optional[ParseResults] = None
        self.init: typing.Optional[ParseResults] = None
        self.goal: typing.Optional[ParseResults] = None
        self.constraints: typing.Optional[ParseResults] = None
        self.metric: typing.Optional[ParseResults] = None

        name = NAME
        variable = VARIABLE

        require_def = (
            Suppress("(")
            + ":requirements"
            + OneOrMore(
                one_of(
                    ":strips :typing :negative-preconditions :disjunctive-preconditions :equality :existential-preconditions :universal-preconditions :quantified-preconditions :conditional-effects :fluents :numeric-fluents :adl :durative-actions :duration-inequalities :timed-initial-literals :action-costs :hierarchy :method-preconditions :constraints :contingent :preferences"
                )
            )
            + Suppress(")")
        )
        domain_require_def = require_def.copy()
        set_parse_action(
            domain_require_def,
            partial(set_unique, self, "requirements"),
        )

        types_def = (
            Suppress("(")
            + Suppress(":types")
            - OneOrMore(Group(Group(OneOrMore(name)) + Optional(Suppress("-") + name)))
            + Suppress(")")
        )
        set_parse_action(types_def, partial(set_unique, self, "types"))

        constants_def = (
            Suppress("(")
            + Suppress(":constants")
            - ZeroOrMore(
                Group(Located(Group(OneOrMore(name)) + Optional(Suppress("-") + name)))
            )
            + Suppress(")")
        )
        set_parse_action(constants_def, partial(set_unique, self, "constants"))

        predicate = (
            Suppress("(")
            + Group(
                name
                + Group(
                    ZeroOrMore(
                        Group(
                            Located(
                                Group(OneOrMore(variable))
                                + Optional(Suppress("-") + name)
                            )
                        )
                    )
                )
            )
            + Suppress(")")
        )

        predicates_def = (
            Suppress("(")
            + Suppress(":predicates")
            - OneOrMore(predicate)
            + Suppress(")")
        )
        set_parse_action(predicates_def, partial(set_unique, self, "predicates"))

        functions_def = (
            Suppress("(")
            + Suppress(":functions")
            - OneOrMore(predicate + Optional(Suppress("- number")))
            + Suppress(")")
        )
        set_parse_action(functions_def, partial(set_unique, self, "functions"))

        parameters = PARAMETERS
        action_def = Group(
            Suppress("(")
            + ":action"
            - set_results_name(name, "name")
            + ":parameters"
            - Suppress("(")
            + parameters
            + Suppress(")")
            + Optional(":precondition" - set_results_name(nested_expr(), "pre"))
            + Optional(":effect" - set_results_name(nested_expr(), "eff"))
            + Optional(":observe" - set_results_name(nested_expr(), "obs"))
            + Suppress(")")
        )
        set_parse_action(action_def, self.actions.append)

        dur_action_def = Group(
            Suppress("(")
            + ":durative-action"
            - set_results_name(name, "name")
            + ":parameters"
            - Suppress("(")
            + parameters
            + Suppress(")")
            + ":duration"
            - set_results_name(nested_expr(), "duration")
            + ":condition"
            - set_results_name(nested_expr(), "cond")
            + ":effect"
            - set_results_name(nested_expr(), "eff")
            + Suppress(")")
        )
        set_parse_action(dur_action_def, self.actions.append)

        task_def = (
            Suppress("(")
            + ":task"
            - set_results_name(name, "name")
            + ":parameters"
            - Suppress("(")
            + parameters
            + Suppress(")")
            + Suppress(")")
        )
        set_parse_action(task_def, self.tasks.append)

        method_def = (
            Suppress("(")
            + ":method"
            - set_results_name(name, "name")
            + ":parameters"
            - Suppress("(")
            + parameters
            + Suppress(")")
            + ":task"
            - set_results_name(nested_expr(), "task")
            + Optional(
                ":precondition" - set_results_name(nested_expr(), "precondition")
            )
            + Optional(
                one_of(":ordered-subtasks :ordered-tasks")
                - set_results_name(nested_expr(), "ordered-subtasks")
            )
            + Optional(
                one_of(":subtasks :tasks") - set_results_name(nested_expr(), "subtasks")
            )
            + Optional(":ordering" - set_results_name(nested_expr(), "ordering"))
            + Optional(":constraints" - set_results_name(nested_expr(), "constraints"))
            + Suppress(")")
        )
        set_parse_action(method_def, self.methods.append)

        domain_stmt = (
            action_def
            | dur_action_def
            | task_def
            | method_def
            | types_def
            | predicates_def
            | functions_def
            | constants_def
            | domain_require_def
        )
        domain = (
            Suppress("(")
            + "define"
            + Suppress("(")
            + "domain"
            + set_results_name(name, "name")
            + Suppress(")")
            + ZeroOrMore(Group(domain_stmt))
            + Suppress(")")
        )

        problem_require_def = require_def.copy()
        set_parse_action(
            problem_require_def,
            partial(set_unique, self, "problem_requirements"),
        )

        objects = ZeroOrMore(
            Group(Group(OneOrMore(name)) + Optional(Suppress("-") + name))
        )
        objects_def = (
            Suppress("(")
            + Suppress(":objects")
            + set_results_name(objects, "objects")
            + Suppress(")")
        )
        set_parse_action(objects_def, partial(set_unique, self, "objects"))

        htn_def = (
            Suppress("(")
            + ":htn"
            - Optional(":parameters" - Suppress("(") + parameters + Suppress(")"))
            + Optional(
                one_of(":ordered-tasks :ordered-subtasks")
                - set_results_name(nested_expr(), "ordered-tasks")
            )
            + Optional(
                one_of(":tasks :subtasks") - set_results_name(nested_expr(), "tasks")
            )
            + Optional(":ordering" - set_results_name(nested_expr(), "ordering"))
            + Optional(":constraints" - set_results_name(nested_expr(), "constraints"))
            + Suppress(")")
        )
        set_parse_action(htn_def, partial(set_unique, self, "htn"))

        init_def = (
            Suppress("(")
            + Suppress(":init")
            + ZeroOrMore(nested_expr())
            + Suppress(")")
        )
        set_parse_action(init_def, partial(set_unique, self, "init"))

        goal_def = Suppress("(") + Suppress(":goal") + nested_expr() + Suppress(")")
        set_parse_action(goal_def, partial(set_unique, self, "goal"))

        constraints_def = (
            Suppress("(")
            + Suppress(":constraints")
            + OneOrMore(nested_expr())
            + Suppress(")")
        )
        set_parse_action(constraints_def, partial(set_unique, self, "constraints"))

        metric = set_results_name(
            one_of(("minimize", "maximize")), "optimization"
        ) + set_results_name((name | nested_expr()), "metric")

        metric_def = Suppress("(") + Suppress(":metric") + metric + Suppress(")")
        set_parse_action(metric_def, partial(set_unique, self, "metric"))

        problem_stmt = (
            problem_require_def
            | goal_def
            | htn_def
            | init_def
            | objects_def
            | constraints_def
            | metric_def
        )

        problem = (
            Suppress("(")
            + "define"
            + Suppress("(")
            + "problem"
            + set_results_name(name, "name")
            + Suppress(")")
            + Suppress("(")
            + ":domain"
            + name
            + Suppress(")")
            + ZeroOrMore(Group(problem_stmt))
            + Suppress(")")
        )

        domain.ignore(";" + rest_of_line)
        problem.ignore(";" + rest_of_line)

        self._domain = domain
        self._problem = problem
        self._parameters = parameters

    @property
    def domain(self):
        return self._domain

    @property
    def problem(self):
        return self._problem

    @property
    def parameters(self):
        return self._parameters
