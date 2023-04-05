(define (problem depot-problem)
 (:domain depot-domain)
 (:objects
   truck0 truck1 - truck
   depot0_place distributor0_place distributor1_place - place
   hoist0 hoist1 hoist2 - hoist
   crate0 crate1 - crate
   pallet0 pallet1 pallet2 - pallet
   depot0_agent - depot0_agent_type
   distributor0_agent - distributor0_agent_type
   distributor1_agent - distributor1_agent_type
   driver0_agent - driver0_agent_type
   driver1_agent - driver1_agent_type
 )
 (:init
  (a_at_ ? pallet0 depot0_place)
  (a_clear ? crate1)
  (a_at_ ? pallet1 distributor0_place)
  (a_clear ? crate0)
  (a_at_ ? pallet2 distributor1_place)
  (a_clear ? pallet2)
  (a_at_ ? truck0 distributor1_place)
  (a_at_ ? truck1 depot0_place)
  (a_at_ ? hoist0 depot0_place)
  (a_at_ ? hoist1 distributor0_place)
  (a_at_ ? hoist2 distributor1_place)
  (a_at_ ? crate0 distributor0_place)
  (a_on ? crate0 pallet1)
  (a_at_ ? crate1 depot0_place)
  (a_on ? crate1 pallet0)
  (a_pos driver0_agent distributor1_place)
  (a_pos driver1_agent depot0_place)
  (a_pos depot0_agent depot0_place)
  (a_available depot0_agent hoist0)
  (a_available distributor0_agent hoist1)
  (a_available distributor1_agent hoist2)
  (a_pos distributor0_agent distributor0_place)
  (a_pos distributor1_agent distributor1_place)
  (a_driving driver0_agent truck0)
  (a_driving driver1_agent truck1))
 (:goal (and (a_on ? crate0 pallet2) (a_on ? crate1 pallet1)))
)