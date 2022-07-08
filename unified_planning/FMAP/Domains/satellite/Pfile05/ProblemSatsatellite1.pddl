(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
 satellite0 satellite1 satellite2 - satellite
 instrument0 instrument1 instrument2 instrument3 instrument4 instrument5 instrument6 instrument7 instrument8 - instrument
 thermograph0 image2 spectrograph1 - mode
 groundstation2 groundstation1 groundstation0 star3 star4 phenomenon5 phenomenon6 star7 phenomenon8 planet9 - direction
)
(:shared-data
  ((pointing ?s - satellite) - direction)
  (have_image ?d - direction ?m - mode) - (either satellite0 satellite2)
)
(:init (mySatellite satellite1)
 (power_avail satellite1)
 (not (power_on instrument0))
 (not (calibrated instrument0))
 (= (calibration_target instrument0) groundstation2)
 (not (power_on instrument1))
 (not (calibrated instrument1))
 (= (calibration_target instrument1) groundstation1)
 (not (power_on instrument2))
 (not (calibrated instrument2))
 (= (calibration_target instrument2) groundstation0)
 (not (power_on instrument3))
 (not (calibrated instrument3))
 (= (calibration_target instrument3) groundstation0)
 (not (power_on instrument4))
 (not (calibrated instrument4))
 (= (calibration_target instrument4) groundstation2)
 (not (power_on instrument5))
 (not (calibrated instrument5))
 (= (calibration_target instrument5) groundstation1)
 (not (power_on instrument6))
 (not (calibrated instrument6))
 (= (calibration_target instrument6) groundstation1)
 (not (power_on instrument7))
 (not (calibrated instrument7))
 (= (calibration_target instrument7) groundstation1)
 (not (power_on instrument8))
 (not (calibrated instrument8))
 (= (calibration_target instrument8) groundstation0)
 (not (have_image star3 thermograph0))
 (not (have_image phenomenon5 image2))
 (not (have_image phenomenon6 image2))
 (not (have_image star7 thermograph0))
 (not (have_image phenomenon8 image2))
 (not (have_image planet9 spectrograph1))
 (= (pointing satellite1) groundstation2)
 (= (on_board satellite1) {instrument3 instrument4 instrument5})
 (not (= (on_board satellite1) {instrument0 instrument1 instrument2 instrument6 instrument7 instrument8}))
 (= (supports instrument0) {thermograph0 image2 spectrograph1})
 (not (= (supports instrument0) {}))
 (= (supports instrument1) {thermograph0 image2 spectrograph1})
 (not (= (supports instrument1) {}))
 (= (supports instrument2) {image2})
 (not (= (supports instrument2) {thermograph0 spectrograph1}))
 (= (supports instrument3) {thermograph0 spectrograph1})
 (not (= (supports instrument3) {image2}))
 (= (supports instrument4) {image2 spectrograph1})
 (not (= (supports instrument4) {thermograph0}))
 (= (supports instrument5) {thermograph0 image2 spectrograph1})
 (not (= (supports instrument5) {}))
 (= (supports instrument6) {image2})
 (not (= (supports instrument6) {thermograph0 spectrograph1}))
 (= (supports instrument7) {thermograph0 image2})
 (not (= (supports instrument7) {spectrograph1}))
 (= (supports instrument8) {thermograph0 image2 spectrograph1})
 (not (= (supports instrument8) {}))
)
(:global-goal (and
 (= (pointing satellite0) phenomenon5)
 (= (pointing satellite1) groundstation2)
 (have_image star3 thermograph0)
 (have_image phenomenon5 image2)
 (have_image phenomenon6 image2)
 (have_image star7 thermograph0)
 (have_image phenomenon8 image2)
 (have_image planet9 spectrograph1)
))
)
