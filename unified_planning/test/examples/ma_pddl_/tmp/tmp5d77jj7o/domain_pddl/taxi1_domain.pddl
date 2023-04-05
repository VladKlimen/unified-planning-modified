(define (domain ma_taxi-domain)
 (:requirements :factored-privacy :typing)
 (:types location taxi ag - object
    person1_type person2_type taxi1_type taxi2_type - ag
 )
 (:predicates
  (free ?location - location)
  (directly_connected ?l1 - location ?l2 - location)
  (at_ ?taxi - taxi ?location - location)
  (empty ?taxi - taxi)
  (:private
   (a_pos ?agent - taxi1_type ?location - location)
   (a_in ?agent - taxi1_type ?taxi - taxi)
   (a_driving ?agent - taxi1_type ?taxi - taxi)))
 (:action drive_t
  :parameters ( ?taxi1 - taxi1_type ?t - taxi ?from_ - location ?to - location)
  :precondition (and 
   (a_driving ?taxi1 ?t)
   (at_ ?t ?from_)
   (directly_connected ?from_ ?to)
   (free ?to)
  )
  :effect (and
   (not (at_ ?t ?from_))
   (not (free ?to))
   (at_ ?t ?to)
   (free ?from_)
))
)
