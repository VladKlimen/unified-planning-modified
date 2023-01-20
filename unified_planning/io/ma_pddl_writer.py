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

import os as osy
from fractions import Fraction
import sys
import re

from decimal import Decimal, localcontext
from warnings import warn

import unified_planning as up
import unified_planning.environment
import unified_planning.model.walkers as walkers
from unified_planning.model import (
    InstantaneousAction,
    DurativeAction,
    Fluent,
    Parameter,
    Problem,
    Object,
)
from unified_planning.exceptions import (
    UPTypeError,
    UPProblemDefinitionError,
    UPException,
)
from unified_planning.model.types import _UserType
from typing import Callable, Dict, IO, List, Optional, Set, Union, cast
from io import StringIO
from functools import reduce
from unified_planning.io.pddl_writer import (
    ObjectsExtractor,
    _update_domain_objects,
    ConverterToPDDLString,
    PDDL_KEYWORDS,
    INITIAL_LETTER,
    _get_pddl_name,
)

from unified_planning.model.walkers.simplifier import Simplifier
from unified_planning.model.expression import ExpressionManager
from unified_planning.model.walkers.substituter import Substituter
import re


class ConverterToMAPDDLString(ConverterToPDDLString):
    """Expression converter to a MA-PDDL string."""

    def __init__(
        self,
        env: "up.environment.Environment",
        get_mangled_name: Callable[
            [
                Union[
                    "up.model.Type",
                    "up.model.Action",
                    "up.model.Fluent",
                    "up.model.Object",
                    "up.model.multi_agent.Agent",
                ]
            ],
            str,
        ],
    ):
        ConverterToPDDLString.__init__(self, env, get_mangled_name)

    def walk_dot(self, expression, args):
        agent = expression.agent()
        fluent = expression.args[0].fluent()
        objects = expression.args[0].args
        # f.args[0].fluent(), f.agent().name, f.args[0].args[0]]
        return f'({self.get_mangled_name(fluent)}{" "}{self.get_mangled_name(agent)}{" " if len(args) > 0 else ""}{" ".join([self.convert(obj) for obj in objects])})'


class MAPDDLWriter:
    """This class can be used to write a :class:`~unified_planning.model.MultiAgentProblem` in `MA-PDDL`."""

    def __init__(
        self,
        problem: "up.model.multi_agent.MultiAgentProblem",
        needs_requirements: bool = True,
    ):
        self._env = problem.env
        self.problem = problem
        self.problem_kind = self.problem.kind
        self.needs_requirements = needs_requirements
        # otn represents the old to new renamings
        self.otn_renamings: Dict[
            Union[
                "up.model.Type",
                "up.model.Action",
                "up.model.Fluent",
                "up.model.Object",
                "up.model.Parameter",
                "up.model.Variable",
                "up.model.multi_agent.Agent",
            ],
            str,
        ] = {}
        # nto represents the new to old renamings
        self.nto_renamings: Dict[
            str,
            Union[
                "up.model.Type",
                "up.model.Action",
                "up.model.Fluent",
                "up.model.Object",
                "up.model.Parameter",
                "up.model.Variable",
                "up.model.multi_agent.Agent",
            ],
        ] = {}
        # those 2 maps are "simmetrical", meaning that "(otn[k] == v) implies (nto[v] == k)"
        self.domain_objects: Optional[Dict[_UserType, Set[Object]]] = None
        self.domain_objects_agents: Dict[up.model.multi_agent.Agent, str]
        self.domain_fluents_agents: Dict[up.model.multi_agent.Agent, List[Fluent]]

    def _write_domain(self, out: IO[str]):
        ag_domains = {}
        for ag in self.problem.agents:
            if self.problem_kind.has_intermediate_conditions_and_effects():
                raise UPProblemDefinitionError(
                    "PDDL2.1 does not support ICE.\nICE are Intermediate Conditions and Effects therefore when an Effect (or Condition) are not at StartTIming(0) or EndTIming(0)."
                )
            if (
                self.problem_kind.has_timed_effect()
                or self.problem_kind.has_timed_goals()
            ):
                raise UPProblemDefinitionError(
                    "PDDL2.1 does not support timed effects or timed goals."
                )
            obe = ObjectsExtractor()
            out.write("(define ")
            if self.problem.name is None:
                name = "ma-pddl"
            else:
                name = _get_pddl_name(self.problem)
            out.write(f"(domain {name}-domain)\n")

            if self.needs_requirements:
                out.write(" (:requirements :factored-privacy")
                # out.write(" (:requirements :strips")
                if self.problem_kind.has_flat_typing():
                    out.write(" :typing")
                if self.problem_kind.has_negative_conditions():
                    out.write(" :negative-preconditions")
                if self.problem_kind.has_disjunctive_conditions():
                    out.write(" :disjunctive-preconditions")
                if self.problem_kind.has_equality():
                    out.write(" :equality")
                if (
                    self.problem_kind.has_continuous_numbers()
                    or self.problem_kind.has_discrete_numbers()
                ):
                    out.write(" :numeric-fluents")
                if self.problem_kind.has_conditional_effects():
                    out.write(" :conditional-effects")
                if self.problem_kind.has_existential_conditions():
                    out.write(" :existential-preconditions")
                if self.problem_kind.has_universal_conditions():
                    out.write(" :universal-preconditions")
                if (
                    self.problem_kind.has_continuous_time()
                    or self.problem_kind.has_discrete_time()
                ):
                    out.write(" :durative-actions")
                if self.problem_kind.has_duration_inequalities():
                    out.write(" :duration-inequalities")
                if (
                    self.problem_kind.has_actions_cost()
                    or self.problem_kind.has_plan_length()
                ):
                    out.write(" :action-costs")
                out.write(")\n")

            if self.problem_kind.has_hierarchical_typing():
                user_types_hierarchy = self.problem.user_types_hierarchy
                out.write(f" (:types\n")
                stack: List["unified_planning.model.Type"] = (
                    user_types_hierarchy[None] if None in user_types_hierarchy else []
                )
                out.write(
                    f'    {" ".join(self._get_mangled_name(t) for t in stack)}{" " if len(self.problem.agents) > 0 else ""}{" ".join((ag.name + "_type") for ag in self.problem.agents)} - object\n'
                )
                while stack:
                    current_type = stack.pop()
                    direct_sons: List[
                        "unified_planning.model.Type"
                    ] = user_types_hierarchy[current_type]
                    if direct_sons:
                        stack.extend(direct_sons)
                        out.write(
                            f'    {" ".join([self._get_mangled_name(t) for t in direct_sons])} - {self._get_mangled_name(current_type)}\n'
                        )
                out.write(" )\n")
            else:
                out.write(
                    f' (:types {" ".join([self._get_mangled_name(t) for t in self.problem.user_types])}{" " if len(self.problem.agents) > 0 else ""}{" ".join((ag.name + "_type") for ag in self.problem.agents)})\n'
                    if len(self.problem.user_types) > 0
                    else ""
                )

            if self.domain_objects is None:
                # This method populates the self._domain_objects map
                self._populate_domain_objects(obe, ag)
            assert self.domain_objects is not None

            if len(self.domain_objects) > 0:
                out.write(" (:constants")
                for ut, os in self.domain_objects.items():
                    if len(os) > 0:
                        out.write(
                            f'\n   {" ".join([self._get_mangled_name(o) for o in os])} - {self._get_mangled_name(ut)}'
                        )
            if len(self.domain_objects_agents) > 0:
                for k, v in self.domain_objects_agents.items():
                    if len(v) > 0:
                        out.write(f"\n   {self._get_mangled_name(k)} - {v}")

            if len(self.domain_objects) > 0 or len(self.domain_objects_agents) > 0:
                out.write("\n )\n")

            predicates = []
            functions = []
            for f in self.problem.ma_environment.fluents:
                if f.type.is_bool_type():
                    params = []
                    i = 0
                    for param in f.signature:
                        if param.type.is_user_type():
                            params.append(
                                f" {self._get_mangled_name(param)} - {self._get_mangled_name(param.type)}"
                            )
                            i += 1
                        else:
                            raise UPTypeError(
                                "MA-PDDL supports only user type parameters"
                            )
                    predicates.append(f'({self._get_mangled_name(f)}{"".join(params)})')
                elif f.type.is_int_type() or f.type.is_real_type():
                    params = []
                    i = 0
                    for param in f.signature:
                        if param.type.is_user_type():
                            params.append(
                                f" {self._get_mangled_name(param)} - {self._get_mangled_name(param.type)}"
                            )
                            i += 1
                        else:
                            raise UPTypeError(
                                "MA-PDDL supports only user type parameters"
                            )
                    functions.append(f'({self._get_mangled_name(f)}{"".join(params)})')
                else:
                    raise UPTypeError(
                        "MA-PDDL supports only boolean and numerical fluents"
                    )
            if (
                self.problem.kind.has_actions_cost()
                or self.problem.kind.has_plan_length()
            ):
                functions.append("(total-cost)")

            predicates_dot_agents = []
            functions_dot_agents = []
            # I add the fluents of other agents specified with the DOT as public fluents
            if len(self.domain_fluents_agents) > 0:
                for ag_dot, fleunt_list in self.domain_fluents_agents.items():
                    for f in fleunt_list:
                        if f.type.is_bool_type():
                            params = []
                            i = 0
                            for param in f.signature:
                                if param.type.is_user_type():
                                    params.append(
                                        f" {self._get_mangled_name(param)} - {self._get_mangled_name(param.type)}"
                                    )
                                    i += 1
                                else:
                                    raise UPTypeError(
                                        "MA-PDDL supports only user type parameters"
                                    )
                            predicates_dot_agents.append(
                                f'({self._get_mangled_name(f)} ?agent - {(ag_dot.name)+"_type"}{"".join(params)})'
                            )
                        elif f.type.is_int_type() or f.type.is_real_type():
                            params = []
                            i = 0
                            for param in f.signature:
                                if param.type.is_user_type():
                                    params.append(
                                        f" {self._get_mangled_name(param)} - {self._get_mangled_name(param.type)}"
                                    )
                                    i += 1
                                else:
                                    raise UPTypeError(
                                        "MA-PDDL supports only user type parameters"
                                    )
                            functions_dot_agents.append(
                                f'({self._get_mangled_name(f)} ?agent - {(ag_dot.name)+"_type"}{"".join(params)})'
                            )
                        else:
                            raise UPTypeError(
                                "MA-PDDL supports only boolean and numerical fluents"
                            )

            predicates_agent = []
            functions_agent = []
            for f in ag.fluents:
                if f.type.is_bool_type():
                    params = []
                    i = 0
                    for param in f.signature:
                        if param.type.is_user_type():
                            params.append(
                                f" {self._get_mangled_name(param)} - {self._get_mangled_name(param.type)}"
                            )
                            i += 1
                        else:
                            raise UPTypeError(
                                "MA-PDDL supports only user type parameters"
                            )
                    predicates_agent.append(
                        f'(a_{self._get_mangled_name(f)} ?agent - {(ag.name)+"_type"}{"".join(params)})'
                    )
                elif f.type.is_int_type() or f.type.is_real_type():
                    params = []
                    i = 0
                    for param in f.signature:
                        if param.type.is_user_type():
                            params.append(
                                f" {self._get_mangled_name(param)} - {self._get_mangled_name(param.type)}"
                            )
                            i += 1
                        else:
                            raise UPTypeError(
                                "MA-PDDL supports only user type parameters"
                            )
                    functions_agent.append(
                        f'(a_{self._get_mangled_name(f)} ?agent - {(ag.name)+"_type"}{"".join(params)})'
                    )
                else:
                    raise UPTypeError(
                        "MA-PDDL supports only boolean and numerical fluents"
                    )

            predicates_agent_goal = []
            functions_agent_goal = []
            for g in self.problem.goals:
                if g.is_dot():
                    f = g.args[0].fluent()
                    agent = g.agent()
                    # args = g.args
                    # objects = g.args[0].args
                    if f not in ag.fluents:
                        if f.type.is_bool_type():
                            params = []
                            i = 0
                            for param in f.signature:
                                if param.type.is_user_type():
                                    params.append(
                                        f" {self._get_mangled_name(param)} - {self._get_mangled_name(param.type)}"
                                    )
                                    i += 1
                                else:
                                    raise UPTypeError(
                                        "MA-PDDL supports only user type parameters"
                                    )
                            predicates_agent_goal.append(
                                f'(a_{self._get_mangled_name(f)} ?agent - {(agent.name) + "_type"}{"".join(params)})'
                            )
                        elif f.type.is_int_type() or f.type.is_real_type():
                            params = []
                            i = 0
                            for param in f.signature:
                                if param.type.is_user_type():
                                    params.append(
                                        f" {self._get_mangled_name(param)} - {self._get_mangled_name(param.type)}"
                                    )
                                    i += 1
                                else:
                                    raise UPTypeError(
                                        "MA-PDDL supports only user type parameters"
                                    )
                            functions_agent_goal.append(
                                f'(a_{self._get_mangled_name(f)} ?agent - {(agent.name) + "_type"}{"".join(params)})'
                            )
                        else:
                            raise UPTypeError(
                                "MA-PDDL supports only boolean and numerical fluents"
                            )

            nl = "\n  "
            out.write(
                f" (:predicates\n "
                if len(predicates) > 0
                or len(predicates_agent) > 0
                or len(predicates_dot_agents) > 0
                or len(predicates_agent_goal) > 0
                else ""
            )
            out.write(f"{nl.join(predicates)}\n" if len(predicates) > 0 else "")
            out.write(
                f"  {nl.join(predicates_dot_agents)}\n"
                if len(predicates_dot_agents) > 0
                else ""
            )
            out.write(
                f"{nl.join(predicates_agent_goal)}\n"
                if len(predicates_agent_goal) > 0
                else ""
            )

            nl = "\n   "
            out.write(
                f"  (:private\n   {nl.join(predicates_agent)})"
                if len(predicates_agent) > 0
                else ""
            )
            out.write(
                f")\n"
                if len(predicates) > 0
                or len(predicates_agent) > 0
                or len(predicates_dot_agents) > 0
                or len(predicates_agent_goal) > 0
                else ""
            )

            out.write(
                f" (:functions\n"
                if len(functions) > 0
                or len(functions_dot_agents) > 0
                or len(functions_agent) > 0
                or len(functions_agent_goal) > 0
                else ""
            )
            out.write(f' {" ".join(functions)}\n' if len(functions) > 0 else "")
            out.write(
                f' {" ".join(functions_dot_agents)}\n'
                if len(functions_dot_agents) > 0
                else ""
            )
            out.write(
                f' {" ".join(functions_agent_goal)}\n'
                if len(functions_agent_goal) > 0
                else ""
            )
            out.write(
                f'  (:private{" ".join(functions_agent)})\n'
                if len(functions_agent) > 0
                else ""
            )
            out.write(
                f" )\n"
                if len(functions) > 0
                or len(functions_dot_agents) > 0
                or len(functions_agent) > 0
                or len(functions_agent_goal) > 0
                else ""
            )

            converter = ConverterToMAPDDLString(
                self.problem.env, self._get_mangled_name
            )
            costs: dict = {}
            for a in ag.actions:
                if isinstance(a, up.model.InstantaneousAction):
                    out.write(f" (:action {self._get_mangled_name(a)}")
                    out.write(f"\n  :parameters (")
                    out.write(f' {self._get_mangled_name(ag)} - {(ag.name)+"_type"}')
                    for ap in a.parameters:
                        if ap.type.is_user_type():
                            out.write(
                                f" {self._get_mangled_name(ap)} - {self._get_mangled_name(ap.type)}"
                            )
                        else:
                            raise UPTypeError(
                                "MA-PDDL supports only user type parameters"
                            )
                    out.write(")")
                    if len(a.preconditions) > 0:
                        out.write(f"\n  :precondition (and \n")
                        for p in a.preconditions:

                            if p.is_dot():
                                out.write(f"   {converter.convert(p)}\n")
                            else:
                                p = self.convert_to_dot_exp(p, ag)
                                out.write(
                                    f"   {self.add_agent_prefix(converter.convert(p), ag.fluents)}\n"
                                )
                        out.write(f"  )")

                    if len(a.effects) > 0:
                        out.write("\n  :effect (and\n")
                        for e in a.effects:
                            if e.is_conditional():
                                out.write(f"   (when {converter.convert(e.condition)}")
                            if e.value.is_true():
                                if e.fluent.fluent() in ag.fluents:
                                    out.write(
                                        f'   (a_{self._get_mangled_name(e.fluent.fluent())} ?{ag.name} {" ".join([converter.convert(arg) for arg in e.fluent.args])})\n'
                                    )
                                else:
                                    out.write(f"   {converter.convert(e.fluent)}\n")
                            elif e.value.is_false():
                                if e.fluent.fluent() in ag.fluents:
                                    out.write(
                                        f'   (not (a_{self._get_mangled_name(e.fluent.fluent())} ?{ag.name} {" ".join([converter.convert(arg) for arg in e.fluent.args])}))\n'
                                    )
                                else:
                                    out.write(
                                        f"   (not {converter.convert(e.fluent)})\n"
                                    )
                            elif e.is_increase():
                                if e.fluent.fluent() in ag.fluents:
                                    out.write(
                                        f'   (increase (a_{self._get_mangled_name(e.fluent.fluent())} ?{ag.name} {" ".join([converter.convert(arg) for arg in e.fluent.args])} {converter.convert(e.value)}))\n'
                                    )
                                else:
                                    out.write(
                                        f"   (increase {converter.convert(e.fluent)} {converter.convert(e.value)})\n"
                                    )
                            elif e.is_decrease():
                                if e.fluent.fluent() in ag.fluents:
                                    out.write(
                                        f'   (decrease (a_{self._get_mangled_name(e.fluent.fluent())} ?{ag.name} {" ".join([converter.convert(arg) for arg in e.fluent.args])} {converter.convert(e.value)}))\n'
                                    )
                                else:
                                    out.write(
                                        f"   (decrease {converter.convert(e.fluent)} {converter.convert(e.value)})\n"
                                    )
                            else:
                                if e.fluent.fluent() in ag.fluents:
                                    out.write(
                                        f'   (assign (a_{self._get_mangled_name(e.fluent.fluent())} ?{ag.name} {" ".join([converter.convert(arg) for arg in e.fluent.args])} {converter.convert(e.value)}))\n'
                                    )
                                else:
                                    out.write(
                                        f"   (assign {converter.convert(e.fluent)} {converter.convert(e.value)})\n"
                                    )
                            if e.is_conditional():
                                out.write(f")\n")

                        if a in costs:
                            out.write(
                                f"   (increase (total-cost) {converter.convert(costs[a])})"
                            )
                        out.write(")")
                    out.write(")\n")
                elif isinstance(a, DurativeAction):
                    out.write(f" (:durative-action {self._get_mangled_name(a)}")
                    out.write(f"\n  :parameters (")
                    for ap in a.parameters:
                        if ap.type.is_user_type():
                            out.write(
                                f" {self._get_mangled_name(ap)} - {self._get_mangled_name(ap.type)}"
                            )
                        else:
                            raise UPTypeError(
                                "MA-PDDL supports only user type parameters"
                            )
                    out.write(")")
                    l, r = a.duration.lower, a.duration.upper
                    if l == r:
                        out.write(f"\n  :duration (= ?duration {converter.convert(l)})")
                    else:
                        out.write(f"\n  :duration (and ")
                        if a.duration.is_left_open():
                            out.write(f"(> ?duration {converter.convert(l)})")
                        else:
                            out.write(f"(>= ?duration {converter.convert(l)})")
                        if a.duration.is_right_open():
                            out.write(f"(< ?duration {converter.convert(r)})")
                        else:
                            out.write(f"(<= ?duration {converter.convert(r)})")
                        out.write(")")
                    if len(a.conditions) > 0:
                        out.write(f"\n  :condition (and ")
                        for interval, cl in a.conditions.items():
                            for c in cl:
                                if interval.lower == interval.upper:
                                    if interval.lower.is_from_start():
                                        out.write(f"(at start {converter.convert(c)})")
                                    else:
                                        out.write(f"(at end {converter.convert(c)})")
                                else:
                                    if not interval.is_left_open():
                                        out.write(f"(at start {converter.convert(c)})")
                                    out.write(f"(over all {converter.convert(c)})")
                                    if not interval.is_right_open():
                                        out.write(f"(at end {converter.convert(c)})")
                        out.write(")")
                    if len(a.effects) > 0:
                        out.write("\n  :effect (and")
                        for t, el in a.effects.items():
                            for e in el:
                                if t.is_from_start():
                                    out.write(f" (at start")
                                else:
                                    out.write(f" (at end")
                                if e.is_conditional():
                                    out.write(
                                        f" (when {converter.convert(e.condition)}"
                                    )
                                if e.value.is_true():
                                    out.write(f" {converter.convert(e.fluent)}")
                                elif e.value.is_false():
                                    out.write(f" (not {converter.convert(e.fluent)})")
                                elif e.is_increase():
                                    out.write(
                                        f" (increase {converter.convert(e.fluent)} {converter.convert(e.value)})"
                                    )
                                elif e.is_decrease():
                                    out.write(
                                        f" (decrease {converter.convert(e.fluent)} {converter.convert(e.value)})"
                                    )
                                else:
                                    out.write(
                                        f" (assign {converter.convert(e.fluent)} {converter.convert(e.value)})"
                                    )
                                if e.is_conditional():
                                    out.write(f")")
                                out.write(")")
                        if a in costs:
                            out.write(
                                f" (at end (increase (total-cost) {converter.convert(costs[a])}))"
                            )
                        out.write(")")
                    out.write(")\n")
                else:
                    raise NotImplementedError
            out.write(")\n")
            out.seek(0)
            ag_domain = out.read()
            ag_domains[ag.name] = ag_domain
            out.truncate(0)
            out.seek(0)
            self.domain_objects = None
            self.domain_objects_agents = {}
            self.domain_fluents_agents = {}
        return ag_domains

    def _write_problem(self, out: IO[str]):
        ag_problems = {}
        for ag in self.problem.agents:
            if self.problem.name is None:
                name = "ma-pddl"
            else:
                name = _get_pddl_name(self.problem)
            out.write(f"(define (problem {name}-problem)\n")
            out.write(f" (:domain {name}-domain)\n")
            if self.domain_objects is None:
                # This method populates the self._domain_objects map
                self._populate_domain_objects(ObjectsExtractor(), ag)
            assert self.domain_objects is not None
            if len(self.problem.user_types) > 0:
                out.write(" (:objects")
                for t in self.problem.user_types:
                    constants_of_this_type = self.domain_objects.get(
                        cast(_UserType, t), None
                    )
                    if constants_of_this_type is None:
                        objects = [o for o in self.problem.all_objects if o.type == t]
                    else:
                        objects = [
                            o
                            for o in self.problem.all_objects
                            if o.type == t and o not in constants_of_this_type
                        ]
                    if len(objects) > 0:
                        out.write(
                            f'\n   {" ".join([self._get_mangled_name(o) for o in objects])} - {self._get_mangled_name(t)}'
                        )

            # If agents are not defined as "constant" in the domain, they are defined in the problem
            if len(self.problem.agents) > 0:
                for agent in self.problem.agents:
                    if agent not in self.domain_objects_agents.keys():
                        out.write(f'\n   {agent.name} - {agent.name + "_type"}')
                    else:
                        out.write(f"")

            out.write("\n )\n")
            converter = ConverterToMAPDDLString(
                self.problem.env, self._get_mangled_name
            )
            out.write(" (:init")
            for f, v in self.problem.initial_values.items():
                if v.is_true():
                    if f.is_dot():
                        fluent = f.args[0].fluent()
                        args = f.args
                        # objects = f.args[0].args
                        if f.agent().name == ag.name and fluent in ag.fluents:
                            out.write(
                                f'\n  (a_{self._get_mangled_name(fluent)}{" "}{ag.name}{" " if len(args) > 0 else ""}{" ".join([converter.convert(obj) for obj in f.args[0].args])})'
                            )
                        elif (
                            f.agent().name != ag.name
                            and fluent in self.domain_fluents_agents
                        ):
                            out.write(f"\n  {converter.convert(f)}")
                        else:
                            out.write(f"")
                    else:
                        out.write(f"\n  {converter.convert(f)}")
                elif v.is_false():
                    pass
                else:
                    out.write(f"\n  (= {converter.convert(f)} {converter.convert(v)})")
            if self.problem.kind.has_actions_cost():
                out.write(f" (= (total-cost) 0)")
            out.write(")\n")
            out.write(f" (:goal (and")
            for p in self.problem.goals:
                if p.is_dot():
                    fluent = p.args[0].fluent()
                    args = p.args
                    # objects = p.args[0].args
                    agent = p.agent()
                    out.write(
                        f' (a_{self._get_mangled_name(fluent)}{" "}{agent.name}{" " if len(args) > 0 else ""}{" ".join([converter.convert(obj) for obj in p.args[0].args])})'
                    )
                else:
                    out.write(f" {converter.convert(p)}")
            out.write(f"))")
            out.write("\n)")
            out.seek(0)
            ag_problem = out.read()
            ag_problems[ag.name] = ag_problem
            out.truncate(0)
            out.seek(0)
            self.domain_objects = None
            self.domain_objects_agents = {}
            self.domain_fluents_agents = {}
        return ag_problems

    def print_ma_domain_agent(self, agent_name):
        """Prints to std output the `MA-PDDL` domain."""
        out = StringIO()
        domains = self._write_domain(out)
        domain_agent = domains[agent_name]
        sys.stdout.write(domain_agent)

    def print_ma_problem_agent(self, agent_name):
        """Prints to std output the `MA-PDDL` problem."""
        out = StringIO()
        problems = self._write_problem(out)
        problem_agent = problems[agent_name]
        sys.stdout.write(problem_agent)

    def get_ma_domain(self) -> Dict:
        """Returns the `MA-PDDL` domain."""
        out = StringIO()
        domains = self._write_domain(out)
        return domains

    def get_ma_domain_agent(self, agent_name) -> str:
        """Returns the `MA-PDDL` domain."""
        out = StringIO()
        domains = self._write_domain(out)
        domain_agent = domains[agent_name]
        return domain_agent

    def get_ma_problem(self) -> Dict:
        """Returns the `MA-PDDL` domain."""
        out = StringIO()
        problems = self._write_problem(out)
        return problems

    def get_ma_problem_agent(self, agent_name) -> str:
        """Returns the `MA-PDDL` domain."""
        out = StringIO()
        problems = self._write_problem(out)
        problem_agent = problems[agent_name]
        return problem_agent

    def write_ma_domain(self, directory_name):
        """Dumps to file the `MA-PDDL` domain."""
        out = StringIO()
        domains = self._write_domain(out)
        outdir_ma_pddl = "ma_pddl_" + directory_name
        osy.makedirs(outdir_ma_pddl, exist_ok=True)
        for ag, domain in domains.items():
            path_ma_pddl = osy.path.join(outdir_ma_pddl, ag + "_domain.pddl")
            with open(path_ma_pddl, "w") as f:
                f.write(domain)

    def write_ma_problem(self, directory_name):
        """Dumps to file the `MA-PDDL` domain."""
        out = StringIO()
        problems = self._write_problem(out)
        outdir_ma_pddl = "ma_pddl_" + directory_name
        osy.makedirs(outdir_ma_pddl, exist_ok=True)
        for ag, problem in problems.items():
            path_ma_pddl = osy.path.join(outdir_ma_pddl, ag + "_problem.pddl")
            with open(path_ma_pddl, "w") as f:
                f.write(problem)

    def _get_mangled_name(
        self,
        item: Union[
            "up.model.Type",
            "up.model.Action",
            "up.model.Fluent",
            "up.model.Object",
            "up.model.Parameter",
            "up.model.Variable",
            "up.model.multi_agent.Agent",
        ],
    ) -> str:
        """This function returns a valid and unique MA-PDDL name."""

        # If we already encountered this item, return it
        if item in self.otn_renamings:
            return self.otn_renamings[item]

        if isinstance(item, up.model.Type):
            assert item.is_user_type()
            original_name = cast(_UserType, item).name
            tmp_name = _get_pddl_name(item)
            # If the problem is hierarchical and the name is object, we want to change it
            if self.problem_kind.has_hierarchical_typing() and tmp_name == "object":
                tmp_name = f"{tmp_name}_"
        else:
            original_name = item.name
            tmp_name = _get_pddl_name(item)
        # if the ma-pddl valid name is the same of the original one and it does not create conflicts,
        # it can be returned
        if tmp_name == original_name and tmp_name not in self.nto_renamings:
            new_name = tmp_name
        else:
            count = 0
            new_name = tmp_name
            while self.problem.has_name(new_name) or new_name in self.nto_renamings:
                new_name = f"{tmp_name}_{count}"
                count += 1
        assert (
            new_name not in self.nto_renamings
            and new_name not in self.otn_renamings.values()
        )
        if isinstance(item, up.model.multi_agent.Agent):
            self.otn_renamings[item] = new_name
            self.nto_renamings[new_name] = item
            new_name = f"?{item.name}"

        self.otn_renamings[item] = new_name
        self.nto_renamings[new_name] = item

        return new_name

    def get_item_named(
        self, name: str
    ) -> Union[
        "up.model.Type",
        "up.model.Action",
        "up.model.Fluent",
        "up.model.Object",
        "up.model.Parameter",
        "up.model.Variable",
        "up.model.multi_agent.Agent",
    ]:
        """
        Since `MA-PDDL` has a stricter set of possible naming compared to the `unified_planning`, when writing
        a :class:`~unified_planning.model.Problem` it is possible that some things must be renamed. This is why the `MAPDDLWriter`
        offers this method, that takes a `MA-PDDL` name and returns the original `unified_planning` data structure that corresponds
        to the `MA-PDDL` entity with the given name.

        This method takes a name used in the `MA-PDDL` domain or `MA-PDDL` problem generated by this `MAPDDLWriter` and returns the original
        item in the `unified_planning` `Problem`.

        :param name: The name used in the generated `MA-PDDL`.
        :return: The `unified_planning` model entity corresponding to the given name.
        """
        try:
            return self.nto_renamings[name]
        except KeyError:
            raise UPException(f"The name {name} does not correspond to any item.")

    def get_ma_pddl_name(
        self,
        item: Union[
            "up.model.Type",
            "up.model.Action",
            "up.model.Fluent",
            "up.model.Object",
            "up.model.Parameter",
            "up.model.Variable",
        ],
    ) -> str:
        """
        This method takes an item in the :class:`~unified_planning.model.MultiAgentProblem` and returns the chosen name for the same item in the `MA-PDDL` problem
        or `MA-PDDL` domain generated by this `MAPDDLWriter`.

        :param item: The `unified_planning` entity renamed by this `MAPDDLWriter`.
        :return: The `MA-PDDL` name of the given item.
        """
        try:
            return self.otn_renamings[item]
        except KeyError:
            raise UPException(
                f"The item {item} does not correspond to any item renamed."
            )

    def _populate_domain_objects(self, obe: ObjectsExtractor, agent):
        self.domain_objects = {}
        self.domain_objects_agents = {}
        self.domain_fluents_agents = {}
        # Iterate the actions to retrieve domain objects
        import unified_planning.model.walkers as walkers

        for a in agent.actions:
            if isinstance(a, up.model.InstantaneousAction):
                for p in a.preconditions:
                    if p.is_dot():
                        _update_domain_objects_ag(self.domain_objects_agents, p.agent())
                        _update_domain_fluents_ag(
                            self.domain_fluents_agents, p.agent(), p.args[0].fluent()
                        )
                    elif p.args[0].is_dot():
                        _update_domain_objects_ag(
                            self.domain_objects_agents, p.args[0].agent()
                        )
                        _update_domain_fluents_ag(
                            self.domain_fluents_agents,
                            p.args[0].agent(),
                            p.args[0].args[0].fluent(),
                        )
                    _update_domain_objects(self.domain_objects, obe.get(p))
                for e in a.effects:
                    if e.is_conditional():
                        _update_domain_objects(
                            self.domain_objects, obe.get(e.condition)
                        )
                    _update_domain_objects(self.domain_objects, obe.get(e.fluent))
                    _update_domain_objects(self.domain_objects, obe.get(e.value))
            elif isinstance(a, DurativeAction):
                _update_domain_objects(self.domain_objects, obe.get(a.duration.lower))
                _update_domain_objects(self.domain_objects, obe.get(a.duration.upper))
                for interval, cl in a.conditions.items():
                    for c in cl:
                        _update_domain_objects(self.domain_objects, obe.get(c))
                for t, el in a.effects.items():
                    for e in el:
                        if e.is_conditional():
                            _update_domain_objects(
                                self.domain_objects, obe.get(e.condition)
                            )
                        _update_domain_objects(self.domain_objects, obe.get(e.fluent))
                        _update_domain_objects(self.domain_objects, obe.get(e.value))

    def convert_to_dot_exp(self, node, agent):
        # Initialize a simplifier object
        o = Simplifier(self.problem.env)
        # Define a helper function to simplify argument
        def simplify_arg(arg):
            # Simplify the argument
            arg = o.simplify(arg)
            if arg.is_not():
                arg = self.problem.env.expression_manager.Not(arg)
            return arg

        # Initialize an empty list to store simplified arguments
        args_list = []
        # Iterate through all arguments of the node
        for arg in node.args:
            if node.is_fluent_exp():
                # If the fluent is in the agent's fluents
                if node.fluent() in agent.fluents:
                    # Create a new dot expression
                    new_dot_expression = self.problem.env.expression_manager.Dot(
                        agent, node
                    )
                    return new_dot_expression
            elif len(arg.args) > 1:
                # Extend args_list with both sub-arguments simplified
                args_list.extend([simplify_arg(arg.args[0]), simplify_arg(arg.args[1])])
            else:
                # Append arg to args_list after simplify
                args_list.append(simplify_arg(arg))

        # Create a new dot expression from the list of simplified args
        new_dot_expression = self.sub_exp_dot(args_list, agent, node)
        return new_dot_expression

    def sub_exp(self, old_exp, new_exp, expression):
        sub = Substituter(self.problem.env)
        subs_map[old_exp] = new_exp
        new_expresion = sub.substitute(expression, subs_map)
        return new_expresion

    def sub_exp_dot(self, list_old_exp, agent, expression):
        subs_map = {}
        sub = Substituter(self.problem.env)
        for old_exp in list_old_exp:
            if old_exp.fluent() in agent.fluents:
                arg_dot = self.problem.env.expression_manager.Dot(agent, old_exp)
                subs_map[old_exp] = arg_dot
            else:
                return old_exp
        new_expresion = sub.substitute(expression, subs_map)
        return new_expresion

    def add_agent_prefix(self, string, objects_list):
        match = re.search(r"\((\w+)\s\?", string)
        if match:
            found = match.group(1)
        else:
            return string
        for obj in objects_list:
            if obj.name == found:
                return re.sub(r"\((\w+)\s\?", r"(a_\1 ?", string)
        return string


def _update_domain_objects_ag(
    dict_to_update: Dict[up.model.multi_agent.Agent, str],
    agent: up.model.multi_agent.Agent,
) -> None:
    """Small utility method that updated the dict domain_objects_agents."""
    dict_to_update.setdefault(agent, agent.name + "_type")


def _update_domain_fluents_ag(
    dict_to_update: Dict[up.model.multi_agent.Agent, List[Fluent]],
    agent: up.model.multi_agent.Agent,
    fluent: Fluent,
) -> None:
    """Small utility method that updated the dict domain_fluents_agents."""
    dict_to_update.setdefault(agent, [])
    if fluent in dict_to_update[agent]:
        pass
    else:
        dict_to_update[agent].append(fluent)
