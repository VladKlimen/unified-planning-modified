(define (problem BLOCKS-12-1)
(:domain ma-blocksworld)
(:objects
 r0 r1 r2 r3 - robot
 e l a b f i h g d j k c - block
)
(:shared-data
  ((on ?b - block) - block)
  (ontable ?b - block)
  (clear ?b - block)
  ((holding ?r - robot) - block) - 
(either r0 r1 r3)
)
(:init
 (myAgent r2)
 (= (holding r0) nob)
 (= (holding r1) nob)
 (= (holding r2) nob)
 (= (holding r3) nob)
 (not (clear e))
 (= (on e) j)
 (not (ontable e))
 (not (clear l))
 (= (on l) e)
 (not (ontable l))
 (not (clear a))
 (= (on a) l)
 (not (ontable a))
 (not (clear b))
 (= (on b) a)
 (not (ontable b))
 (not (clear f))
 (= (on f) b)
 (not (ontable f))
 (not (clear i))
 (= (on i) f)
 (not (ontable i))
 (not (clear h))
 (= (on h) i)
 (not (ontable h))
 (not (clear g))
 (= (on g) h)
 (not (ontable g))
 (not (clear d))
 (ontable d)
 (= (on d) nob)
 (not (clear j))
 (ontable j)
 (= (on j) nob)
 (clear k)
 (= (on k) d)
 (not (ontable k))
 (clear c)
 (= (on c) g)
 (not (ontable c))
)
(:global-goal (and
 (= (on j) c)
 (= (on c) e)
 (= (on e) k)
 (= (on k) h)
 (= (on h) a)
 (= (on a) f)
 (= (on f) l)
 (= (on l) g)
 (= (on g) b)
 (= (on b) i)
 (= (on i) d)
)))
