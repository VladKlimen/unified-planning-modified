(define (problem p_g-problem)
 (:domain p_g-domain)
 (:objects
   home vision2 - location
   startstate active - stateg
   pouch1 - pouchobj
   scale_a - scale_a_type
 )
 (:init
  (a_statedoor scale_a close20))
 (:goal (and (a_at_ robot_a home) (a_statedoor scale_a open20)))
)