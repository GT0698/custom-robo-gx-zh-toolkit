.syntax unified
.cpu arm7tdmi
.thumb
.text
.macro translate reg, slot
    push {r0,r1,r2,r3,r4,lr}
    movs r0, \reg
    bl .Llookup
    str r0, [sp, #\slot]
    pop {r0,r1,r2,r3,r4}
    mov ip, r4
    pop {r4}
    mov lr, r4
    mov r4, ip
.endm
.global hook_map_width
hook_map_width:
    pop {r4}
    // This UI wrapper is the audited width consumer for original map labels.
    ldr r3, =0x08009cc3
    cmp lr, r3
    bne .Lmap_width_original
    ldr r3, =0x087b7710
    cmp r0, r3
    blo .Lmap_width_original
    ldr r3, =0x087b8569
    cmp r0, r3
    bhs .Lmap_width_original
    translate r0, 0
.Lmap_width_original:
    push {r4,lr}
    movs r3, #0
    movs r2, #0
    movs r1, r0
    ldrb r0, [r1]
    adds r1, #1
    ldr r4, =0x08011a85
    bx r4
    .ltorg
.global hook_whole_glyph
hook_whole_glyph:
    pop {r4}
    push {r0,r1,r2,r3,r4,r5,r6,r7,lr}
    movs r4, r0
    movs r5, r1
    // Restrict pairing to our extended main/compact font tables. Original
    // Japanese glyphs, ASCII and icons keep the existing wrap behavior.
    ldr r2, [r4, #12]
    ldr r3, [r2, #4]
    ldr r6, =0x08880000
    cmp r3, r6
    beq .Lpair_main
    ldr r6, =0x08884000
    cmp r3, r6
    bne .Lpair_done
    ldr r6, =236
    b .Lpair_index
.Lpair_main:
    ldr r6, =1719
.Lpair_index:
    cmp r5, r6
    blo .Lpair_done
    subs r6, r5, r6
    movs r3, #1
    tst r6, r3
    bne .Lpair_done
    ldrh r3, [r2, #22]
    adds r6, r5, #1
    cmp r6, r3
    bhi .Lpair_done
    ldrb r2, [r4, #2]
    ldr r3, =0x083f77f0
    ldrb r2, [r3, r2]
    cmp r2, #2
    blo .Lpair_done
    ldrb r3, [r4, #6]
    adds r3, #2
    cmp r3, r2
    bls .Lpair_done
    movs r0, r4
    ldr r3, =0x0800d001
    bl .Lpair_call_r3
.Lpair_done:
    pop {r0,r1,r2,r3,r4,r5,r6,r7}
    pop {r3}
    mov lr, r3
    // Replay the exact English DrawChar prologue displaced by the hook.
    push {r4,r5,lr}
    movs r4, r0
    ldr r3, =0x083f8101
    bl .Lpair_call_r3
    ldrb r1, [r4, #6]
    cmp r0, r1
    ldr r3, =0x0800cd39
    bx r3
.Lpair_call_r3:
    bx r3
    .ltorg
.global hook_drawstr
hook_drawstr:
    pop {r4}
    translate r0, 0
    push {r4,r5,r6,r7,lr}
    ldr r5, =0x020127bc
    movs r4, r0
    cmp r1, #0
    beq .Ldraw_default
    ldr r0, =0x030013d0
    ldr r3, =0x0800d569
    bx r3
.Ldraw_default:
    ldr r3, =0x0800d57d
    bx r3
.global hook_e28
hook_e28:
    pop {r4}
    translate r3, 12
    push {r4,r5,r6,r7,lr}
    mov r7, r8
    push {r7}
    movs r6, r0
    mov r8, r1
    movs r7, r2
    ldr r4, =0x08004e35
    bx r4
.global hook_e6c
hook_e6c:
    pop {r4}
    translate r3, 12
    push {r4,r5,r6,r7,lr}
    mov r7, r8
    push {r7}
    movs r7, r0
    movs r6, r3
    ldr r0, [sp, #0x18]
    ldr r4, =0x08004e79
    bx r4
.global hook_ec0
hook_ec0:
    pop {r4}
    translate r3, 12
    push {r4,r5,r6,r7,lr}
    mov r7, sl
    mov r6, sb
    mov r5, r8
    push {r5,r6,r7}
    sub sp, #4
    ldr r4, =0x08004ecd
    bx r4
.global hook_9e64
hook_9e64:
    pop {r4}
    translate r3, 12
    push {r4,r5,r6,r7,lr}
    movs r5, r0
    movs r4, r3
    ldrh r0, [r5, #0x14]
    muls r0, r2, r0
    adds r0, r0, r1
    ldr r3, =0x08009e71
    bx r3
.global hook_9ea8
hook_9ea8:
    pop {r4}
    translate r2, 8
    push {r4,r5,r6,r7,lr}
    movs r6, r0
    movs r7, r1
    movs r4, r3
    movs r5, r2
    movs r0, r5
    ldr r3, =0x08009eb5
    bx r3
.global hook_length
.global hook_equipment_text
hook_equipment_text:
    pop {r4}
    translate r1, 4
    push {r4,r5,lr}
    movs r4, r0
    movs r5, r1
    movs r1, #0
    ldrb r0, [r5]
    cmp r0, #0x81
    ldr r3, =0x08008099
    bx r3
hook_length:
    pop {r4}
    push {r1,r2}
    mov r1, lr
    ldr r2, =0x0800c243
    cmp r1, r2
    beq .Llength_display
    ldr r2, =0x080096ab
    cmp r1, r2
    beq .Llength_display
    pop {r1,r2}
    b .Llength_original
.Llength_display:
    pop {r1,r2}
    translate r0, 0
.Llength_original:
    push {lr}
    movs r1, r0
    movs r2, #0
    ldrb r0, [r1]
    adds r1, #1
    cmp r0, #0
    ldr r3, =0x08004961
    bx r3
.global native_lookup
.global hook_shop_name_copy
hook_shop_name_copy:
    pop {r4}
    push {r2,r3,r4,r5,r6}
    ldr r3, =0x0200cdc8
    ldr r3, [r3]
    ldr r4, =0x0850941d
    cmp r3, r4
    beq .Lshop_copy_translate
    ldr r4, =0x08509517
    cmp r3, r4
    beq .Lshop_copy_translate
    // Retry/COM label compositions: exact script PC, original string pointer and
    // destination buffer. No generic RAM/string-bank translation.
    ldr r4, =0x088f1000
    ldr r5, [r4]
    adds r4, #4
.Lretry_copy_scan:
    cmp r5, #0
    beq .Lcopy_untranslated
    ldr r6, [r4]
    cmp r3, r6
    bne .Lretry_copy_next
    ldr r6, [r4, #4]
    cmp r1, r6
    bne .Lretry_copy_next
    ldr r6, [r4, #8]
    cmp r0, r6
    beq .Lretry_copy_translate
.Lretry_copy_next:
    adds r4, #12
    subs r5, #1
    b .Lretry_copy_scan
.Lcopy_untranslated:
    ldr r4, =0x088f1400
    ldr r5, [r4]
    adds r4, #4
.Lcopy_context_scan:
    cmp r5, #0
    beq .Lcopy_no_extra
    ldr r6, [r4]
    cmp r3, r6
    beq .Lcopy_selected_guard
    adds r4, #16
    subs r5, #1
    b .Lcopy_context_scan
.Lcopy_selected_guard:
    ldr r6, =0x02017ae0
    ldr r5, [r6]
    cmp r0, r5
    bne .Lcopy_no_extra
    cmp r0, r6
    bhs .Lcopy_no_extra
    ldr r6, =0x020132e0
    cmp r0, r6
    blo .Lcopy_no_extra
    subs r5, r0, r6
    movs r2, #15
    ands r2, r5
    bne .Lcopy_no_extra
    // For offset/16 in0..1151: divisible by3 iff (x*2731)%4096 <=383.
    // This validates exact48-byte slots without a division or unbounded loop.
    lsrs r5, r5, #4
    ldr r2, =2731
    muls r5, r2
    lsls r5, r5, #20
    lsrs r5, r5, #20
    ldr r2, =383
    cmp r5, r2
    bhi .Lcopy_no_extra
    ldr r6, [r4, #12]
    mov ip, r6
    ldr r3, [r4, #4]
    ldr r5, [r4, #8]
    movs r4, #0
.Lcopy_source_search:
    cmp r4, r5
    bhs .Lcopy_no_extra
    adds r6, r4, r5
    lsrs r6, r6, #1
    lsls r2, r6, #2
    adds r2, r2, r3
    ldr r2, [r2]
    cmp r1, r2
    beq .Lcopy_extra_found
    blo .Lcopy_source_lower
    adds r4, r6, #1
    b .Lcopy_source_search
.Lcopy_source_lower:
    movs r5, r6
    b .Lcopy_source_search
.Lcopy_extra_found:
    mov r2, ip
    str r2, [sp]
    b .Lretry_copy_translate
.Lcopy_no_extra:
    pop {r2,r3,r4,r5,r6}
    b .Lshop_copy_original
.Lretry_copy_translate:
    pop {r2,r3,r4,r5,r6}
    translate r1, 4
    b .Lshop_copy_original
.Lshop_copy_translate:
    pop {r2,r3,r4,r5,r6}
    translate r1, 4
    movs r2, #14
.Lshop_copy_original:
    push {r4,r5,r6,r7,lr}
    mov r7, sl
    mov r6, sb
    mov r5, r8
    push {r5,r6,r7}
    mov r8, r0
    ldr r3, =0x0800a921
    bx r3
.global hook_com_right
hook_com_right:
    pop {r4}
    push {r2,r3,r4,r5,r6}
    ldr r2, =0x0200cdc8
    ldr r2, [r2]
    ldr r3, =0x02017ae0
    ldr r3, [r3]
    ldr r4, =0x088f1100
    ldr r5, [r4]
    adds r4, #4
.Lright_scan:
    cmp r5, #0
    beq .Lright_miss
    ldr r6, [r4]
    cmp r2, r6
    bne .Lright_next
    ldr r6, [r4, #4]
    cmp r0, r6
    bne .Lright_next
    ldr r6, [r4, #8]
    cmp r3, r6
    beq .Lright_found
.Lright_next:
    adds r4, #12
    subs r5, #1
    b .Lright_scan
.Lright_found:
    pop {r2,r3,r4,r5,r6}
    translate r0, 0
    movs r1, #6
    b .Lright_resume
.Lright_miss:
    pop {r2,r3,r4,r5,r6}
.Lright_resume:
    push {r4,r5,r6,lr}
    sub sp, #0x4c
    movs r6, r0
    movs r4, r1
    ldr r0, =0x020132e0
    movs r1, #0x90
    ldr r3, =0x0800ab69
    bx r3
    .ltorg
native_lookup:
.Llookup:
    push {r1,r2,r3,r4,r5,r6,r7,lr}
    ldr r1, =0x08000000
    cmp r0, r1
    blo .Lram_range
    ldr r1, =0x08800000
    cmp r0, r1
    bhs .Ldone
    ldr r3, =0x088c0000
    ldr r2, [r3]
    adds r3, #4
    movs r1, #0
.Lsearch:
    cmp r1, r2
    bhs .Ldone
    adds r4, r1, r2
    lsrs r4, r4, #1
    lsls r5, r4, #3
    adds r5, r5, r3
    ldr r6, [r5]
    cmp r0, r6
    beq .Lfound
    blo .Llower
    adds r1, r4, #1
    b .Lsearch
.Llower:
    movs r2, r4
    b .Lsearch
.Lfound:
    ldr r0, [r5, #4]
.Ldone:
    pop {r1,r2,r3,r4,r5,r6,r7,pc}
.Lram_range:
    ldr r1, =0x02000000
    cmp r0, r1
    blo .Ldone
    ldr r7, =0x02040000
    cmp r0, r7
    blo .Lram_hash_init
    ldr r1, =0x03000000
    cmp r0, r1
    blo .Ldone
    ldr r7, =0x03008000
    cmp r0, r7
    bhs .Ldone
.Lram_hash_init:
    movs r1, r0
    ldr r2, =512
    movs r5, #0
.Lram_hash:
    cmp r1, r7
    bhs .Ldone
    ldrb r3, [r1]
    cmp r3, #0
    beq .Lram_search_init
    adds r1, #1
    cmp r3, #32
    beq .Lram_hash_next
    subs r5, r1, r0
.Lram_hash_next:
    subs r2, #1
    bne .Lram_hash
    b .Ldone
.Lram_search_init:
    cmp r5, #0
    beq .Ldone
    // Hash the measured, right-trimmed prefix; a matching candidate also
    // receives a full byte comparison. Every pass is bounded by511 bytes.
    push {r5}
    ldr r4, =5381
    movs r1, #0
.Lram_rehash:
    ldrb r2, [r0,r1]
    lsls r3, r4, #5
    adds r4, r4, r3
    adds r4, r4, r2
    adds r1, #1
    cmp r1, r5
    blo .Lram_rehash
    // NPC names are copied to a distinct16-byte buffer. Translate them only
    // in the opponent-info screen, never a player-name buffer. Story mode
    // additionally requires an exact original ROM name in string variable9.
    ldr r3, =0x0200c1c4
    cmp r0, r3
    bne .Ltitle_table
    ldr r1, =0x0200cdc8
    ldr r1, [r1]
    ldr r2, =0x084fdb79
    cmp r1, r2
    bne .Ltitle_table
    ldr r1, =0x0200cb41
    ldrb r1, [r1]
    movs r2, #3
    ands r1, r2
    cmp r1, #1
    bhi .Ltitle_table
    // If the opponent name is a copy of the human player's name, retain it.
    ldr r1, =0x0200c1b4
    movs r2, #0
.Lnpc_player_compare:
    ldrb r3, [r0,r2]
    ldrb r6, [r1,r2]
    cmp r3, r6
    bne .Lnpc_table
    cmp r3, #0
    beq .Lram_miss
    adds r2, #1
    cmp r2, #16
    blo .Lnpc_player_compare
    b .Lram_miss
.Lnpc_table:
    ldr r3, =0x088f0000
    b .Lram_table_ready
.Ltitle_table:
    ldr r3, =0x088e0000
.Lram_table_ready:
    ldr r2, [r3]
    adds r3, #4
    movs r1, #0
.Lram_search:
    cmp r1, r2
    bhs .Lram_miss
    adds r6, r1, r2
    lsrs r6, r6, #1
    lsls r7, r6, #4
    adds r7, r7, r3
    ldr r5, [r7]
    cmp r4, r5
    beq .Lram_compare
    blo .Lram_lower
    adds r1, r6, #1
    b .Lram_search
.Lram_lower:
    movs r2, r6
    b .Lram_search
.Lram_compare:
    ldr r5, [sp]
    ldr r6, [r7, #12]
    cmp r5, r6
    bne .Lram_miss
    ldr r2, [r7, #4]
    // r3 still identifies the selected table. Tournament title aliases are
    // independent of this name provenance check.
    ldr r1, =0x088f0004
    cmp r3, r1
    bne .Lram_bytes_init
    ldr r1, =0x0200cb41
    ldrb r1, [r1]
    movs r6, #3
    ands r1, r6
    cmp r1, #1
    beq .Lram_bytes_init
    // VM root +0xA60 +9*4, as used by str_var_get/set. Match the
    // candidate source pointer, not arbitrary ROM or RAM name text.
    ldr r1, =0x0200cc24
    ldr r1, [r1]
    cmp r1, r2
    bne .Lram_miss
.Lram_bytes_init:
    movs r1, #0
.Lram_compare_byte:
    ldrb r4, [r0,r1]
    ldrb r6, [r2,r1]
    cmp r4, r6
    bne .Lram_miss
    adds r1, #1
    cmp r1, r5
    blo .Lram_compare_byte
    ldr r0, [r7, #8]
.Lram_miss:
    pop {r5}
    b .Ldone
    .ltorg
