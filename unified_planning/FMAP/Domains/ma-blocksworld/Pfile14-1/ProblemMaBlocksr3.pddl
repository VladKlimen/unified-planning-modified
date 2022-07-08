(define (problem BLOCKS-14-1)
(:domain ma-blocksworld)
(:objects
 r0 r1 r2 r3 - robot
 k a f l d b m e j n h i c g - block
)
(:shared-data
  ((on ?b - block) - block)
  (ontable ?b - block)
  (clear ?b - block)
  ((holding ?r - robot) - block) - 
(either r0 r1 r2)
)
(:init
 (myAgent r3)
 (= (holding r0) nob)
 (= (holding r1) nob)
 (= (holding r2) nob)
 (= (holding r3) nob)
 (not (clear k))
 (= (on k) b)
 (not (ontable k))
 (not (clear a))
 (= (on a) k)
 (not (ontable a))
 (not (clear f))
 (= (on f) a)
 (not (ontable f))
 (not (clear l))
 (= (on l) m)
 (not (ontable l))
 (not (clear d))
 (= (on d) l)
 (not (ontable d))
 (not (clear b))
 (ontable b)
 (= (on b) nob)
 (not (clear m))
 (ontable m)
 (= (on m) nob)
 (not (clear e))
 (ontable e)
 (= (on e) nob)
 (not (clear j))
 (ontable j)
 (= (on j) nob)
 (clear n)
 (ontable n)
 (= (on n) nob)
 (clear h)
 (= (on h) f)
 (not (ontable h))
 (clear i)
 (= (on i) d)
 (not (ontable i))
 (clear c)
 (= (on c) e)
 (not (ontable c))
 (clear g)
 (= (on g) j)
 (not (ontable g))
)
(:global-goal (and
 (= (on j) d)
 (= (on d) b)
 (= (on b) h)
 (= (on h) m)
 (= (on m) k)
 (= (on k) f)
 (= (on f) g)
 (= (on g) a)
 (= (on a) i)
 (= (on i) e)
 (= (on e) l)
 (= (on l) n)
 (= (on n) c)
)))
