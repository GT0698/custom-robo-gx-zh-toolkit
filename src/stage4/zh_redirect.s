.syntax unified
.cpu arm7tdmi
.thumb
.text
.global zh_fetch
.macro call address
    ldr r3, =\address
    bl .Lcall_r3
.endm
zh_fetch:
    push {r1, r3, r5, r6, r7, lr}
    @ Redirect only exact original message-body addresses, preserving script layout.
    ldr r3, =0x084b5fa0
    cmp r4, r3
    blo .Lfetch
    ldr r3, =0x085371d8
    cmp r4, r3
    bhs .Lfetch
    ldr r3, =0x088a0000
    ldr r1, [r3]
    adds r3, #4
    movs r0, #0
.Lsearch:
    cmp r0, r1
    bhs .Lfetch
    adds r2, r0, r1
    lsrs r2, r2, #1
    lsls r6, r2, #3
    adds r6, r6, r3
    ldr r7, [r6]
    cmp r4, r7
    beq .Lfound
    blo .Llower
    adds r0, r2, #1
    b .Lsearch
.Llower:
    movs r1, r2
    b .Lsearch
.Lfound:
    ldr r4, [r6, #4]
.Lfetch:
    ldrb r0, [r4]
    cmp r0, #0xff
    bne .Lcheck
    adds r4, #1
    b .Lfetch
.Lcheck:
    cmp r0, #1
    bne .Lordinary
    ldr r3, =0x08910000
    cmp r4, r3
    blo .Lordinary
    ldr r3, =0x08b00000
    cmp r4, r3
    bhs .Lordinary
    ldrb r0, [r4, #1]
    cmp r0, #5
    beq .Lexplicit_newline
    cmp r0, #0xfe
    bne .Lordinary
    ldrb r6, [r4, #2]
    ldrb r0, [r4, #3]
    lsls r0, r0, #8
    orrs r6, r0
    adds r4, #4
    @ One logical Chinese character, two physical six-pixel glyphs.
    @ Check both halves fit BEFORE drawing either half.
    ldrb r0, [r5, #2]
    ldr r3, =0x083f77f0
    ldrb r0, [r3, r0]
    ldrb r1, [r5, #6]
    adds r1, #2
    cmp r1, r0
    bls .Lfits
    ldrb r0, [r5, #7]
    adds r0, #1
    ldrb r1, [r5, #3]
    cmp r1, #3
    blo .Lnewline
    cmp r0, r1
    blo .Lnewline
    movs r0, r5
    movs r1, #7
    call 0x083f7ec3
    cmp r0, #0
    beq .Lfits
    subs r4, #4
    b .Labort
.Lnewline:
    movs r0, r5
    call 0x0800d001
.Lfits:
    lsls r6, r6, #1
    ldr r0, =1719
    adds r6, r6, r0
    movs r0, r5
    movs r1, r6
    call 0x0800cd2d
    movs r0, r5
    adds r1, r6, #1
    call 0x0800cd2d
    movs r0, r5
    movs r1, #1
    call 0x0800cfc1
    b .Lfetch
.Lexplicit_newline:
    ldrb r0, [r5, #7]
    adds r0, #1
    ldrb r1, [r5, #3]
    cmp r1, #3
    blo .Lordinary
    cmp r0, r1
    blo .Lordinary
    adds r4, #2
    movs r0, r5
    movs r1, #7
    call 0x083f7ec3
    cmp r0, #0
    beq .Lfetch
    subs r4, #2
.Labort:
    @ Match DrawDialogString's pause/resume contract when START interrupts a wait.
    ldr r0, [sp, #12]
    str r4, [r0]
    pop {r1, r3, r5, r6, r7}
    pop {r2}
    movs r0, #0
    ldr r2, =0x0800d557
    bx r2
.Lordinary:
    ldrb r0, [r4]
    movs r2, r0
    adds r4, #1
    pop {r1, r3, r5, r6, r7}
    pop {r0}
    mov lr, r0
    movs r0, r2
    bx lr
.Lcall_r3:
    bx r3
    .ltorg
