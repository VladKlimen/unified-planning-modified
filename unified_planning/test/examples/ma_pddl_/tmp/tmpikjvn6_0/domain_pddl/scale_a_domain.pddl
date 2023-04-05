(define (domain simple_ma-domain)
 (:requirements :factored-privacy :typing)
 (:types
    location door ag - object
    robot_a_type scale_a_type - ag
    close20 open20 - door
    office home - location
 )
 (:predicates
   (a_pos ?agent - robot_a_type ?loc - location)
  (:private
   (a_open ?agent - ag ?door - door)))
 (:action open_door
  :parameters ( ?scale_a - scale_a_type ?z - close20 ?w - open20)
  :precondition (and 
   (a_open ?scale_a ?z)
  )
  :effect (and
   (a_open ?scale_a ?w)
))
)
