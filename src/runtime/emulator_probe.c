/* Bounded mGBA function probes. No input automation, runFrame or screenshot API. */
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba/internal/arm/arm.h>
#include <mgba-util/vfs.h>
#include <stdlib.h>
static struct mCore *core;
static color_t pixels[240*160];

static void quiet(struct mLogger *logger, int category, enum mLogLevel level, const char *fmt, va_list args) {}

static struct mLogger logger={.log=quiet};

int start(const char *path) {
  mLogSetDefaultLogger(&logger);
  core = mCoreFind(path);
  if (!core || !core->init(core)) return 0;
  mCoreInitConfig(core, NULL);
  core->setVideoBuffer(core, pixels, 240);
  if (!mCoreLoadFile(core,path)) return 0;
  core->reset(core);
  return 1;
}

unsigned read32(unsigned a) { return core->busRead32(core,a); }

unsigned read8(unsigned a) { return core->busRead8(core,a); }

unsigned lookup_probe(unsigned source) {
  // Test-only invocation of the redirect lookup; stop BEFORE any drawing occurs.
  // Run in Thumb system mode with IRQ/FIQ masked, using a disposable test stack.
  unsigned cpsr=0xf3, sp=0x03007f00, pc=0x08900000;
  core->writeRegister(core,"cpsr",&cpsr);
  core->writeRegister(core,"sp",&sp);
  core->writeRegister(core,"r4",&source);
  core->writeRegister(core,"pc",&pc);
  struct ARMCore *cpu=core->cpu;
  for(unsigned i=0;i<512;i++) {
    if(cpu->gprs[15]==0x08900038) return cpu->gprs[4];
    core->step(core);
  }
  return 0;
}

unsigned native_display_probe(unsigned source, unsigned entry) {
  unsigned cpsr=0xf3, sp=0x03007f00, ret=0x080000e1;
  core->writeRegister(core,"cpsr",&cpsr);core->writeRegister(core,"sp",&sp);
  core->writeRegister(core,"r0",&source);core->writeRegister(core,"lr",&ret);
  core->writeRegister(core,"pc",&entry);
  struct ARMCore *cpu=core->cpu;
  for(unsigned i=0;i<16384;i++) {
    if(cpu->gprs[15]==0x080000e4) return cpu->gprs[0];
    core->step(core);
  }
  return 0;
}

unsigned native_length_probe(unsigned source, unsigned return_address) {
  // Isolated unit probe: emulate a caller, stop before executing its return site.
  unsigned cpsr=0xf3, sp=0x03007f00, entry=0x08004954;
  core->writeRegister(core,"cpsr",&cpsr);core->writeRegister(core,"sp",&sp);
  core->writeRegister(core,"r0",&source);core->writeRegister(core,"lr",&return_address);
  core->writeRegister(core,"pc",&entry);
  struct ARMCore *cpu=core->cpu;
  for(unsigned i=0;i<16384;i++) {
    if(cpu->gprs[15]==((return_address&~1U)+4)) return cpu->gprs[0];
    core->step(core);
  }
  return 0xffffffff;
}

int test_write_ram(unsigned address, const unsigned char *data, unsigned count) {
  // Test-fixture bytes only; never used to alter gameplay flags, HP or outcomes.
  if(!count || count>1024) return 0;
  if(!((address>=0x02000000 && address<=0x02040000-count) ||
       (address>=0x03000000 && address<=0x03008000-count))) return 0;
  for(unsigned i=0;i<count;i++) core->busWrite8(core,address+i,data[i]);
  return 1;
}

int shop_copy_probe(unsigned destination, unsigned source, unsigned width) {
  // Isolated UI-buffer unit fixture. No gameplay state is resumed after this call.
  unsigned cpsr=0xf3, sp=0x03007f00, pc=0x0800a914, ret=0x080000e1;
  core->writeRegister(core,"cpsr",&cpsr);core->writeRegister(core,"sp",&sp);
  core->writeRegister(core,"r0",&destination);core->writeRegister(core,"r1",&source);
  core->writeRegister(core,"r2",&width);core->writeRegister(core,"lr",&ret);
  core->writeRegister(core,"pc",&pc);
  struct ARMCore *cpu=core->cpu;
  for(unsigned i=0;i<16384;i++) {
    if(cpu->gprs[15]==0x080000e4) return 1;
    core->step(core);
  }
  return 0;
}

int right_copy_probe(unsigned destination, unsigned source, unsigned width) {
  // Isolated formatting function call; no gameplay or savedata import.
  unsigned cpsr=0xf3, sp=0x03007f00, pc=0x0800ab5c, ret=0x080000e1;
  core->busWrite32(core,0x02017ae0,destination);
  core->writeRegister(core,"cpsr",&cpsr);core->writeRegister(core,"sp",&sp);
  core->writeRegister(core,"r0",&source);core->writeRegister(core,"r1",&width);
  core->writeRegister(core,"lr",&ret);core->writeRegister(core,"pc",&pc);
  struct ARMCore *cpu=core->cpu;
  for(unsigned i=0;i<65536;i++) {
    if(cpu->gprs[15]==0x080000e4) return 1;
    core->step(core);
  }
  return 0;
}

void stop(void) { mCoreConfigDeinit(&core->config);core->deinit(core);core=NULL; }

static unsigned glyph_probe_values[3];

void *glyph_probe_result(void) { return glyph_probe_values; }

int glyph_wrap_probe(unsigned context, unsigned glyph) {
  unsigned cpsr=0xf3, sp=0x03007f00, entry=0x0800cd2c, ret=0x080000e1;
  core->writeRegister(core,"cpsr",&cpsr);core->writeRegister(core,"sp",&sp);
  core->writeRegister(core,"r0",&context);core->writeRegister(core,"r1",&glyph);
  core->writeRegister(core,"lr",&ret);core->writeRegister(core,"pc",&entry);
  struct ARMCore *cpu=core->cpu;
  for(unsigned i=0;i<65536;i++) {
    if(cpu->gprs[15]==0x080000e4) return cpu->gprs[13]==sp ? 1 : 0;
    if(cpu->gprs[15]==0x0800ccf2) {
      glyph_probe_values[0]=core->busRead8(core,context+6);
      glyph_probe_values[1]=core->busRead8(core,context+7);
      glyph_probe_values[2]=cpu->gprs[3];
      // Observe the real placement, then bypass the unchanged pixel blitter.
      unsigned next=cpu->gprs[14]&~1U;
      core->writeRegister(core,"pc",&next);
    } else core->step(core);
  }
  return 0;
}

static unsigned string_probe_records[512][3];
static unsigned string_probe_count;

unsigned string_draw_events(void) { return string_probe_count; }

void *string_draw_event_data(void) { return string_probe_records; }

int native_string_draw_probe(unsigned source, unsigned compact) {
  unsigned cpsr=0xf3, sp=0x03007f00, entry=0x0800d55c, ret=0x080000e1;
  core->writeRegister(core,"cpsr",&cpsr);core->writeRegister(core,"sp",&sp);
  core->writeRegister(core,"r0",&source);core->writeRegister(core,"r1",&compact);
  core->writeRegister(core,"lr",&ret);core->writeRegister(core,"pc",&entry);
  struct ARMCore *cpu=core->cpu;string_probe_count=0;
  for(unsigned i=0;i<200000;i++) {
    if(cpu->gprs[15]==0x080000e4) return cpu->gprs[13]==sp ? 1 : 0;
    if(cpu->gprs[15]==0x0800ccf2) {
      if(string_probe_count>=512) return 0;
      unsigned ctx=cpu->gprs[0];
      string_probe_records[string_probe_count][0]=core->busRead8(core,ctx+6);
      string_probe_records[string_probe_count][1]=core->busRead8(core,ctx+7);
      string_probe_records[string_probe_count][2]=cpu->gprs[3];
      string_probe_count++;
      unsigned next=cpu->gprs[14]&~1U;core->writeRegister(core,"pc",&next);
    } else core->step(core);
  }
  glyph_probe_values[0]=cpu->gprs[15];glyph_probe_values[1]=cpu->gprs[13];glyph_probe_values[2]=string_probe_count;
  return 0;
}

static unsigned name_probe_records[128][4];
static unsigned name_probe_count;

unsigned name_field_events(void) { return name_probe_count; }

void *name_field_event_data(void) { return name_probe_records; }

int name_field_probe(unsigned font, unsigned source, unsigned tiles) {
  unsigned cpsr=0xf3, sp=0x03007f00, entry=0x08004e6c, ret=0x080000e1;
  core->writeRegister(core,"cpsr",&cpsr);core->writeRegister(core,"sp",&sp);
  core->busWrite32(core,sp,tiles);
  unsigned x=7,y=0;name_probe_count=0;
  core->writeRegister(core,"r0",&font);core->writeRegister(core,"r1",&x);
  core->writeRegister(core,"r2",&y);core->writeRegister(core,"r3",&source);
  core->writeRegister(core,"lr",&ret);core->writeRegister(core,"pc",&entry);
  struct ARMCore *cpu=core->cpu;
  for(unsigned i=0;i<65536;i++) {
    if(cpu->gprs[15]==0x080000e4) return cpu->gprs[13]==sp ? 1 : 0;
    unsigned kind=0xffffffff;
    // Between steps Thumb PC is next instruction +2. Intercept BEFORE the
    // callee's push; using entry+4 would leave an unbalanced stack.
    if(cpu->gprs[15]==0x08004992) kind=0;
    if(cpu->gprs[15]==0x08004b1e) kind=1;
    if(cpu->gprs[15]==0x083f7ae4) kind=2;
    if(kind!=0xffffffff) {
      if(name_probe_count>=128) return 0;
      name_probe_records[name_probe_count][0]=kind;
      name_probe_records[name_probe_count][1]=cpu->gprs[1];
      name_probe_records[name_probe_count][2]=cpu->gprs[2];
      name_probe_records[name_probe_count][3]=cpu->gprs[5];
      name_probe_count++;
      unsigned next=cpu->gprs[14]&~1U;core->writeRegister(core,"pc",&next);
    } else core->step(core);
  }
  return 0;
}
