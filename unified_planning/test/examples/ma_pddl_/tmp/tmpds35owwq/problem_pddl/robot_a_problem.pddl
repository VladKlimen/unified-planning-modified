(define (problem simple_ma-problem)
 (:domain simple_ma-domain)
 (:objects
   open20 close20 - door
   robot_a - robot_a_type
   scale_a - scale_a_type
 )
 (:init
  (a_pos robot_a office))
 (:goal (and (a_----------pos ?robot_a home) (a_----------open ?scale_a open20)))
)