(define (problem depotprob4534)
(:domain depot)
(:objects
 depot0 depot1 depot2 - depot
 distributor0 distributor1 distributor2 - distributor
 truck0 truck1 - truck
 crate0 crate1 crate2 crate3 crate4 crate5 crate6 crate7 crate8 crate9 crate10 crate11 crate12 crate13 crate14 - crate
 pallet0 pallet1 pallet2 pallet3 pallet4 pallet5 pallet6 pallet7 pallet8 pallet9 - pallet
 hoist0 hoist1 hoist2 hoist3 hoist4 hoist5 - hoist
)
(:shared-data
  (clear ?x - (either surface hoist))
  ((at ?t - truck) - place)
  ((pos ?c - crate) - (either place truck))
  ((on ?c - crate) - (either surface hoist truck)) - 
(either depot1 depot2 distributor0 distributor1 distributor2 truck0 truck1)
)
(:init
 (myAgent depot0)
 (= (pos crate0) distributor2)
 (not (clear crate0))
 (= (on crate0) pallet5)
 (= (pos crate1) distributor1)
 (not (clear crate1))
 (= (on crate1) pallet4)
 (= (pos crate2) depot2)
 (not (clear crate2))
 (= (on crate2) pallet8)
 (= (pos crate3) depot2)
 (not (clear crate3))
 (= (on crate3) crate2)
 (= (pos crate4) depot1)
 (clear crate4)
 (= (on crate4) pallet6)
 (= (pos crate5) distributor2)
 (not (clear crate5))
 (= (on crate5) crate0)
 (= (pos crate6) depot1)
 (not (clear crate6))
 (= (on crate6) pallet1)
 (= (pos crate7) depot1)
 (clear crate7)
 (= (on crate7) crate6)
 (= (pos crate8) distributor0)
 (clear crate8)
 (= (on crate8) pallet3)
 (= (pos crate9) distributor0)
 (clear crate9)
 (= (on crate9) pallet7)
 (= (pos crate10) distributor1)
 (not (clear crate10))
 (= (on crate10) crate1)
 (= (pos crate11) distributor2)
 (clear crate11)
 (= (on crate11) crate5)
 (= (pos crate12) distributor1)
 (clear crate12)
 (= (on crate12) crate10)
 (= (pos crate13) depot2)
 (clear crate13)
 (= (on crate13) crate3)
 (= (pos crate14) distributor0)
 (clear crate14)
 (= (on crate14) pallet9)
 (= (at truck0) distributor1)
 (= (at truck1) distributor2)
 (= (located hoist0) depot0)
 (clear hoist0)
 (= (located hoist1) depot1)
 (clear hoist1)
 (= (located hoist2) depot2)
 (clear hoist2)
 (= (located hoist3) distributor0)
 (clear hoist3)
 (= (located hoist4) distributor1)
 (clear hoist4)
 (= (located hoist5) distributor2)
 (clear hoist5)
 (= (placed pallet0) depot0)
 (clear pallet0)
 (= (placed pallet1) depot1)
 (not (clear pallet1))
 (= (placed pallet2) depot2)
 (clear pallet2)
 (= (placed pallet3) distributor0)
 (not (clear pallet3))
 (= (placed pallet4) distributor1)
 (not (clear pallet4))
 (= (placed pallet5) distributor2)
 (not (clear pallet5))
 (= (placed pallet6) depot1)
 (not (clear pallet6))
 (= (placed pallet7) distributor0)
 (not (clear pallet7))
 (= (placed pallet8) depot2)
 (not (clear pallet8))
 (= (placed pallet9) distributor0)
 (not (clear pallet9))
)
(:global-goal (and
 (= (on crate0) crate8)
 (= (on crate1) crate10)
 (= (on crate2) pallet0)
 (= (on crate3) pallet1)
 (= (on crate4) crate7)
 (= (on crate5) pallet5)
 (= (on crate6) pallet6)
 (= (on crate7) pallet4)
 (= (on crate8) pallet7)
 (= (on crate9) crate4)
 (= (on crate10) crate11)
 (= (on crate11) crate9)
 (= (on crate12) crate5)
 (= (on crate13) pallet8)
 (= (on crate14) pallet9)
))
)
