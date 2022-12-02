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


from enum import Enum, auto
from fractions import Fraction
import unified_planning as up
from unified_planning.model import (
    InstantaneousAction,
    DurativeAction,
    FNode,
    Effect,
    Timing,
    Action,
    TimeInterval,
    StartTiming,
    EndTiming,
    SimulatedEffect,
    Problem,
    TemporalState,
    DeltaSimpleTemporalNetwork,
    COWState,
    ROState,
)
from unified_planning.engines.compilers import Grounder, GrounderHelper
from unified_planning.engines.engine import Engine
from unified_planning.engines.sequential_simulator import InstantaneousEvent
from unified_planning.engines.mixins.simulator import Event, SimulatorMixin
from unified_planning.exceptions import UPUsageError
from unified_planning.model.walkers import StateEvaluator
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union, cast


class TemporalEventKind(Enum):
    START_ACTION = auto()
    END_ACTION = auto()
    START_CONDITION = auto()
    END_CONDITION = auto()
    INTERMEDIATE_CONDITION_EFFECT = auto()


class TemporalEvent(InstantaneousEvent):
    """Implements the Event class for the temporal scenario."""

    _class_id = 0

    def __init__(
        self,
        kind: TemporalEventKind,
        timing: Timing,
        timing_included: bool,
        committed_events: Optional[List["TemporalEvent"]],
        conditions: List["up.model.FNode"],
        effects: List["up.model.Effect"],
        simulated_effect: Optional["up.model.SimulatedEffect"] = None,
    ):
        InstantaneousEvent.__init__(self, conditions, effects, simulated_effect)
        self._kind = kind
        self._timing = timing
        self._timing_included = timing_included
        if (
            committed_events is not None
            and self._kind != TemporalEventKind.START_ACTION
        ):
            raise UPUsageError(
                "Committed events make sense only for start action events."
            )
        elif committed_events is None and self._kind == TemporalEventKind.START_ACTION:
            raise UPUsageError(
                "Start action events must have a list for committed events."
            )
        self._committed_events = committed_events
        self._id = TemporalEvent._class_id
        TemporalEvent._class_id += 1

    @property
    def kind(self) -> TemporalEventKind:
        return self._kind

    @property
    def timing(self) -> Timing:
        return self._timing

    @property
    def timing_included(self) -> bool:
        return self._timing_included

    @property
    def committed_events(self) -> Optional[List["TemporalEvent"]]:
        return self._committed_events

    @committed_events.setter
    def committed_events(self, new_value: List["TemporalEvent"]):
        if self._kind != TemporalEventKind.START_ACTION:
            raise UPUsageError(
                "Committed events make sense only for start action events."
            )
        self._committed_events = new_value

    @property
    def id(self) -> int:
        return self._id


class TemporalSimulator(Engine, SimulatorMixin):
    """
    Sequential SimulatorMixin implementation.
    """

    EPSILON = Fraction(1, 1000)

    def __init__(self, problem: "up.model.Problem"):
        Engine.__init__(self)
        SimulatorMixin.__init__(self, problem)
        pk = problem.kind
        assert Grounder.supports(pk)
        assert isinstance(self._problem, up.model.Problem)
        self._grounder = GrounderHelper(problem)
        self._actions = set(self._problem.actions)
        self._se = StateEvaluator(self._problem)
        self._all_events_grounded: bool = False
        self._em = problem.env.expression_manager

    def _is_applicable(
        self, event: Union["Event", Iterable["Event"]], state: "ROState"
    ) -> bool:
        assert self._se is not None
        if not isinstance(state, TemporalState):
            raise UPUsageError(
                f"Temporal Simulator needs a TemporalState instance, but {type(state)} is given!"
            )
        if isinstance(event, Event):
            event = [event]
        for e in event:
            assert isinstance(e, TemporalEvent)
            if (
                len(self.get_unsatisfied_conditions(e, state, early_termination=True))
                == 0
            ):
                return False
            if e.kind != TemporalEventKind.START_ACTION:
                found = any(
                    running_events[0] == e for running_events in state.running_events
                )
                if not found:
                    return False
        new_state = self.apply_unsafe(event, state)
        assert isinstance(new_state, TemporalState)
        if not new_state.stn.check_stn():
            return False
        for condition in state.durative_conditions:
            assert isinstance(condition, FNode)
            if not self._se.evaluate(condition, new_state).bool_constant_value():
                return False
        return True

    def _get_unsatisfied_conditions(
        self, event: "Event", state: "up.model.ROState", early_termination: bool = False
    ) -> List["up.model.FNode"]:
        """
        Returns the list of unsatisfied event conditions evaluated in the given state.
        If the flag `early_termination` is set, the method ends and returns at the first unsatisfied condition.

        :param state: The `State` in which the event conditions are evaluated.
        :param early_termination: Flag deciding if the method ends and returns at the first unsatisfied condition.
        :return: The list of all the event conditions that evaluated to `False` or the list containing the first
            condition evaluated to False if the flag `early_termination` is set.
        """
        # Evaluate every condition and if the condition is False or the condition is not simplified as a
        # boolean constant in the given state, return False. Return True otherwise
        assert self._se is not None
        unsatisfied_conditions = []
        for c in event.conditions:
            evaluated_cond = self._se.evaluate(c, state)
            if (
                not evaluated_cond.is_bool_constant()
                or not evaluated_cond.bool_constant_value()
            ):
                unsatisfied_conditions.append(c)
                if early_termination:
                    break
        return unsatisfied_conditions

    def _apply(
        self, event: Union["Event", Iterable["Event"]], state: "up.model.COWState"
    ) -> Optional["up.model.COWState"]:
        """
        Returns `None` if the event is not applicable in the given state, otherwise returns a new COWState,
        which is a copy of the given state but the applicable effects of the event are applied; therefore
        some fluent values are updated.

        :param state: the state where the event formulas are calculated.
        :param event: the event that has the information about the conditions to check and the effects to apply.
        :return: None if the event is not applicable in the given state, a new COWState with some updated values
            if the event is applicable.
        """
        if not self.is_applicable(event, state):
            return None
        else:
            return self.apply_unsafe(event, state)

    def _apply_unsafe(
        self, event: Union["Event", Iterable["Event"]], state: "COWState"
    ) -> "COWState":
        """
        Returns a new COWState, which is a copy of the given state but the applicable effects of the event are applied; therefore
        some fluent values are updated.
        IMPORTANT NOTE: Assumes that self.is_applicable(state, event) returns True

        :param state: the state where the event formulas are evaluated.
        :param event: the event that has the information about the effects to apply.
        :return: A new COWState with some updated values.
        """
        if not isinstance(state, TemporalState):
            raise UPUsageError("Timed Simulator needs a TemporalState!")
        if isinstance(event, Event):
            event = [event]
        updated_values, red_fluents = self._get_updated_values_and_red_fluents(
            event, state, self._se
        )
        # New State variables
        stn = state.stn.copy_stn()
        running_events = state.running_events[:]
        durative_conditions = state.durative_conditions[:]

        events = iter(event)
        # save first event and add a zero distance between all events to apply in this call.
        try:
            first_ev = next(events)
        except StopIteration:
            raise UPUsageError("The given iterator of events is empty")
        if not isinstance(first_ev, TemporalEvent):
            raise UPUsageError(
                f"The timed simulator needs Temporal Events, {type(first_ev)} was given!"
            )
        self._expand_event(first_ev, stn, running_events, durative_conditions)
        other_ev = next(events, None)
        while other_ev is not None:
            if not isinstance(other_ev, TemporalEvent):
                raise UPUsageError(
                    f"The timed simulator needs Temporal Events, {type(other_ev)} was given!"
                )
            self._expand_event(other_ev, stn, running_events, durative_conditions)
            insert_interval(
                stn, first_ev, other_ev, left_bound=Fraction(0), right_bound=Fraction(0)
            )
            other_ev = next(events, None)
        written_fluents: Set[FNode] = set(updated_values.keys())
        # red_fluents.difference_update(written_fluents) # Might be useful or pointless #TODO
        prev_state = state
        state_father = state._father
        while (red_fluents or written_fluents) and state_father is not None:
            assert isinstance(prev_state, TemporalState)
            assert isinstance(state_father, TemporalState)
            # setup loop variables
            (
                oth_updated_values,
                oth_red_fluents,
            ) = self._get_updated_values_and_red_fluents(
                prev_state.last_events, state_father, self._se
            )
            oth_written_fluents: Set[FNode] = set(oth_updated_values.keys())
            last_event = next(
                iter(prev_state.last_events)
            )  # TODO check if use list instead of sets
            assert isinstance(last_event, TemporalEvent)
            # Case where at least 1 Event writes something, affecting the other Event
            if (
                not red_fluents.isdisjoint(oth_written_fluents)
                or not written_fluents.isdisjoint(oth_red_fluents)
                or not written_fluents.isdisjoint(oth_written_fluents)
            ):
                insert_interval(
                    stn,
                    last_event,
                    first_ev,
                    left_bound=Fraction(0) + type(self).EPSILON,
                )
            # Case where both read same fluents
            elif not red_fluents.isdisjoint(oth_red_fluents):
                insert_interval(stn, last_event, first_ev, left_bound=Fraction(0))

            # Update loop variables for sentinel and next loop.
            red_fluents.difference_update(oth_red_fluents)
            red_fluents.difference_update(oth_written_fluents)
            written_fluents.difference_update(oth_red_fluents)
            written_fluents.difference_update(oth_written_fluents)
            prev_state = state_father
            state_father = state_father._father
        new_state = cast(
            TemporalState,
            state.make_child(
                updated_values, running_events, stn, durative_conditions, set(event)
            ),
        )
        return new_state

    def _get_applicable_events(self, state: "up.model.ROState") -> Iterator["Event"]:
        """
        Returns a view over all the events that are applicable in the given State;
        an Event is considered applicable in a given State, when all the Event condition
        simplify as True when evaluated in the State.

        :param state: The state where the formulas are evaluated.
        :return: an Iterator of applicable Events.
        """
        raise NotImplementedError

    def _get_events(
        self,
        action: "up.model.Action",
        parameters: Union[
            Tuple["up.model.Expression", ...], List["up.model.Expression"]
        ],
        duration: Optional[Fraction] = None,
    ) -> List["Event"]:
        """
        Returns a list containing all the events derived from the given action, grounded with the given parameters.

        :param action: The action containing the information to create the event.
        :param parameters: The parameters needed to ground the action
        :return: the List of Events derived from this action with these parameters.
        """
        # sanity checks
        if duration is None:
            raise UPUsageError(
                "The TemporalSimulator needs a specified duration to give ordered action events."
            )
        if action not in self._actions:
            raise UPUsageError(
                "The action given as parameter does not belong to the problem given to the SequentialSimulator."
            )
        params_exp = tuple(
            self._problem.env.expression_manager.auto_promote(parameters)
        )
        grounded_action = self._grounder.ground_action(action, params_exp)
        event_list = self._get_or_create_events(
            action, params_exp, grounded_action, duration
        )
        return event_list

    def _get_unsatisfied_goals(
        self, state: "up.model.ROState", early_termination: bool = False
    ) -> List["up.model.FNode"]:
        """
        Returns the list of unsatisfied goals evaluated in the given state.
        If the flag "early_termination" is set, the method ends and returns at the first unsatisfied goal.

        :param state: The State in which the problem goals are evaluated.
        :param early_termination: Flag deciding if the method ends and returns at the first unsatisfied goal.
        :return: The list of all the goals that evaluated to False or the list containing the first goal evaluated to False if the flag "early_termination" is set.
        """
        unsatisfied_goals = []
        assert self._se is not None
        for g in cast(up.model.Problem, self._problem).goals:
            g_eval = self._se.evaluate(g, state).bool_constant_value()
            if not g_eval:
                unsatisfied_goals.append(g)
                if early_termination:
                    break
        return unsatisfied_goals

    def _get_initial_state(self) -> "COWState":
        """
        Returns the :class:`~unified_planning.model.TemporalState` instance that represents
        the initial state of the given `problem`.
        """
        # TODO Populate those data structures for initial state
        running_events: List[
            List[Event]
        ] = []  # Add tils as if problem was an action(code refactoring needed)
        stn = (
            DeltaSimpleTemporalNetwork()
        )  # Add all tils with right distance from plan_start!
        durative_conditions: List[
            List[FNode]
        ] = []  # Add durative conditions added from start
        last_events: Set[Event] = set()  # add the plan_start event
        assert isinstance(self._problem, Problem)
        return TemporalState(
            self._problem.initial_values,
            running_events,
            stn,
            durative_conditions,
            last_events,
        )

    @property
    def name(self) -> str:
        return "temporal_simulator"

    @staticmethod
    def supported_kind() -> "up.model.ProblemKind":
        supported_kind = up.model.ProblemKind()
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
        supported_kind.set_simulated_entities("SIMULATED_EFFECTS")
        return supported_kind

    @staticmethod
    def supports(problem_kind):
        return problem_kind <= TemporalSimulator.supported_kind()

    def _get_or_create_events(
        self,
        original_action: "up.model.Action",
        params: Tuple["up.model.FNode", ...],
        grounded_action: Optional["up.model.Action"],
        duration: Fraction,
    ) -> List[Event]:
        """
        Support function that takes the `original Action`, the `parameters` used to ground the `grounded Action` and
        the `grounded Action` itself, and adds the corresponding `List of Events` to this `Simulator`. If the
        corresponding `Events` were already created, the same value is returned and no new `Events` are created.

        :param original_action: The `Action` of the :class:`~unified_planning.model.Problem` grounded with the given `params`.
        :param params: The expressions used to ground the `original_action`.
        :param grounded_action: The grounded action, result of the `original_action` grounded with the given `parameters`.
        :return: The retrieved or created `List of Events` corresponding to the `grounded_action`.
        """
        if isinstance(original_action, up.model.InstantaneousAction):
            assert False, "For now we support only durative actions"
            # TODO here should be enough to call the SequentialSimulator code
        elif isinstance(original_action, up.model.DurativeAction):
            if (
                grounded_action is None
            ):  # The grounded action is meaningless, no event associated
                event_list: List["Event"] = []
            else:
                assert isinstance(grounded_action, DurativeAction)
                event_list = break_durative_action_in_event_list(
                    grounded_action, duration
                )
            return event_list
        else:
            raise NotImplementedError(
                "The TemporalSimulator currently supports only InstantaneousActions and DurativeActions."
            )

    def _expand_event(
        self,
        event: "TemporalEvent",
        stn: DeltaSimpleTemporalNetwork,
        running_events: List[List[Event]],
        durative_conditions: List[List[FNode]],
    ):
        """IMPORTANT NOTE: This function modifies the data structures given as parameters."""
        if event.kind == TemporalEventKind.START_ACTION:
            committed_events: List[Event] = []
            ce = event.committed_events
            assert (
                ce is not None
            ), "Error, start Action event can't have None committed events"
            for committed_event in ce:
                if any(committed_event in el for el in running_events):
                    raise UPUsageError(
                        "START_ACTION event already submitted to ",
                        "the timed_simulator! NOTE that TemporalEvents are unique and only usable once!",
                    )
                committed_events.append(committed_event)
                bound = Fraction(committed_event.timing.delay)
                if (
                    committed_event.kind == TemporalEventKind.START_CONDITION
                    and not committed_event.timing_included
                ):
                    bound += type(self).EPSILON
                elif (
                    committed_event.kind == TemporalEventKind.END_CONDITION
                    and not committed_event.timing_included
                ):
                    bound -= type(self).EPSILON
                insert_interval(
                    stn, event, committed_event, left_bound=bound, right_bound=bound
                )
            running_events.append(committed_events)
        else:
            found = False
            for el in running_events:
                if el[0] == event:
                    el.pop(0)
                    found = True
                    if len(el) == 0:
                        running_events.remove(el)
                    break
            if not found:
                raise UPUsageError(
                    f"event: {event} not found in this state ",
                    "! NOTE that TemporalEvents are unique, only usable once and ",
                    "must be given to the simulator in the same order as they are given!",
                )
            if event.kind == TemporalEventKind.START_CONDITION:
                durative_conditions.append(event.conditions)
            elif event.kind == TemporalEventKind.END_CONDITION:
                conditions_to_remove = event.conditions[:]
                for cl in durative_conditions:
                    cl_indexes_to_remove: List[int] = []
                    for i, cond in enumerate(cl):
                        if cond in conditions_to_remove:
                            conditions_to_remove.remove(cond)
                            cl_indexes_to_remove.insert(0, i)
                    for itr in cl_indexes_to_remove:
                        cl.pop(itr)
                assert (
                    len(conditions_to_remove) == 0
                ), "All conditions should have been added before being removed"
                # Filter out empty lists
                durative_conditions[:] = [x for x in filter(None, durative_conditions)]


def break_durative_action_in_event_list(
    grounded_action: "DurativeAction",
    duration: Fraction,
) -> List[Event]:
    em = grounded_action.env.expression_manager
    point_events_map: Dict[Timing, Set[Union[Effect, FNode]]] = {}
    start_durative_conditions_map: Dict[Tuple[Timing, bool], List[FNode]] = {}
    end_durative_conditions_map: Dict[Tuple[Timing, bool], List[FNode]] = {}

    for t, el in grounded_action.effects.items():
        point_events_map.setdefault(get_timing_from_start(t, duration), set()).update(
            el
        )

    for i, cl in grounded_action.conditions.items():
        assert isinstance(i, TimeInterval)
        lower = get_timing_from_start(i.lower, duration)
        upper = get_timing_from_start(i.upper, duration)
        if lower == upper:  # point conditions
            if not i.is_left_open() and not i.is_right_open():
                point_events_map.setdefault(lower, set()).update(cl)
        elif lower.delay < upper.delay:
            # Empty interval condition is always considered True
            cond = em.And(cl)
            # handle left side
            start_durative_conditions_map.setdefault(
                (lower, i.is_left_open()), []
            ).append(cond)
            # handle right side
            end_durative_conditions_map.setdefault(
                (upper, i.is_right_open()), []
            ).append(cond)

    t_start = StartTiming()
    t_end = get_timing_from_start(EndTiming(), duration)

    # events is a mapping from each timing of the action to the corresponding list of events.
    # after it is populated, it must be ordered for key and it's values returned as a list
    events: Dict[Timing, List[TemporalEvent]] = {}
    start_conditions = None
    start_effects = None
    for t, ecs in point_events_map.items():
        conditions = [c for c in ecs if isinstance(c, FNode)]
        effects = [e for e in ecs if isinstance(e, Effect)]
        if t == t_start:
            assert (
                start_conditions is None and start_effects is None
            ), "Error, multiple StartTiming found."
            start_conditions = conditions
            start_effects = effects
            continue
        elif t == t_end:
            kind = TemporalEventKind.END_ACTION
        else:
            kind = TemporalEventKind.INTERMEDIATE_CONDITION_EFFECT
        event = TemporalEvent(
            kind,
            t,
            True,
            None,
            conditions,
            effects,
            grounded_action.simulated_effects[t],
        )
        events.setdefault(t, []).append(event)

    if start_conditions is None:
        start_conditions = []
        assert start_effects is None
        start_effects = []
    assert start_effects is not None

    if t_end not in events:
        event = TemporalEvent(
            TemporalEventKind.END_ACTION,
            t_end,
            True,
            None,
            [],
            [],
            None,
        )
        events[t_end] = [event]

    for (t, timing_included), cl in start_durative_conditions_map.items():
        event = TemporalEvent(
            TemporalEventKind.START_CONDITION,
            t,
            timing_included,
            [],
            cl,
            [],
            None,
        )
        events.setdefault(t, []).append(event)

    for (t, timing_included), cl in end_durative_conditions_map.items():
        event = TemporalEvent(
            TemporalEventKind.END_CONDITION,
            t,
            timing_included,
            [],
            cl,
            [],
            None,
        )
        events.setdefault(t, []).append(event)
    # reverse t_end so that the END_ACTION event is the last of the list,
    # if some durative conditions at end were included in the cycle above
    events[t_end].reverse()

    ret_list: List[Event] = []
    for ev_list in (
        events[key] for key in sorted(events.keys(), key=lambda t: t.delay)
    ):
        ret_list.extend(ev_list)

    start_event = TemporalEvent(
        TemporalEventKind.START_ACTION,
        t_start,
        True,
        cast(List[TemporalEvent], ret_list)[:],
        start_conditions,
        start_effects,
        grounded_action.simulated_effects[t_start],
    )
    ret_list.insert(0, start_event)
    assert cast(TemporalEvent, ret_list[0]).kind == TemporalEventKind.START_ACTION
    assert cast(TemporalEvent, ret_list[-1]).kind == TemporalEventKind.END_ACTION
    return ret_list


def get_timing_from_start(timing: Timing, action_duration: Fraction) -> Timing:
    res = timing
    if timing.is_from_end():
        res = StartTiming(action_duration - timing.delay)
    if res.delay > action_duration:
        start_or_end = "end" if timing.is_from_end() else "start"
        raise UPUsageError(
            "Error, the given action duration is smaller than a",
            f" delay from the {start_or_end} of the action.",
        )
    return res


def insert_interval(
    stn: DeltaSimpleTemporalNetwork,
    left_event: TemporalEvent,
    right_event: TemporalEvent,
    *,
    left_bound: Optional[Fraction] = None,
    right_bound: Optional[Fraction] = None,
):
    """Important NOTE: This function modifies the given stn!"""
    if left_bound is not None:
        stn.add(left_event, right_event, -left_bound)
    if right_bound is not None:
        stn.add(right_event, left_event, right_bound)
