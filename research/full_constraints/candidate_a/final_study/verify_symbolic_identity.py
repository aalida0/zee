#!/usr/bin/env python3
"""Gauge-invariant square completion, symbolic equality over rational functions."""
import sympy as s
x,y,u,w,t,z,a,b,e,mu,m12,mcs,l1,l2,l3,l4,l5,lc,k1,k2,k12=s.symbols('x y u w t z a b e mu m12 mcs l1 l2 l3 l4 l5 lc k1 k2 k12',real=True,nonzero=True)
l345=l3+l4+l5
m11=m12*b/a-(l1*a*a+l345*b*b)/2
m22=m12*a/b-(l2*b*b+l345*a*a)/2
q=s.Matrix([x,y,u,w,z]);q0=s.Matrix([a*a/2,b*b/2,a*b/2,0,0]);
C=s.Matrix([[l1/2,l3/2,0,0,k1/2],[l3/2,l2/2,0,0,k2/2],[0,0,l4+l5,0,-k12],[0,0,0,l4-l5,0],[k1/2,k2/2,-k12,0,lc]])
J=s.Matrix([[0,s.Rational(1,2),0,0,0],[s.Rational(1,2),0,0,0,0],[0,0,-1,0,0],[0,0,0,-1,0],[0,0,0,0,0]])
V=m11*x+m22*y-2*m12*u+mcs*z+(q.T*C*q)[0]+2*mu*t
V0=V.subs({x:a*a/2,y:b*b/2,u:a*b/2,w:0,z:0,t:0})
n=a*a+b*b; md=n*(m12/(a*b)-(l4+l5)/2); ms=mcs+(k1*a*a+k2*b*b-2*k12*a*b)/2
B=(b*b*x+a*a*y-2*a*b*u)/n
D=x*y-u*u-w*w
rhs=((q-q0).T*(C-e*J)*(q-q0))[0]+e*D+2*mu*t+mu*mu*z/e+(md-e*n/2)*B+(ms-mu*mu/e)*z
assert s.cancel(s.expand(V-V0-rhs))==0
# Full complex-field Gram determinant identity with independent real components.
r=s.symbols('r:8',real=True); h=[r[i]+s.I*r[i+1] for i in range(0,8,2)]
norm=lambda v:s.expand(v*s.conjugate(v))
x1=norm(h[0])+norm(h[1]); y1=norm(h[2])+norm(h[3]); overlap=s.conjugate(h[0])*h[2]+s.conjugate(h[1])*h[3]; det=h[0]*h[3]-h[1]*h[2]
assert s.expand(x1*y1-norm(overlap)-norm(det))==0
print('PASS: exact square completion and complex Gram identity')
