(define (domain pddl-domain)
(:requirements :strips :typing :negative-preconditions)
(:types surface place hoist agent - object
        truck - agent
        depot distributor - (either place agent)
        crate pallet - surface
)
(:predicates 
  (myAgent ?a - place)
  (clear ?x - (either hoist surface)))
(:functions
  (located ?h - hoist) - place
  (at ?t - truck) - place
  (placed ?p - pallet) - place
  (pos ?c - crate) - (either place truck)
  (on ?c - crate) - (either hoist truck surface)
)
(:action LiftP
 :parameters ( ?h - hoist ?c - crate ?z - pallet ?p - place)
 :precondition (and (myAgent ?p) (= (located ?h) ?p) (= (placed ?z) ?p) (clear ?h) (= (pos ?c) ?p) (= (on ?c) ?z) (clear ?c))
 :effect (and (assign (on ?c) ?h) (not (clear ?c)) (not (clear ?h)) (clear ?z)))
(:action LiftC
 :parameters ( ?h - hoist ?c - crate ?z - crate ?p - place)
 :precondition (and (myAgent ?p) (= (located ?h) ?p) (= (pos ?z) ?p) (clear ?h) (= (pos ?c) ?p) (= (on ?c) ?z) (clear ?c))
 :effect (and (assign (on ?c) ?h) (not (clear ?c)) (not (clear ?h)) (clear ?z)))
(:action DropP
 :parameters ( ?h - hoist ?c - crate ?z - pallet ?p - place)
 :precondition (and (myAgent ?p) (= (located ?h) ?p) (= (placed ?z) ?p) (clear ?z) (= (on ?c) ?h) (not (clear ?c)) (not (clear ?h)))
 :effect (and (clear ?h) (clear ?c) (not (clear ?z)) (assign (on ?c) ?z)))
(:action DropC
 :parameters ( ?h - hoist ?c - crate ?z - crate ?p - place)
 :precondition (and (myAgent ?p) (= (located ?h) ?p) (= (pos ?z) ?p) (clear ?z) (= (on ?c) ?h) (not (clear ?c)) (not (clear ?h)))
 :effect (and (clear ?h) (clear ?c) (not (clear ?z)) (assign (on ?c) ?z)))
)
