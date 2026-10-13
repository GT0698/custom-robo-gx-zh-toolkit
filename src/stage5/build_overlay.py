from pathlib import Path
import json,sys,struct,re,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2]
for p in ['work/stage4','work/stage2','work/tools','work/catalog']:sys.path.insert(0,str(ROOT/p))
from build_redirect import build,NATIVE_CODES
from arm_object import text_section
from elf_symbols import symbols
from bps import digest

NATIVE_CATALOG_RAW=(ROOT/'work/catalog/reviewed-native-translations.json').read_bytes()
NATIVE_ROWS=json.loads(NATIVE_CATALOG_RAW)
OFFBANK_CATALOG_RAW=(ROOT/'work/catalog/reviewed-offbank-translations.json').read_bytes()
OFFBANK_ROWS=json.loads(OFFBANK_CATALOG_RAW)
LABELS={r['string_id']:r['zh'] for r in NATIVE_ROWS}
ALIAS_IDS={r['string_id'] for r in NATIVE_ROWS if r['alias_policy']=='all-identical-ROM-strings'}
RAM_IDS={r['string_id'] for r in NATIVE_ROWS if r.get('ram_display_alias')}
from tournament_title_policy import allowed_ids
if RAM_IDS - allowed_ids():raise ValueError('Unaudited RAM display alias')
BANK_IDS={r['string_id'] for r in NATIVE_ROWS if r.get('storage_policy')=='text-only-bank-pointer'}
# Only audited presentation prefixes may be redirected before RAM composition.
if BANK_IDS - {0x618}:raise ValueError('Unaudited text-only bank pointer')
for r in NATIVE_ROWS:
    if r['string_id'] in BANK_IDS and (r['kind']!='ui-buffer-prefix' or r['alias_policy']!='exact-bank-pointer'):raise ValueError('Invalid buffer-prefix classification')
CONTROL=re.compile(r'[$#][A-Za-z0-9]')
HOOKS={0x808c:('hook_equipment_text','30b5041c0d1c002128788128'),0xa914:('hook_shop_name_copy','f0b557464e464546e0b48046'),0xd55c:('hook_drawstr','f0b5054d041c00290ad00448'),0x4e28:('hook_e28','f0b5474680b4061c8846171c'),0x4e6c:('hook_e6c','f0b5474680b4071c1e1c0698'),0x4ec0:('hook_ec0','f0b557464e464546e0b481b0'),0x9e64:('hook_9e64','f0b5051c1c1ca88a50434018'),0x9ea8:('hook_9ea8','f0b5061c0f1c1c1c151c281c'),0x4954:('hook_length','00b5011c0022087801310028')}

HOOKS[0x11a78]=('hook_map_width','10b500230022011c08780131')
HOOKS[0xcd2c]=('hook_whole_glyph','30b5041cebf3e6f9a1798842')
HOOKS[0xab5c]=('hook_com_right','70b593b0061c0c1c0d489021')

def native_encode(text,ids):
    out=bytearray();p=0
    while p<len(text):
        if text[p] in '$#':
            if p+1>=len(text) or not CONTROL.fullmatch(text[p:p+2]):raise ValueError('Invalid native control')
            out+=text[p:p+2].encode('ascii');p+=2;continue
        c=text[p];p+=1
        if c.isascii() and (c.isalnum() or c==' '):out.append(ord(c))
        else:
            if c not in ids:raise ValueError('Missing native glyph '+c)
            for h in (0,1):out+=NATIVE_CODES[ids[c]*2+h].to_bytes(2,'big')
    if 0 in out:raise ValueError('Embedded NUL')
    return bytes(out)+b'\0'

def build_overlay():
    from audit_offbank_catalog import audit
    audit()
    rows={r['id']:r for r in json.loads((ROOT/'work/catalog/string-banks.json').read_text())}
    policies={r['string_id']:r.get('layout_policy') for r in NATIVE_ROWS}
    for key,text in LABELS.items():
        source_controls=CONTROL.findall(rows[key]['jp']['text']);target_controls=CONTROL.findall(text)
        if policies[key]=='reflow-newlines':
            # Native $n/$N affects layout only. Color/icon ordering remains exact.
            source_controls=[c for c in source_controls if c.lower()!='$n']
            target_controls=[c for c in target_controls if c.lower()!='$n']
        if target_controls!=source_controls:raise ValueError('Control change '+hex(key))
    chars=set(''.join(CONTROL.sub('',s) for s in LABELS.values())+''.join(CONTROL.sub('',r['zh']) for r in OFFBANK_ROWS)+''.join(v['zh_suffix'] for r in NATIVE_ROWS for v in r.get('ram_display_variants',[])))
    extras=''.join(sorted(c for c in chars if not(c.isascii() and (c.isalnum() or c==' '))))
    m=build(extra_chars=extras)
    base=(ROOT/'work/roms/custom-robo-gx-zh-redirect.gba').read_bytes();rom=bytearray(base)
    en=(ROOT/'work/roms/custom-robo-gx-en-v1.0.1.gba').read_bytes();ids=json.loads((ROOT/'work/stage4/character-map.json').read_text())
    # The compact font has its own glyph IDs/count. Extend it independently.
    subset=base[0x800000+1719*32:0x800000+m['font_bytes']]
    alt_font=en[0x3f659e:0x3f831e]+subset
    alt_table=en[0x3f831e:0x3f84f4]+b''.join(struct.pack('<H',v) for v in NATIVE_CODES[:len(ids)*2])
    if 0x840000+len(alt_font)>0x880000 or 0x884000+len(alt_table)>0x88f000:raise ValueError('Alternate font allocation overlap')
    rom[0x840000:0x840000+len(alt_font)]=alt_font
    rom[0x884000:0x884000+len(alt_table)]=alt_table
    struct.pack_into('<I',rom,0x4c98,0x08840000)
    struct.pack_into('<I',rom,0x4c9c,0x08884000)
    struct.pack_into('<H',rom,0x88f002,235+len(ids)*2)
    struct.pack_into('<I',rom,0x4ca4,0x0888f002)
    pos=0xb00000;mapping={};details=[];payload_cache={}
    for key,text in LABELS.items():
        row=rows[key];raw=bytes.fromhex(row['en']['raw']);payload=native_encode(text,ids)
        sources=[row['en']['offset']]
        # Unique part labels may live at multiple addresses. Money is context-sensitive.
        if key in ALIAS_IDS:
            cur=0
            while True:
                cur=en.find(raw,cur)
                if cur<0:break
                if cur not in sources:sources.append(cur)
                cur+=1
        if payload in payload_cache:target=payload_cache[payload]
        else:
            target=pos;payload_cache[payload]=target
            rom[pos:pos+len(payload)]=payload;pos+=len(payload)
        if key in BANK_IDS:
            if row['en']['encrypted']:raise ValueError('Encrypted buffer prefix')
            struct.pack_into('<I',rom,row['pointer_slot'],0x08000000+target)
        else:
            for a in sources:
                if a in mapping and mapping[a]!=target:raise ValueError('Ambiguous display mapping')
                mapping[a]=target
        details.append(dict(string_id=key,ja=row['jp']['text'],en=row['en']['text'],zh=text,sources=sources,target=target,pointer_slot=row['pointer_slot'],route='text-only-bank-pointer' if key in BANK_IDS else 'display-pointer-overlay'))
    offbank_details=[]
    for row in OFFBANK_ROWS:
        source=row['source_offset'];payload=native_encode(row['zh'],ids)
        if payload in payload_cache:target=payload_cache[payload]
        else:
            target=pos;payload_cache[payload]=target
            rom[pos:pos+len(payload)]=payload;pos+=len(payload)
        if source in mapping and mapping[source]!=target:raise ValueError('Ambiguous off-bank display mapping')
        mapping[source]=target
        raw=bytes.fromhex(row['en_raw_hex'])
        if rom[source:source+len(raw)]!=raw:raise ValueError('Off-bank source changed before overlay')
        offbank_details.append(dict(id=row['id'],source=source,target=target,zh=row['zh'],source_size=len(raw)))
    if pos>0xb20000:raise ValueError('Native payload budget')
    table=struct.pack('<I',len(mapping))+b''.join(struct.pack('<II',0x08000000+a,0x08000000+b) for a,b in sorted(mapping.items()))
    if 0x8c0000+len(table)>0x8e0000:raise ValueError('Display map overlaps RAM alias table')
    rom[0x8c0000:0x8c0000+len(table)]=table
    ram_entries=[];hashes=set()
    row_config={r['string_id']:r for r in NATIVE_ROWS}
    for detail in details:
        key=detail['string_id']
        if key not in RAM_IDS:continue
        raw=bytes.fromhex(rows[key]['en']['raw'])
        if not raw.endswith(b'\0') or b'\0' in raw[:-1]:raise ValueError('Invalid RAM alias source')
        raw=raw[:-1].rstrip(b' ')
        variants=[('base',raw,rows[key]['en']['offset'],detail['target'])]
        for v in row_config[key].get('ram_display_variants',[]):
            suffix=bytes.fromhex(v['source_suffix_hex'])
            if b'\0' in suffix or CONTROL.findall(v['zh_suffix']):raise ValueError('Invalid RAM display suffix')
            source=raw+suffix;source_pos=pos
            rom[pos:pos+len(source)+1]=source+b'\0';pos+=len(source)+1
            payload=native_encode(detail['zh']+v['zh_suffix'],ids);target=pos
            rom[pos:pos+len(payload)]=payload;pos+=len(payload)
            variants.append((v['name'],source,source_pos,target))
        for variant,source,source_pos,target in variants:
            if not 0<len(source)<512:raise ValueError('RAM alias source exceeds bounded scan')
            h=5381
            for c in source:h=(h*33+c)&0xffffffff
            if h in hashes:raise ValueError('RAM alias hash collision; add multi-entry support before expanding')
            hashes.add(h);ram_entries.append(dict(string_id=key,variant=variant,hash=h,source=source_pos,target=target,length=len(source),raw_hex=source.hex()))
    if pos>0xb20000:raise ValueError('Native payload budget including RAM display variants')
    ram_entries.sort(key=lambda r:r['hash'])
    ram_table=struct.pack('<I',len(ram_entries))+b''.join(struct.pack('<IIII',r['hash'],0x08000000+r['source'],0x08000000+r['target'],r['length']) for r in ram_entries)
    if 0x8e0000+len(ram_table)>0x8f0000:raise ValueError('RAM alias table overlaps NPC name table')
    rom[0x8e0000:0x8e0000+len(ram_table)]=ram_table
    npc_names=[];npc_hashes=set();by_id={d['string_id']:d for d in details}
    for row in NATIVE_ROWS:
        if row.get('kind')!='character-display-name':continue
        key=row['string_id'];source=rows[key]['en'];raw=bytes.fromhex(source['raw'])[:-1]
        if not 0<len(raw)<16:raise ValueError('NPC name exceeds original16-byte name buffer')
        text=row['zh'];target=by_id[key]['target']
        if key==0x102f:
            text='博士';payload=native_encode(text,ids);target=pos
            rom[pos:pos+len(payload)]=payload;pos+=len(payload)
        cells=sum(1 if c.isascii() and(c.isalnum() or c==' ') else 2 for c in text)
        if cells>9:raise ValueError('NPC display name exceeds header field')
        h=5381
        for c in raw:h=(h*33+c)&0xffffffff
        if h in npc_hashes:raise ValueError('NPC name hash collision')
        npc_hashes.add(h);npc_names.append(dict(string_id=key,hash=h,source=source['offset'],target=target,length=len(raw),zh=text,raw_hex=raw.hex()))
    if pos>0xb20000:raise ValueError('NPC display payload overlaps graphics')
    npc_names.sort(key=lambda r:r['hash'])
    npc_table=struct.pack('<I',len(npc_names))+b''.join(struct.pack('<IIII',r['hash'],0x08000000+r['source'],0x08000000+r['target'],r['length']) for r in npc_names)
    if 0x8f0000+len(npc_table)>0x8f1000:raise ValueError('NPC name table overlaps retry copy table')
    rom[0x8f0000:0x8f0000+len(npc_table)]=npc_table
    from retry_copy_policy import install as install_retry_policy
    from font_support import JP_PATH
    from com_copy_policy import install as install_com_policy
    com_copy_policy=install_com_policy(JP_PATH.read_bytes(),en,rom,rows)
    retry_copy_sites=install_retry_policy(JP_PATH.read_bytes(),en,rom,rows,com_copy_policy['left'])
    from inventory_copy_policy import install as install_inventory_policy
    inventory_copy_policy=install_inventory_policy(JP_PATH.read_bytes(),en,rom,rows,mapping)
    # Original7 background tiles give56px, fitting the NPC glyphs while preserving the panel edge.
    if en[0x8e62:0x8e64]!=bytes.fromhex('0720'):raise ValueError('Name field instruction mismatch')
    rom[0x8e62:0x8e64]=bytes.fromhex('0720')
    subprocess.run(['clang','-target','armv4t-none-eabi','-c',str(ROOT/'work/stage5/native_overlay.s'),'-o',str(ROOT/'work/stage5/native_overlay.o')],check=True)
    code=text_section(ROOT/'work/stage5/native_overlay.o');syms=symbols(ROOT/'work/stage5/native_overlay.o');rom[0x901000:0x901000+len(code)]=code
    for offset,(name,expected) in HOOKS.items():
        if base[offset:offset+12].hex()!=expected:raise ValueError(f'Hook mismatch {offset:x}: '+base[offset:offset+12].hex())
        # push r4; ldr r4,[pc,#4]; bx r4; padding; destination. Wrapper restores r4.
        rom[offset:offset+12]=b'\x10\xb4\x01\x4c\x20\x47\x00\x00'+struct.pack('<I',0x08901000+(syms[name]&~1)+1)
    for r in details:
        for a in r['sources']:assert rom[a:a+len(bytes.fromhex(rows[r['string_id']]['en']['raw']))]==en[a:a+len(bytes.fromhex(rows[r['string_id']]['en']['raw']))]
        slot=r['pointer_slot']
        expected=struct.pack('<I',0x08000000+r['target']) if r['string_id'] in BANK_IDS else en[slot:slot+4]
        assert rom[slot:slot+4]==expected
    from banner_assets import apply_type_banners
    graphics=apply_type_banners(rom,en)
    from main_menu_assets import apply_main_menu
    main_menu_graphics=apply_main_menu(rom,en)
    from equipment_panel_assets import apply_equipment_panel
    equipment_panel_graphics=apply_equipment_panel(rom,en)
    from battle_pause_assets import apply_battle_pause
    battle_pause_graphics=apply_battle_pause(rom,en)
    from equipment_model_labels import apply_model_labels
    model_label_graphics=apply_model_labels(rom,en)
    from venue_title_assets import apply_venue_titles
    venue_title_graphics=apply_venue_titles(rom,en)
    from league_graphics import apply_league_graphics
    league_graphics=apply_league_graphics(rom,en)
    from battle_result_assets import apply_battle_results
    battle_result_graphics=apply_battle_results(rom,en)
    from victory_assets import apply_victory
    victory_graphics=apply_victory(rom,en)
    from title_prompt_assets import apply_title_prompt
    title_prompt_graphics=apply_title_prompt(rom,en)
    from battle_hud_assets import apply_battle_hud
    battle_hud_graphics=apply_battle_hud(rom,en)
    from intro_panel_assets import apply_intro_panels
    intro_panel_graphics=apply_intro_panels(rom,en)
    from venue_sign_assets import apply_venue_signs
    venue_sign_graphics=apply_venue_signs(rom,en)
    from map_graphic_assets import apply_map_graphic
    map_graphics=apply_map_graphic(rom,en)
    from title_branding_assets import apply_title_branding
    title_branding=apply_title_branding(rom,en)
    path=ROOT/'work/roms/custom-robo-gx-zh-native-overlay.gba';path.write_bytes(rom)
    report=dict(shop_name_copy_sites=['0x0850941D','0x08509517'],native_ledger_sha256=hashlib.sha256(NATIVE_CATALOG_RAW).hexdigest(),ram_display_aliases=ram_entries,length_translation_callers=['0x0800C243','0x080096AB'],target=digest(rom),base=digest(base),labels=details,lookup_entries=len(mapping),engine_bytes=len(code),alternate_font_glyphs=236+len(ids)*2,hooks={hex(k):v[0] for k,v in HOOKS.items()},symbols=syms,original_string_bytes_unchanged=True,overlay_bank_pointers_unchanged=True,text_only_bank_pointers=[dict(string_id=r['string_id'],pointer_slot=r['pointer_slot'],target=r['target']) for r in details if r['string_id'] in BANK_IDS],scope='Display-only ROM pointers and explicitly audited padded RAM aliases. Generic string length remains untranslated outside two UI width callers. Other RAM compositions/rendering paths still need review')
    report.update(npc_name_display_entries=npc_names,npc_name_display_scope=dict(buffer="0x0200C1C4",script_pc="0x084FDB79",flag_index=4,allowed_flag_values=[0,1],story_flag_value=0,story_source_variable=9,story_source_pointer_address="0x0200CC24",story_requires_exact_candidate_source=True,exclude_equal_player_name=True,field_half_cells=9),league_graphics=league_graphics,venue_title_graphics=venue_title_graphics,model_label_graphics=model_label_graphics,battle_pause_graphics=battle_pause_graphics,equipment_panel_graphics=equipment_panel_graphics,main_menu_graphics=main_menu_graphics,graphics=graphics,offbank_labels=offbank_details,offbank_ledger_sha256=hashlib.sha256(OFFBANK_CATALOG_RAW).hexdigest())
    report['title_branding']=title_branding
    report['map_graphics']=map_graphics
    report['whole_glyph_wrap']=dict(hook='0x0800CD2C',font_tables=['0x08880000','0x08884000'],first_half_glyphs=[1719,236],preflight_half_cells=2)
    report['commander_name_field_tiles']=7
    report['venue_sign_graphics']=venue_sign_graphics
    report['retry_copy_sites']=retry_copy_sites
    report['com_copy_policy']=com_copy_policy
    report['inventory_copy_policy']=inventory_copy_policy
    report['battle_result_graphics']=battle_result_graphics
    report['victory_graphics']=victory_graphics
    report['title_prompt_graphics']=title_prompt_graphics
    report['battle_hud_graphics']=battle_hud_graphics
    report['intro_panel_graphics']=intro_panel_graphics
    report['retry_copy_scope']='Exact script PC + source pointer + destination buffer; original script, numbers, bank pointers, and backend identity unchanged.'
    (ROOT/'outputs/reports/stage5-native-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('Native overlay built',len(mapping),'entries',len(code),'code bytes')
    return report
if __name__=='__main__':build_overlay()
