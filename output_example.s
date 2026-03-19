.global _start
.text
_start:
    ldr r10, =const_0
    vldr.f64 d0, [r10]
    ldr r10, =const_1
    vldr.f64 d1, [r10]
    vmul.f64 d0, d0, d1
    ldr r10, =mem_VAR
    vldr.f64 d1, [r10]
    vadd.f64 d0, d0, d1
    ldr r10, =res_0
    vstr.f64 d0, [r10]
    b .

.data
res_0: .double 0.0
mem_VAR: .double 0.0
const_0: .double 3.14
const_1: .double 2.0
