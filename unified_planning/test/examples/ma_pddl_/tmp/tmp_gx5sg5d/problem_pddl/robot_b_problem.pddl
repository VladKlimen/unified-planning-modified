(define (problem pgmulti-problem)
 (:domain pgmulti-domain)
 (:objects
   drawer pouchposedrawer vision2 pickup bin binup scale scalerest scaleout pouchposescale scaleup mark10 mark10rest mark10out mark10up pouchposemark10 - location
   grasping open20 open0 - postureg
   horizontal vertical - modeg
   pouch1 pouch2 pouch3 - pouchobj
   robot_b - robot_b_type
 )
 (:init
  (a_instateg robot_b startState))
 (:goal (and (a_at_ robot_b drawer)))
)