(define (domain ma_logistic-domain)
 (:requirements :factored-privacy :typing)
 (:types
    object_ ag - object
    truck1_type truck2_type airplane_type - ag
    location city package vehicle - object_
    airport - location
 )
 (:predicates
  (at_ ?object - object_ ?location - location)
  (in ?package - package ?vehicle - vehicle)
  (a_on ?agent - ag ?object - object_)
  (a_pos ?agent - ag ?location - location)
)
 (:action load_airplane
  :parameters ( ?airplane - airplane_type ?loc_0 - airport ?obj - package)
  :precondition (and 
   (at_ ?obj ?loc_0)
   (a_pos ?airplane ?loc_0)
  )
  :effect (and
   (not (at_ ?obj ?loc_0))
   (a_on ?airplane ?obj)
))
 (:action unload_airplane
  :parameters ( ?airplane - airplane_type ?loc_0 - airport ?obj - package)
  :precondition (and 
   (a_on ?airplane ?obj)
   (a_pos ?airplane ?loc_0)
  )
  :effect (and
   (not (a_on ?airplane ?obj))
   (at_ ?obj ?loc_0)
))
 (:action fly_airplane
  :parameters ( ?airplane - airplane_type ?loc_from_0 - airport ?loc_to_0 - airport)
  :precondition (and 
   (a_pos ?airplane ?loc_from_0)
  )
  :effect (and
   (not (a_pos ?airplane ?loc_from_0))
   (a_pos ?airplane ?loc_to_0)
))
)
