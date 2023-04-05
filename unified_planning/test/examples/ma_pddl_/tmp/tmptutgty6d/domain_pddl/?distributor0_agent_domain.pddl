(define (domain depot-domain)
 (:requirements :factored-privacy :typing)
 (:types
    locatable place ?depot0_agent_type ?distributor0_agent_type ?distributor1_agent_type ?driver0_agent_type ?driver1_agent_type - object
    truck hoist surface - locatable
    crate pallet - surface
 )
 (:predicates
 (at_ ?locatable - locatable ?place - place)
  (on ?crate - crate ?surface - surface)
  (in ?crate - crate ?truck - truck)
  (clear ?surface - surface)
  (:private
   (a_lifting ?agent - distributor0_agent_type ?hoist - hoist ?crate - crate)
   (a_available ?agent - distributor0_agent_type ?hoist - hoist)
   (a_pos ?agent - distributor0_agent_type ?place - place)))
 (:action lift
  :parameters ( ?distributor0_agent - distributor0_agent_type ?p - place ?x - hoist ?y - crate ?z - surface)
  :precondition (and 
   (pos ?distributor0_agent p)
   (at_ ?x ?p)
   (available ?distributor0_agent x)
   (at_ ?y ?p)
   (on ?y ?z)
   (clear ?y)
  )
  :effect (and
   (a_lifting ?? ?x ?y)
   (clear ?z)
   (not (at_ ?y ?p))
   (not (clear ?y))
   (not (a_available ?? ?x))
   (not (on ?y ?z))
))
 (:action drop
  :parameters ( ?distributor0_agent - distributor0_agent_type ?p - place ?x - hoist ?y - crate ?z - surface)
  :precondition (and 
   (pos ?distributor0_agent p)
   (at_ ?x ?p)
   (at_ ?z ?p)
   (clear ?z)
   (lifting ?distributor0_agent x)
  )
  :effect (and
   (a_available ?? ?x)
   (at_ ?y ?p)
   (clear ?y)
   (on ?y ?z)
   (not (a_lifting ?? ?x ?y))
   (not (clear ?z))
))
 (:action load
  :parameters ( ?distributor0_agent - distributor0_agent_type ?p - place ?x - hoist ?y - crate ?z_0 - truck)
  :precondition (and 
   (pos ?distributor0_agent p)
   (at_ ?x ?p)
   (at_ ?z_0 ?p)
   (lifting ?distributor0_agent x)
  )
  :effect (and
   (in ?y ?z_0)
   (a_available ?? ?x)
   (not (a_lifting ?? ?x ?y))
))
 (:action unload
  :parameters ( ?distributor0_agent - distributor0_agent_type ?p - place ?x - hoist ?y - crate ?z_0 - truck)
  :precondition (and 
   (pos ?distributor0_agent p)
   (at_ ?x ?p)
   (at_ ?z_0 ?p)
   (available ?distributor0_agent x)
   (in ?y ?z_0)
  )
  :effect (and
   (a_lifting ?? ?x ?y)
   (not (in ?y ?z_0))
   (not (a_available ?? ?x))
))
)
