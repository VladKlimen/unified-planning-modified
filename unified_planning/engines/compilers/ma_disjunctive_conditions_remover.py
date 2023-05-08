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
"""This module defines the dnf remover class."""

import unified_planning as up
import unified_planning.engines as engines
from unified_planning.engines.mixins.compiler import CompilationKind, CompilerMixin
from unified_planning.engines.compilers.utils import get_fresh_name, replace_action
from unified_planning.engines.results import CompilerResult
from unified_planning.exceptions import UPProblemDefinitionError
from unified_planning.model import (
    FNode,
    Problem,
    InstantaneousAction,
    DurativeAction,
    TimeInterval,
    Timing,
    Action,
    ProblemKind,
    Oversubscription,
)
from unified_planning.model.walkers import Dnf
from typing import List, Optional, Tuple, Dict, cast
from itertools import product
from functools import partial
from unified_planning.engines.compilers.disjunctive_conditions_remover import (
    DisjunctiveConditionsRemover,
)
from unified_planning.model.multi_agent.ma_problem import MultiAgentProblem
from unified_planning.model.multi_agent.agent import Agent
from typing import Dict, Iterable, List, Optional, Tuple, cast


class MA_DisjunctiveConditionsRemover(DisjunctiveConditionsRemover):
    """
    DisjunctiveConditions remover class: this class offers the capability
    to transform a :class:`~unified_planning.model.multi_agent.MultiAgentProblem` with `MA_DisjunctiveConditions` into a semantically equivalent `MultiAgentProblem`
    where the :class:`Actions <unified_planning.model.Action>` `conditions <unified_planning.model.InstantaneousAction.preconditions>` don't contain the `Or` operand.

    This is done by taking all the `Actions conditions` that are not in the `DNF` form (an `OR` of `ANDs`) and calculate the equivalent `DNF`.
    Then, the resulting `OR` is decomposed into multiple `subActions`; every `subAction` has the same :func:`Effects <unified_planning.model.InstantaneousAction.effects>`
    of the original `Action`, and as condition an element of the decomposed `Or`. So, for every element of the `Or`, an `Action` is created.

    For this `Compiler`, only the `MA_DISJUNCTIVE_CONDITIONS_REMOVING` :class:`~unified_planning.engines.CompilationKind` is supported.
    """

    def __init__(self):
        engines.engine.Engine.__init__(self)
        CompilerMixin.__init__(self, CompilationKind.MA_DISJUNCTIVE_CONDITIONS_REMOVING)

    @property
    def name(self):
        return "ma_dcrm"

    @staticmethod
    def supported_kind() -> ProblemKind:
        supported_kind = ProblemKind()
        supported_kind.set_problem_class("ACTION_BASED_MULTI_AGENT")
        supported_kind.set_problem_class("ACTION_BASED")
        supported_kind.set_typing("FLAT_TYPING")
        supported_kind.set_typing("HIERARCHICAL_TYPING")
        supported_kind.set_numbers("CONTINUOUS_NUMBERS")
        supported_kind.set_numbers("DISCRETE_NUMBERS")
        supported_kind.set_problem_type("SIMPLE_NUMERIC_PLANNING")
        supported_kind.set_problem_type("GENERAL_NUMERIC_PLANNING")
        supported_kind.set_fluents_type("NUMERIC_FLUENTS")
        supported_kind.set_fluents_type("OBJECT_FLUENTS")
        supported_kind.set_conditions_kind("NEGATIVE_CONDITIONS")
        supported_kind.set_conditions_kind("DISJUNCTIVE_CONDITIONS")
        supported_kind.set_conditions_kind("EQUALITY")
        supported_kind.set_conditions_kind("EXISTENTIAL_CONDITIONS")
        supported_kind.set_conditions_kind("UNIVERSAL_CONDITIONS")
        supported_kind.set_effects_kind("CONDITIONAL_EFFECTS")
        supported_kind.set_effects_kind("INCREASE_EFFECTS")
        supported_kind.set_effects_kind("DECREASE_EFFECTS")
        supported_kind.set_time("CONTINUOUS_TIME")
        supported_kind.set_time("DISCRETE_TIME")
        supported_kind.set_time("INTERMEDIATE_CONDITIONS_AND_EFFECTS")
        supported_kind.set_time("TIMED_EFFECT")
        supported_kind.set_time("TIMED_GOALS")
        supported_kind.set_time("DURATION_INEQUALITIES")
        supported_kind.set_simulated_entities("SIMULATED_EFFECTS")
        supported_kind.set_quality_metrics("ACTIONS_COST")
        supported_kind.set_quality_metrics("PLAN_LENGTH")
        supported_kind.set_quality_metrics("OVERSUBSCRIPTION")
        supported_kind.set_quality_metrics("MAKESPAN")
        supported_kind.set_quality_metrics("FINAL_VALUE")
        return supported_kind

    @staticmethod
    def supports(problem_kind):
        return problem_kind <= MA_DisjunctiveConditionsRemover.supported_kind()

    @staticmethod
    def supports_compilation(compilation_kind: CompilationKind) -> bool:
        return compilation_kind == CompilationKind.MA_DISJUNCTIVE_CONDITIONS_REMOVING

    @staticmethod
    def resulting_problem_kind(
        problem_kind: ProblemKind, compilation_kind: Optional[CompilationKind] = None
    ) -> ProblemKind:
        new_kind = ProblemKind(problem_kind.features)
        new_kind.unset_conditions_kind("MA_DISJUNCTIVE_CONDITIONS")
        return new_kind

    def _compile(
        self,
        problem: "up.model.AbstractProblem",
        compilation_kind: "up.engines.CompilationKind",
    ) -> CompilerResult:
        """
        Takes an instance of a :class:`~unified_planning.model.multi_agent.MultiAgentProblem` and the `MA_DISJUNCTIVE_CONDITIONS_REMOVING` `~unified_planning.engines.CompilationKind`
        and returns a `CompilerResult` where the `Problem` does not have `Actions` with disjunctive conditions.

        :param problem: The instance of the `MultiAgentProblem` that must be returned without disjunctive conditions.
        :param compilation_kind: The `CompilationKind` that must be applied on the given problem;
            only `MA_DISJUNCTIVE_CONDITIONS_REMOVING` is supported by this compiler
        :return: The resulting `CompilerResult` data structure.
        """

        assert isinstance(problem, MultiAgentProblem)

        env = problem.environment

        new_to_old: Dict[Action, Optional[Action]] = {}
        new_fluents: List["up.model.Fluent"] = []

        new_problem = problem.clone()
        new_problem.name = f"{self.name}_{problem.name}"
        # new_problem.clear_agents()
        new_problem.clear_goals()

        dnf = Dnf(env)
        meaningful_actions: List["up.model.Action"] = []
        for ag in problem.agents:
            new_problem.agent(ag.name).clear_actions()
            new_ag = new_problem.agent(ag.name)
            # new_ag = up.model.multi_agent.Agent(ag.name, problem.clone())
            for a in ag.actions:
                if isinstance(a, InstantaneousAction):
                    new_precond = dnf.get_dnf_expression(
                        env.expression_manager.And(a.preconditions)
                    )
                    if new_precond.is_or():
                        for and_exp in new_precond.args:
                            na = self._create_new_action_with_given_precond(
                                new_problem, and_exp, a, dnf
                            )
                            if na is not None:
                                new_to_old[na] = a
                                new_ag.add_action(na)
                    else:
                        na = self._create_new_action_with_given_precond(
                            new_problem, new_precond, a, dnf
                        )
                        if na is not None:
                            new_to_old[na] = a
                            new_ag.add_action(na)
                elif isinstance(a, DurativeAction):
                    interval_list: List[TimeInterval] = []
                    conditions: List[List[FNode]] = []
                    # save the timing, calculate the dnf of the and of all the conditions at the same time
                    # and then save it in conditions.
                    # conditions contains lists of Fnodes, where [a,b,c] means a or b or c
                    for i, cl in a.conditions.items():
                        interval_list.append(i)
                        new_cond = dnf.get_dnf_expression(
                            env.expression_manager.And(cl)
                        )
                        if new_cond.is_or():
                            conditions.append(new_cond.args)
                        else:
                            conditions.append([new_cond])
                    conditions_tuple = cast(
                        Tuple[List[FNode], ...], product(*conditions)
                    )
                    for cond_list in conditions_tuple:
                        nda = self._create_new_durative_action_with_given_conds_at_given_times(
                            new_ag, interval_list, cond_list, a, dnf
                        )
                        if nda is not None:
                            new_to_old[nda] = a
                            new_ag.add_action(nda)
                else:
                    raise NotImplementedError
            new_problem.add_agent(new_ag)

            # Meaningful action is the list of the actions that modify fluents that are not added
            # just to remove the disjunction from goals
            ag_actions: List["up.model.Action"] = new_ag.actions[:]
            meaningful_actions.extend(ag_actions)

            self._ma_goals_without_disjunctions_adding_new_elements(
                dnf,
                new_problem,
                new_ag,
                new_to_old,
                new_fluents,
                problem.goals,
            )

        # Every meaningful action must set to False every new fluent added.
        # For the DurativeActions this must happen every time the action modifies something
        em = env.expression_manager
        # new_effects is the List of effects that must be added to every meaningful action
        new_effects: List["up.model.Effect"] = [
            up.model.Effect(em.FluentExp(f), em.FALSE(), em.TRUE()) for f in new_fluents
        ]
        for a in meaningful_actions:
            # Since we modify the action that is a key in the Dict, we must update the mapping
            old_action = new_to_old.pop(a)
            if isinstance(a, InstantaneousAction):
                for e in new_effects:
                    a._add_effect_instance(e)
            elif isinstance(a, DurativeAction):
                for tim in a.effects:
                    for e in new_effects:
                        a._add_effect_instance(tim, e)
            else:
                raise NotImplementedError
            new_to_old[a] = old_action

        return CompilerResult(
            new_problem, partial(replace_action, map=new_to_old), self.name
        )

    # "def _ma_goals_without_disjunctions_adding_new_elements" not yet adapted to multi-agent case!
    def _ma_goals_without_disjunctions_adding_new_elements(
        self,
        dnf: Dnf,
        new_problem: "MultiAgentProblem",
        new_agent: "up.model.multi_agent.Agent",
        new_to_old: Dict[Action, Optional[Action]],
        new_fluents: List["up.model.Fluent"],
        goals: List["up.model.FNode"],
        timing: Optional["up.model.timing.TimeInterval"] = None,
    ) -> List["up.model.FNode"]:
        env = new_problem.environment
        # new_goal = dnf.get_dnf_expression(env.expression_manager.And(goals))
        new_goals: List["up.model.FNode"] = []
        for g in goals:
            new_goal = dnf.get_dnf_expression(g)
            if new_goal.is_or():
                new_name = self.name if timing is None else f"{self.name}_timed"
                fake_fluent = up.model.Fluent(
                    self.get_fresh_name(new_problem, f"{new_name}_fake_goal")
                )
                fake_action = InstantaneousAction(f"{new_name}_fake_action", _env=env)
                fake_action.add_effect(fake_fluent, True)
                for and_exp in g.args:
                    na = self._create_new_action_with_given_precond(
                        new_problem, and_exp, fake_action, dnf
                    )
                    if na is not None:
                        new_to_old[na] = None
                        new_agent.add_action(na)
                new_agent.add_fluent(fake_fluent, default_initial_value=False)
                new_fluents.append(fake_fluent)
                if new_goal not in new_problem.goals:
                    new_problem.add_goal(new_goal)
                # return env.expression_manager.FluentExp(fake_fluent)
            else:
                new_goals.append(new_goal)
                if new_goal not in new_problem.goals:
                    new_problem.add_goal(new_goal)
        return new_goals
