# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Test Commands

This is a RISC-V assembly alignment testing project using GNU toolchain binaries. The Makefile defines several test configurations:

- `make all` - Builds all test variants
- `make norvc` - Tests without RVC (compressed instructions), with relaxation
- `make norvc-norelax` - Tests without RVC and without relaxation
- `make norelax` - Tests with RVC but without relaxation
- `make relax-rvc` - Tests with both RVC and relaxation enabled
- `make clean` - Removes generated files (*.o, *.elf, *.dump)

Each test target produces object files, linked ELF binaries, and disassembly dumps, then searches for alignment markers.

## Code Architecture

This is a RISC-V toolchain testing repository focused on linker relaxation and instruction alignment behavior:

### Core Files
- `test.s` - Main test assembly file with alignment directives and conditional compilation
- `relax-align-1.s` / `relax-align-2.s` - Additional test cases for different alignment scenarios
- `x.ld` - Linker script defining memory layout (text section at 0x1000)
- `Makefile` - Build system with cross-compilation toolchain paths

### Test Purpose
The tests verify alignment behavior under different RISC-V assembler/linker configurations:
- RVC (compressed instruction) extensions on/off
- Linker relaxation on/off
- Assembly alignment directives (.balign 8)

### Toolchain Configuration
Uses RISC-V GNU toolchain with hardcoded paths to:
- `riscv64-unknown-linux-gnu-as` (assembler)
- `riscv64-unknown-linux-gnu-ld` (linker)  
- `riscv64-unknown-linux-gnu-objdump` (disassembler)

The tests use conditional assembly (.ifdef NORVC, .ifdef NORELAX) to enable different compilation modes and check for proper 8-byte alignment at the `SHOULD_ALIGN_8_HERE` marker.