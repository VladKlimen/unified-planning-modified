(define (problem wood-prob)
(:domain woodworking)
(:objects
 agPlanner agGrinder agVarnisher agSaw - agent
 grinder0 - grinder
 glazer0 - glazer
 immersion-varnisher0 - immersion-varnisher
 planer0 - planer
 highspeed-saw0 - highspeed-saw
 spray-varnisher0 - spray-varnisher
 saw0 - saw
 blue mauve white - acolour
 pine oak - awood
 p0 p1 p2 p3 - part
 b0 b1 - board
 s0 s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 - aboardsize
)
(:shared-data
 (unused ?obj - part) (available ?obj - woodobj)
 (empty ?m - highspeed-saw) (is-smooth ?surface - surface)
 (has-colour ?machine - machine ?colour - acolour)
 ((surface-condition ?obj - woodobj) - surface)
 ((treatment ?obj - part) - treatmentstatus)
 ((colour ?obj - part) - acolour)
 ((wood ?obj - woodobj) - awood)
 ((boardsize ?board - board) - aboardsize)
 ((goalsize ?part - part) - apartsize)
 ((boardsize-successor ?size1 - aboardsize) - aboardsize)
 ((in-highspeed-saw ?m - highspeed-saw) - board)
 ((grind-treatment-change ?old - treatmentstatus) - treatmentstatus)
 - (either agGrinder agVarnisher agSaw))
(:init
 (= (colour p0) natural)
 (unused p0)
 (= (goalsize p0) medium)
 (not (available p0))
 (= (wood p0) unknown-wood)
 (= (surface-condition p0) smooth)
 (= (treatment p0) untreated)
 (= (colour p1) natural)
 (unused p1)
 (= (goalsize p1) large)
 (not (available p1))
 (= (wood p1) unknown-wood)
 (= (surface-condition p1) smooth)
 (= (treatment p1) untreated)
 (= (colour p2) natural)
 (unused p2)
 (= (goalsize p2) large)
 (not (available p2))
 (= (wood p2) unknown-wood)
 (= (surface-condition p2) smooth)
 (= (treatment p2) untreated)
 (= (colour p3) natural)
 (unused p3)
 (= (goalsize p3) medium)
 (not (available p3))
 (= (wood p3) unknown-wood)
 (= (surface-condition p3) smooth)
 (= (treatment p3) untreated)
 (= (grind-treatment-change varnished) colourfragments)
 (= (grind-treatment-change glazed) untreated)
 (= (grind-treatment-change untreated) untreated)
 (= (grind-treatment-change colourfragments) untreated)
 (is-smooth verysmooth)
 (is-smooth smooth)
 (not (is-smooth rough))
 (= (boardsize-successor s0) s1)
 (= (boardsize-successor s1) s2)
 (= (boardsize-successor s2) s3)
 (= (boardsize-successor s3) s4)
 (= (boardsize-successor s4) s5)
 (= (boardsize-successor s5) s6)
 (= (boardsize-successor s6) s7)
 (= (boardsize-successor s7) s8)
 (= (boardsize-successor s8) s9)
 (= (boardsize-successor s9) s10)
 (not (has-colour grinder0 natural))
 (not (has-colour grinder0 blue))
 (not (has-colour grinder0 mauve))
 (not (has-colour grinder0 white))
 (not (has-colour glazer0 natural))
 (has-colour glazer0 blue)
 (has-colour glazer0 mauve)
 (has-colour glazer0 white)
 (not (has-colour immersion-varnisher0 natural))
 (has-colour immersion-varnisher0 blue)
 (has-colour immersion-varnisher0 mauve)
 (not (has-colour immersion-varnisher0 white))
 (not (has-colour planer0 natural))
 (not (has-colour planer0 blue))
 (not (has-colour planer0 mauve))
 (not (has-colour planer0 white))
 (not (has-colour highspeed-saw0 natural))
 (not (has-colour highspeed-saw0 blue))
 (not (has-colour highspeed-saw0 mauve))
 (not (has-colour highspeed-saw0 white))
 (not (has-colour spray-varnisher0 natural))
 (has-colour spray-varnisher0 blue)
 (has-colour spray-varnisher0 mauve)
 (not (has-colour spray-varnisher0 white))
 (not (has-colour saw0 natural))
 (not (has-colour saw0 blue))
 (not (has-colour saw0 mauve))
 (not (has-colour saw0 white))
 (= (in-highspeed-saw highspeed-saw0) no-board)
 (= (boardsize b0) s10)
 (= (wood b0) oak)
 (= (surface-condition b0) rough)
 (available b0)
 (= (boardsize b1) s3)
 (= (wood b1) pine)
 (= (surface-condition b1) rough)
 (available b1)
)
(:global-goal (and
 (available p0)
 (= (colour p0) mauve)
 (= (surface-condition p0) smooth)
 (available p1)
 (= (colour p1) blue)
 (= (surface-condition p1) smooth)
 (available p2)
 (= (colour p2) white)
 (= (wood p2) oak)
 (= (surface-condition p2) smooth)
 (= (treatment p2) glazed)
 (available p3)
 (= (colour p3) mauve)
 (= (wood p3) pine)
 (= (treatment p3) glazed)
))
)
