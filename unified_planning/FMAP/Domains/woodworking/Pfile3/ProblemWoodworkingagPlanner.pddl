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
 mauve white black blue - acolour
 pine oak - awood
 p0 p1 p2 p3 p4 - part
 b0 b1 - board
 s0 s1 s2 s3 s4 s5 s6 - aboardsize
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
 (= (colour p0) blue)
 (unused p0)
 (= (goalsize p0) medium)
 (available p0)
 (= (wood p0) pine)
 (= (surface-condition p0) verysmooth)
 (= (treatment p0) glazed)
 (= (colour p1) natural)
 (unused p1)
 (= (goalsize p1) small)
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
 (= (goalsize p3) small)
 (not (available p3))
 (= (wood p3) unknown-wood)
 (= (surface-condition p3) smooth)
 (= (treatment p3) untreated)
 (= (colour p4) natural)
 (unused p4)
 (= (goalsize p4) small)
 (not (available p4))
 (= (wood p4) unknown-wood)
 (= (surface-condition p4) smooth)
 (= (treatment p4) untreated)
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
 (not (has-colour grinder0 natural))
 (not (has-colour grinder0 mauve))
 (not (has-colour grinder0 white))
 (not (has-colour grinder0 black))
 (not (has-colour grinder0 blue))
 (not (has-colour glazer0 natural))
 (not (has-colour glazer0 mauve))
 (has-colour glazer0 white)
 (has-colour glazer0 black)
 (has-colour glazer0 blue)
 (not (has-colour immersion-varnisher0 natural))
 (not (has-colour immersion-varnisher0 mauve))
 (not (has-colour immersion-varnisher0 white))
 (has-colour immersion-varnisher0 black)
 (not (has-colour immersion-varnisher0 blue))
 (not (has-colour planer0 natural))
 (not (has-colour planer0 mauve))
 (not (has-colour planer0 white))
 (not (has-colour planer0 black))
 (not (has-colour planer0 blue))
 (not (has-colour highspeed-saw0 natural))
 (not (has-colour highspeed-saw0 mauve))
 (not (has-colour highspeed-saw0 white))
 (not (has-colour highspeed-saw0 black))
 (not (has-colour highspeed-saw0 blue))
 (not (has-colour spray-varnisher0 natural))
 (not (has-colour spray-varnisher0 mauve))
 (not (has-colour spray-varnisher0 white))
 (has-colour spray-varnisher0 black)
 (not (has-colour spray-varnisher0 blue))
 (not (has-colour saw0 natural))
 (not (has-colour saw0 mauve))
 (not (has-colour saw0 white))
 (not (has-colour saw0 black))
 (not (has-colour saw0 blue))
 (= (in-highspeed-saw highspeed-saw0) no-board)
 (= (boardsize b0) s6)
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
 (= (colour p0) white)
 (= (treatment p0) glazed)
 (available p1)
 (= (wood p1) pine)
 (= (treatment p1) varnished)
 (available p2)
 (= (colour p2) blue)
 (= (surface-condition p2) verysmooth)
 (= (treatment p2) glazed)
 (available p3)
 (= (colour p3) black)
 (= (surface-condition p3) verysmooth)
 (available p4)
 (= (surface-condition p4) verysmooth)
 (= (treatment p4) varnished)
))
)
