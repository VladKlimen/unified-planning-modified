(define (problem ma_dcrm_p_g-problem)
 (:domain ma_dcrm_p_g-domain)
 (:objects
   vision2 - location
   startstate active - stateg
   pouch1 - pouchobj
   robot_a - robot_a_type
   scale_a - scale_a_type
 )
 (:init
  (a_at_ robot_a office)
  (a_statedoor scale_a close20))
 (:goal (and (ma_dcrm_fake_goal) (a_ma_dcrm_fake_goal_0 ?scale_a)))
)