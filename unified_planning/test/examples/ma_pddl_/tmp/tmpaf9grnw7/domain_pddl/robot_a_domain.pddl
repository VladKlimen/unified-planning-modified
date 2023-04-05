(define (domain simple_ma-domain)
 (:requirements :factored-privacy :typing)
 (:types location door ag - object
    robot_a_type scale_a_type - ag
 )
 (:constants
   office home - location
 )
 (:predicates
   (a_open ?agent------ - scale_a_type ?door - door)
  (:private
   (a_pos ?agent - ag ?loc - location)))
 (:action movegripper
  :parameters ( ?robot_a - robot_a_type)
  :precondition (and 
   (a_pos ?robot_a office)
  )
  :effect (and
   (a_pos ?robot_a home)
))
)
