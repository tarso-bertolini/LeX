.global _start
.text
_start:
    ldr r10, =const_0
    vldr.f64 d0, [r10]
    ldr r10, =const_1
    vldr.f64 d1, [r10]
    vadd.f64 d0, d0, d1
    ldr r10, =res_0
    vstr.f64 d0, [r10]
    ldr r10, =const_2
    vldr.f64 d0, [r10]
    ldr r10, =const_3
    vldr.f64 d1, [r10]
    vsub.f64 d0, d0, d1
    ldr r10, =res_1
    vstr.f64 d0, [r10]
    ldr r10, =const_1
    vldr.f64 d0, [r10]
    ldr r10, =const_4
    vldr.f64 d1, [r10]
    vmul.f64 d0, d0, d1
    ldr r10, =res_2
    vstr.f64 d0, [r10]
    ldr r10, =const_5
    vldr.f64 d0, [r10]
    ldr r10, =const_6
    vldr.f64 d1, [r10]
    vdiv.f64 d0, d0, d1
    ldr r10, =res_3
    vstr.f64 d0, [r10]
    ldr r10, =const_5
    vldr.f64 d0, [r10]
    ldr r10, =const_4
    vldr.f64 d1, [r10]
    vcvtr.s32.f64 s31, d0
    vmov r0, s31
    vcvtr.s32.f64 s30, d1
    vmov r1, s30
    cmp r1, #0
    beq intop_zero_1
    sdiv r2, r0, r1
    b intop_done_1
intop_zero_1:
    mov r2, #0
intop_done_1:
    vmov s31, r2
    vcvt.f64.s32 d0, s31
    ldr r10, =res_4
    vstr.f64 d0, [r10]
    ldr r10, =const_5
    vldr.f64 d0, [r10]
    ldr r10, =const_4
    vldr.f64 d1, [r10]
    vcvtr.s32.f64 s31, d0
    vmov r0, s31
    vcvtr.s32.f64 s30, d1
    vmov r1, s30
    cmp r1, #0
    beq intop_zero_2
    sdiv r2, r0, r1
    mls r2, r2, r1, r0
    b intop_done_2
intop_zero_2:
    mov r2, #0
intop_done_2:
    vmov s31, r2
    vcvt.f64.s32 d0, s31
    ldr r10, =res_5
    vstr.f64 d0, [r10]
    ldr r10, =const_1
    vldr.f64 d0, [r10]
    ldr r10, =const_7
    vldr.f64 d1, [r10]
    vcvtr.s32.f64 s31, d1
    vmov r0, s31
    vmov.f64 d0, d0
    bl pow_pos_int
    vmov.f64 d0, d0
    ldr r10, =res_6
    vstr.f64 d0, [r10]
    ldr r10, =const_5
    vldr.f64 d0, [r10]
    ldr r10, =const_1
    vldr.f64 d1, [r10]
    vcvtr.s32.f64 s31, d0
    vmov r0, s31
    vcvtr.s32.f64 s30, d1
    vmov r1, s30
    cmp r1, #0
    beq intop_zero_3
    sdiv r2, r0, r1
    b intop_done_3
intop_zero_3:
    mov r2, #0
intop_done_3:
    vmov s31, r2
    vcvt.f64.s32 d0, s31
    ldr r10, =mem_X
    vstr.f64 d0, [r10]
    ldr r10, =res_7
    vstr.f64 d0, [r10]
    ldr r10, =const_5
    vldr.f64 d0, [r10]
    ldr r10, =mem_X
    vldr.f64 d1, [r10]
    vmul.f64 d0, d0, d1
    ldr r10, =res_8
    vstr.f64 d0, [r10]
    ldr r10, =mem_X
    vldr.f64 d0, [r10]
    ldr r10, =const_1
    vldr.f64 d1, [r10]
    vmul.f64 d0, d0, d1
    ldr r10, =mem_Y
    vstr.f64 d0, [r10]
    ldr r10, =res_9
    vstr.f64 d0, [r10]
    ldr r10, =res_7
    vldr.f64 d0, [r10]
    ldr r10, =res_10
    vstr.f64 d0, [r10]
    ldr r10, =mem_Y
    vldr.f64 d0, [r10]
    ldr r10, =res_11
    vstr.f64 d0, [r10]
    ldr r10, =res_1
    vldr.f64 d0, [r10]
    ldr r10, =res_12
    vstr.f64 d0, [r10]
    ldr r10, =const_1
    vldr.f64 d0, [r10]
    ldr r10, =const_4
    vldr.f64 d1, [r10]
    vmul.f64 d0, d0, d1
    ldr r10, =const_9
    vldr.f64 d1, [r10]
    vadd.f64 d0, d0, d1
    ldr r10, =mem_X
    vldr.f64 d1, [r10]
    vmul.f64 d0, d0, d1
    ldr r10, =res_11
    vldr.f64 d1, [r10]
    vdiv.f64 d0, d0, d1
    ldr r10, =res_13
    vstr.f64 d0, [r10]
    b .
pow_pos_int:
    push {r4, lr}
    vmov.f64 d1, d0
    ldr r4, =const_8
    vldr.f64 d0, [r4]
    cmp r0, #0
    ble pow_done
pow_loop:
    vmul.f64 d0, d0, d1
    subs r0, r0, #1
    bgt pow_loop
pow_done:
    pop {r4, pc}

.data
res_0: .double 0.0
res_1: .double 0.0
res_2: .double 0.0
res_3: .double 0.0
res_4: .double 0.0
res_5: .double 0.0
res_6: .double 0.0
res_7: .double 0.0
res_8: .double 0.0
res_9: .double 0.0
res_10: .double 0.0
res_11: .double 0.0
res_12: .double 0.0
res_13: .double 0.0
mem_X: .double 0.0
mem_Y: .double 0.0
const_0: .double 3.14
const_1: .double 2.0
const_2: .double 5.5
const_3: .double 2.1
const_4: .double 3.0
const_5: .double 10.0
const_6: .double 2.5
const_7: .double 3
const_8: .double 1.0
const_9: .double 5.0
