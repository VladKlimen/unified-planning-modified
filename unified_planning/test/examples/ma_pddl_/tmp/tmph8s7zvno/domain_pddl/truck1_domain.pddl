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
  (:private
   (a_in_city ?agent - ag ?location - location ?city - city)))
 (:action drive_truck
  :parameters ( ?truck1 - truck1_type ?loc_from - location ?loc_to - location ?city_ - city)
  :precondition (and 
   (a_pos ?truck1 ?loc_from)
   (a_in_city ?truck1 ?loc_from ?city_)
   (a_in_city ?truck1 ?loc_to ?city_)
  )
  :effect (and
   (not (a_pos ?truck1 ?loc_from))
   (a_pos ?truck1 ?loc_to)
))
 (:action unload_truck
  :parameters ( ?truck1 - truck1_type ?obj - package ?loc - location)
  :precondition (and 
   (a_pos ?truck1 ?loc)
   (a_on ?truck1 ?obj)
  )
  :effect (and
   (not (a_on ?truck1 ?obj))
   (at_ ?obj ?loc)
))
 (:action load_truck
  :parameters ( ?truck1 - truck1_type ?loc - location ?obj - package)
  :precondition (and 
   (at_ ?obj ?loc)
   (a_pos ?truck1 ?loc)
  )
  :effect (and
   (not (at_ ?obj ?loc))
   (a_on ?truck1 ?obj)
))
)
