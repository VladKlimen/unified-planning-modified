(define (problem ZTRAVEL-5-10)
(:domain zeno-travel)
(:objects
 plane1 plane2 plane3 plane4 plane5 - aircraft
 person1 person2 person3 person4 person5 person6 person7 person8 person9 person10 - person
 city0 city1 city2 city3 city4 city5 city6 city7 city8 city9 - city
 fl0 fl1 fl2 fl3 fl4 fl5 fl6 - flevel
)
(:shared-data
  ((at ?a - aircraft) - city)
  ((in ?p - person) - (either city aircraft)) - 
(either plane1 plane3 plane4 plane5)
)
(:init
 (myAgent plane2)
 (= (at plane1) city5)
 (= (at plane2) city2)
 (= (at plane3) city4)
 (= (at plane4) city8)
 (= (at plane5) city9)
 (= (fuel-level plane2) fl6)
 (= (in person1) city9)
 (= (in person2) city1)
 (= (in person3) city0)
 (= (in person4) city9)
 (= (in person5) city6)
 (= (in person6) city0)
 (= (in person7) city7)
 (= (in person8) city6)
 (= (in person9) city4)
 (= (in person10) city7)
 (= (next fl0) fl1)
 (= (next fl1) fl2)
 (= (next fl2) fl3)
 (= (next fl3) fl4)
 (= (next fl4) fl5)
 (= (next fl5) fl6)
)
(:global-goal (and
 (= (at plane2) city3)
 (= (at plane4) city5)
 (= (at plane5) city8)
 (= (in person2) city8)
 (= (in person3) city2)
 (= (in person4) city7)
 (= (in person5) city1)
 (= (in person6) city6)
 (= (in person7) city5)
 (= (in person8) city1)
 (= (in person9) city5)
 (= (in person10) city9)
)))
