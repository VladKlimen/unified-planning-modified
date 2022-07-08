(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
 satellite0 satellite1 satellite2 satellite3 - satellite
 instrument0 instrument1 instrument2 instrument3 instrument4 instrument5 instrument6 instrument7 - instrument
 image2 image1 image0 image3 - mode
 star3 groundstation2 star1 groundstation4 groundstation0 phenomenon5 star6 star7 planet8 planet9 planet10 planet11 - direction
)
(:shared-data
  ((pointing ?s - satellite) - direction)
  (have_image ?d - direction ?m - mode) - (either satellite0 satellite2 satellite3)
)
(:init (mySatellite satellite1)
 (power_avail satellite1)
 (not (power_on instrument0))
 (not (calibrated instrument0))
 (= (calibration_target instrument0) star1)
 (not (power_on instrument1))
 (not (calibrated instrument1))
 (= (calibration_target instrument1) groundstation0)
 (not (power_on instrument2))
 (not (calibrated instrument2))
 (= (calibration_target instrument2) groundstation2)
 (not (power_on instrument3))
 (not (calibrated instrument3))
 (= (calibration_target instrument3) groundstation4)
 (not (power_on instrument4))
 (not (calibrated instrument4))
 (= (calibration_target instrument4) star1)
 (not (power_on instrument5))
 (not (calibrated instrument5))
 (= (calibration_target instrument5) star1)
 (not (power_on instrument6))
 (not (calibrated instrument6))
 (= (calibration_target instrument6) groundstation4)
 (not (power_on instrument7))
 (not (calibrated instrument7))
 (= (calibration_target instrument7) groundstation0)
 (not (have_image phenomenon5 image0))
 (not (have_image star6 image1))
 (not (have_image star7 image0))
 (not (have_image planet8 image0))
 (not (have_image planet9 image3))
 (not (have_image planet10 image0))
 (not (have_image planet11 image2))
 (= (pointing satellite1) groundstation0)
 (= (on_board satellite1) {instrument3})
 (not (= (on_board satellite1) {instrument0 instrument1 instrument2 instrument4 instrument5 instrument6 instrument7}))
 (= (supports instrument0) {image1 image3})
 (not (= (supports instrument0) {image2 image0}))
 (= (supports instrument1) {image3})
 (not (= (supports instrument1) {image2 image1 image0}))
 (= (supports instrument2) {image0})
 (not (= (supports instrument2) {image2 image1 image3}))
 (= (supports instrument3) {image2 image0})
 (not (= (supports instrument3) {image1 image3}))
 (= (supports instrument4) {image1 image0})
 (not (= (supports instrument4) {image2 image3}))
 (= (supports instrument5) {image2 image1 image0})
 (not (= (supports instrument5) {image3}))
 (= (supports instrument6) {image2 image1 image0})
 (not (= (supports instrument6) {image3}))
 (= (supports instrument7) {image1 image0 image3})
 (not (= (supports instrument7) {image2}))
)
(:global-goal (and
 (= (pointing satellite1) star1)
 (= (pointing satellite2) phenomenon5)
 (have_image phenomenon5 image0)
 (have_image star6 image1)
 (have_image star7 image0)
 (have_image planet8 image0)
 (have_image planet9 image3)
 (have_image planet10 image0)
 (have_image planet11 image2)
))
)
