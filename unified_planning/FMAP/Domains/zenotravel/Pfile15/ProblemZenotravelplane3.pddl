(define (problem ZTRAVEL-5-15)
(:domain zeno-travel)
(:objects
 plane1 plane2 plane3 plane4 plane5 - aircraft
 person1 person2 person3 person4 person5 person6 person7 person8 person9 person10 person11 person12 person13 person14 person15 - person
 city0 city1 city2 city3 city4 city5 city6 city7 city8 city9 city10 city11 - city
 fl0 fl1 fl2 fl3 fl4 fl5 fl6 - flevel
)
(:shared-data
  ((at ?a - aircraft) - city)
  ((in ?p - person) - (either city aircraft)) - 
(either plane1 plane2 plane4 plane5)
)
(:init
 (myAgent plane3)
 (= (at plane1) city0)
 (= (at plane2) city3)
 (= (at plane3) city2)
 (= (at plane4) city9)
 (= (at plane5) city5)
 (= (fuel-level plane3) fl1)
 (= (in person1) city8)
 (= (in person2) city10)
 (= (in person3) city7)
 (= (in person4) city5)
 (= (in person5) city1)
 (= (in person6) city10)
 (= (in person7) city11)
 (= (in person8) city8)
 (= (in person9) city9)
 (= (in person10) city11)
 (= (in person11) city4)
 (= (in person12) city5)
 (= (in person13) city8)
 (= (in person14) city4)
 (= (in person15) city1)
 (= (next fl0) fl1)
 (= (next fl1) fl2)
 (= (next fl2) fl3)
 (= (next fl3) fl4)
 (= (next fl4) fl5)
 (= (next fl5) fl6)
)
(:global-goal (and
 (= (in person1) city1)
 (= (in person2) city4)
 (= (in person3) city7)
 (= (in person4) city6)
 (= (in person5) city8)
 (= (in person6) city11)
 (= (in person7) city2)
 (= (in person8) city11)
 (= (in person10) city9)
 (= (in person11) city6)
 (= (in person12) city4)
 (= (in person13) city11)
 (= (in person14) city4)
 (= (in person15) city6)
)))
