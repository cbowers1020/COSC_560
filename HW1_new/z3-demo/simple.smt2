; Basic Boolean example
;(set-option :print-success false)
(set-logic QF_UF)
(declare-const p Bool)
(declare-const q Bool)

(assert (and p (not q))) 
(check-sat)

(get-value (q))
(exit)
