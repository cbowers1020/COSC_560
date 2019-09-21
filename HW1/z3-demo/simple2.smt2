(set-logic QF_LIA)
(declare-const x Int)
(declare-const y Int)

; (2*y) + x = 20
; x - y = 2
(assert (= (+ x (* 2 y)) 20))
(assert (= (- x y) 2))

(check-sat)
(get-value (x y))
;(get-model)
(exit)
