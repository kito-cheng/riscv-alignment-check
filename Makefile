AS:=/scratch/kitoc/riscv-gnu-workspace/rv64gc-sifive-linux/install/bin/riscv64-unknown-linux-gnu-as
LD:=/scratch/kitoc/riscv-gnu-workspace/rv64gc-sifive-linux/install/bin/riscv64-unknown-linux-gnu-ld
OBJDUMP:=/scratch/kitoc/riscv-gnu-workspace/rv64gc-sifive-linux/install/bin/riscv64-unknown-linux-gnu-objdump

TESTS:=norvc norvc-norelax norelax relax-rvc \
	relax1-norvc relax1-norvc-norelax relax1-norelax relax1-relax-rvc \
	relax2-norvc relax2-norvc-norelax relax2-norelax relax2-relax-rvc

all: $(TESTS)

norvc: test.s
	$(AS) test.s -o test.norvc.o -march=rv64gc -mrelax -defsym NORVC=1
	$(LD) -Tx.ld test.norvc.o -o test.norvc.elf
	$(OBJDUMP) -d test.norvc.elf > test.norvc.dump
	grep SHOULD_ALIGN_8_HERE test.norvc.dump

norvc-norelax: test.s
	$(AS) test.s -o test.norvc-norelax.o -march=rv64gc -mrelax -defsym NORVC=1 -defsym NORELAX=1
	$(LD) -Tx.ld test.norvc-norelax.o -o test.norvc-norelax.elf
	$(OBJDUMP) -d test.norvc-norelax.elf > test.norvc-norelax.dump
	grep SHOULD_ALIGN_8_HERE test.norvc-norelax.dump

norelax: test.s
	$(AS) test.s -o test.norelax.o -march=rv64gc -mrelax -defsym NORELAX=1
	$(LD) -Tx.ld test.norelax.o -o test.norelax.elf
	$(OBJDUMP) -d test.norelax.elf > test.norelax.dump
	grep SHOULD_ALIGN_8_HERE test.norelax.dump

relax-rvc: test.s
	$(AS) test.s -o test.relax-rvc.o -march=rv64gc -mrelax
	$(LD) -Tx.ld test.relax-rvc.o -o test.relax-rvc.elf
	$(OBJDUMP) -d test.relax-rvc.elf > test.relax-rvc.dump
	grep SHOULD_ALIGN_8_HERE test.relax-rvc.dump

# relax-align-1.s tests
relax1-norvc: relax-align-1.s
	$(AS) relax-align-1.s -o relax1.norvc.o -march=rv64gc -mrelax -defsym NORVC=1
	$(LD) -Tx.ld relax1.norvc.o -o relax1.norvc.elf
	$(OBJDUMP) -d relax1.norvc.elf > relax1.norvc.dump
	grep SHOULD_ALIGN_8_HERE relax1.norvc.dump

relax1-norvc-norelax: relax-align-1.s
	$(AS) relax-align-1.s -o relax1.norvc-norelax.o -march=rv64gc -mrelax -defsym NORVC=1 -defsym NORELAX=1
	$(LD) -Tx.ld relax1.norvc-norelax.o -o relax1.norvc-norelax.elf
	$(OBJDUMP) -d relax1.norvc-norelax.elf > relax1.norvc-norelax.dump
	grep SHOULD_ALIGN_8_HERE relax1.norvc-norelax.dump

relax1-norelax: relax-align-1.s
	$(AS) relax-align-1.s -o relax1.norelax.o -march=rv64gc -mrelax -defsym NORELAX=1
	$(LD) -Tx.ld relax1.norelax.o -o relax1.norelax.elf
	$(OBJDUMP) -d relax1.norelax.elf > relax1.norelax.dump
	grep SHOULD_ALIGN_8_HERE relax1.norelax.dump

relax1-relax-rvc: relax-align-1.s
	$(AS) relax-align-1.s -o relax1.relax-rvc.o -march=rv64gc -mrelax
	$(LD) -Tx.ld relax1.relax-rvc.o -o relax1.relax-rvc.elf
	$(OBJDUMP) -d relax1.relax-rvc.elf > relax1.relax-rvc.dump
	grep SHOULD_ALIGN_8_HERE relax1.relax-rvc.dump

# relax-align-2.s tests
relax2-norvc: relax-align-2.s
	$(AS) relax-align-2.s -o relax2.norvc.o -march=rv64gc -mrelax -defsym NORVC=1
	$(LD) -Tx.ld relax2.norvc.o -o relax2.norvc.elf
	$(OBJDUMP) -d relax2.norvc.elf > relax2.norvc.dump
	grep SHOULD_ALIGN_8_HERE relax2.norvc.dump

relax2-norvc-norelax: relax-align-2.s
	$(AS) relax-align-2.s -o relax2.norvc-norelax.o -march=rv64gc -mrelax -defsym NORVC=1 -defsym NORELAX=1
	$(LD) -Tx.ld relax2.norvc-norelax.o -o relax2.norvc-norelax.elf
	$(OBJDUMP) -d relax2.norvc-norelax.elf > relax2.norvc-norelax.dump
	grep SHOULD_ALIGN_8_HERE relax2.norvc-norelax.dump

relax2-norelax: relax-align-2.s
	$(AS) relax-align-2.s -o relax2.norelax.o -march=rv64gc -mrelax -defsym NORELAX=1
	$(LD) -Tx.ld relax2.norelax.o -o relax2.norelax.elf
	$(OBJDUMP) -d relax2.norelax.elf > relax2.norelax.dump
	grep SHOULD_ALIGN_8_HERE relax2.norelax.dump

relax2-relax-rvc: relax-align-2.s
	$(AS) relax-align-2.s -o relax2.relax-rvc.o -march=rv64gc -mrelax
	$(LD) -Tx.ld relax2.relax-rvc.o -o relax2.relax-rvc.elf
	$(OBJDUMP) -d relax2.relax-rvc.elf > relax2.relax-rvc.dump
	grep SHOULD_ALIGN_8_HERE relax2.relax-rvc.dump

clean:
	rm *.o *.elf *.dump
