#set page(width: 660pt, height: auto, margin: 24pt, fill: rgb("080c0e"))
#set text(font: "Libertinus Serif", size: 20pt, fill: rgb("f2f4ed"))
#set math.equation(block: true)
#set par(leading: 12pt)

#text(font: "Arial", size: 13pt, fill: rgb("86e1c4"))[01 / ROUTING UNCERTAINTY & RISK]
$ P(n) &= sum_(l in "leaves"(n)) p_l \
  "err"(s) &= 1 - max_l p_l \
  L(s) &= 1 + w_"crit" dot p_"crit" \
  R(s) &= L(s) dot "err"(s) $

#pagebreak()
#text(font: "Arial", size: 13pt, fill: rgb("86e1c4"))[02 / EXPECTED ERROR AFTER EVIDENCE]
$ "err"_"inf" &= sum_(l in.not cal(S)_e) p_l - max_(l in.not cal(S)_e) p_l \
  "err"'(e) &= rho_e dot "err"_"inf" + (1 - rho_e) dot "err"(s) $

#pagebreak()
#text(font: "Arial", size: 13pt, fill: rgb("86e1c4"))[03 / EVIDENCE COST & NET UTILITY]
$ C(e) &= alpha dot T_e + beta dot E_e + gamma dot S_e \
  U(e) &= L(s) dot ("err"(s) - "err"'(e)) - lambda dot C(e) $
