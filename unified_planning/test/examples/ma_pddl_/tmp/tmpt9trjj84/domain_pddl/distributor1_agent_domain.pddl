(define (domain depot-domain)
 (:requirements :factored-privacy :typing)
 (:types
    locatable place depot0_agent_type distributor0_agent_type distributor1_agent_type driver0_agent_type driver1_agent_type - object
    truck hoist surface - locatable
    crate pallet - surface
 )
 (:predicates
 (at_ ?locatable - locatable ?place - place)
  (on ?crate - crate ?surface - surface)
  (in ?crate - crate ?truck - truck)
  (clear ?surface - surface)
  (:private
   (a_lifting ?agent - distributor1_agent_type ?hoist - hoist ?crate - crate)
   (a_available ?agent - distributor1_agent_type ?hoist - hoist)
   (a_pos ?agent - distributor1_agent_type ?place - place)))
 (:action lift
  :parameters ( ?distributor1_agent - distributor1_agent_type ?p - place ?x - hoist ?y - crate ?z - surface)
  :precondition (and 
   ('(pos ?distributor1_agent p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(at_ ?x ?p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(available ?distributor1_agent x)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(at_ ?y ?p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(on ?y ?z)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(clear ?y)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
  )
  :effect (and
   (a_lifting ?distributor1_agent ?x ?y)
   (clear ?z)
   (not (at_ ?y ?p))
   (not (clear ?y))
   (not (a_available ?distributor1_agent ?x))
   (not (on ?y ?z))
))
 (:action drop
  :parameters ( ?distributor1_agent - distributor1_agent_type ?p - place ?x - hoist ?y - crate ?z - surface)
  :precondition (and 
   ('(pos ?distributor1_agent p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(at_ ?x ?p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(at_ ?z ?p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(clear ?z)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(lifting ?distributor1_agent x)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
  )
  :effect (and
   (a_available ?distributor1_agent ?x)
   (at_ ?y ?p)
   (clear ?y)
   (on ?y ?z)
   (not (a_lifting ?distributor1_agent ?x ?y))
   (not (clear ?z))
))
 (:action load
  :parameters ( ?distributor1_agent - distributor1_agent_type ?p - place ?x - hoist ?y - crate ?z_0 - truck)
  :precondition (and 
   ('(pos ?distributor1_agent p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(at_ ?x ?p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(at_ ?z_0 ?p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(lifting ?distributor1_agent x)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
  )
  :effect (and
   (in ?y ?z_0)
   (a_available ?distributor1_agent ?x)
   (not (a_lifting ?distributor1_agent ?x ?y))
))
 (:action unload
  :parameters ( ?distributor1_agent - distributor1_agent_type ?p - place ?x - hoist ?y - crate ?z_0 - truck)
  :precondition (and 
   ('(pos ?distributor1_agent p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(at_ ?x ?p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(at_ ?z_0 ?p)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(available ?distributor1_agent x)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
   ('(in ?y ?z_0)', [bool lifting[hoist=hoist - locatable, crate=crate - surface], bool available[hoist=hoist - locatable], bool pos[place=place]])
  )
  :effect (and
   (a_lifting ?distributor1_agent ?x ?y)
   (not (in ?y ?z_0))
   (not (a_available ?distributor1_agent ?x))
))
)
