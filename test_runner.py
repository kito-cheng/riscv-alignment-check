#!/usr/bin/env python3
"""
RISC-V Alignment Test Runner

Runs alignment tests with different configurations for RISC-V assembly files.
"""

import subprocess
import sys
import os
import re
from pathlib import Path
import argparse
from typing import List, Dict, Tuple

class RISCVTestRunner:
    def __init__(self, toolchain_base: str = None, use_clang: bool = False,
                 clang_path: str = None, as_path: str = None,
                 ld_path: str = None, objdump_path: str = None):
        # Tool paths
        if toolchain_base:
            self.toolchain_base = toolchain_base
        else:
            self.toolchain_base = "/scratch/kitoc/riscv-gnu-workspace/rv64gc-sifive-linux/install/bin"

        self.use_clang = use_clang

        # Set assembler/clang path
        if use_clang:
            if clang_path:
                self.as_cmd = clang_path
            else:
                self.as_cmd = f"{self.toolchain_base}/riscv64-unknown-linux-gnu-clang"
        else:
            if as_path:
                self.as_cmd = as_path
            else:
                self.as_cmd = f"{self.toolchain_base}/riscv64-unknown-linux-gnu-as"

        # Set linker path
        if ld_path:
            self.ld_cmd = ld_path
        else:
            self.ld_cmd = f"{self.toolchain_base}/riscv64-unknown-linux-gnu-ld"

        # Set objdump path
        if objdump_path:
            self.objdump_cmd = objdump_path
        else:
            self.objdump_cmd = f"{self.toolchain_base}/riscv64-unknown-linux-gnu-objdump"

        # Test configurations
        self.configs = {
            'norvc': ['-defsym', 'NORVC=1'],
            'norvc-norelax': ['-defsym', 'NORVC=1', '-defsym', 'NORELAX=1'],
            'norelax': ['-defsym', 'NORELAX=1'],
            'relax-rvc': []
        }

        # Source files mapping
        self.sources = {
            'test': 'test.s',
            'relax1': 'relax-align-1.s',
            'relax2': 'relax-align-2.s',
            'relax3': 'relax-align-3.s',
            'relax4': 'relax-align-4.s',
            'relax5': 'relax-align-5.s',
            'relax6': 'relax-align-6.s',
            'relax7': 'relax-align-7.s',
            'relax8': 'relax-align-8.s',
            'relax9': 'relax-align-9.s',
            'relax10': 'relax-align-10.s',
            'relax11': 'relax-align-11.s',
            'relax12': 'relax-align-12.s',
        }

    def run_command(self, cmd: List[str], description: str = "") -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error {description}: {e}")
            print(f"stderr: {e.stderr}")
            return False, e.stderr
        except FileNotFoundError as e:
            print(f"Tool not found {description}: {e}")
            return False, str(e)

    def run_test(self, source_name: str, config_name: str) -> bool:
        """Run a single test configuration."""
        source_file = self.sources[source_name]
        config_flags = self.configs[config_name]

        # Generate file names
        if source_name == 'test':
            prefix = 'test'
            target_name = config_name
        else:
            prefix = source_name
            target_name = f"{source_name}-{config_name}"

        obj_file = f"{prefix}.{config_name.replace('-', '.')}.o"
        elf_file = f"{prefix}.{config_name.replace('-', '.')}.elf"
        dump_file = f"{prefix}.{config_name.replace('-', '.')}.dump"

        print(f"\n=== Running test: {target_name} ===")

        # Step 1: Assemble
        if self.use_clang:
            # Convert assembler flags for clang
            clang_flags = ['-target', 'riscv64-unknown-linux-gnu', '-c', source_file, '-o', obj_file, '-march=rv64gc', '-mrelax']
            i = 0
            while i < len(config_flags):
                flag = config_flags[i]
                if flag == '-defsym' and i + 1 < len(config_flags):
                    # Convert -defsym SYMBOL=1 to -Wa,--defsym,SYMBOL=1
                    defsym_value = config_flags[i + 1]
                    clang_flags.append(f'-Wa,--defsym,{defsym_value}')
                    i += 2  # Skip both -defsym and its value
                else:
                    clang_flags.append(flag)
                    i += 1
            as_cmd = [self.as_cmd] + clang_flags
        else:
            as_cmd = [self.as_cmd, source_file, '-o', obj_file, '-march=rv64gc', '-mrelax'] + config_flags
        success, output = self.run_command(as_cmd, "assembling")
        if not success:
            return False

        # Step 2: Link
        ld_cmd = [self.ld_cmd, '-Tx.ld', obj_file, '-o', elf_file]
        success, output = self.run_command(ld_cmd, "linking")
        if not success:
            return False

        # Step 3: Disassemble
        objdump_cmd = [self.objdump_cmd, '-d', elf_file]
        success, output = self.run_command(objdump_cmd, "disassembling")
        if not success:
            return False

        # Write dump file
        with open(dump_file, 'w') as f:
            f.write(output)

        # Step 4: Check alignment
        success = self.check_alignment(dump_file, target_name)

        return success

    def check_alignment(self, dump_file: str, target_name: str) -> bool:
        """Check if SHOULD_ALIGN_X_HERE symbols are aligned to their required boundaries."""
        try:
            with open(dump_file, 'r') as f:
                content = f.read()

            # Look for any SHOULD_ALIGN_X_HERE symbols
            # Expected format: "0000000000001008 <SHOULD_ALIGN_4_HERE>:" or "0000000000001010 <SHOULD_ALIGN_16_HERE>:"
            pattern = r'([0-9a-fA-F]+)\s+<SHOULD_ALIGN_(\d+)_HERE>:'
            matches = re.findall(pattern, content)

            if not matches:
                print(f"✗ Alignment check failed for {target_name}")
                print(f"  Error: No SHOULD_ALIGN_X_HERE symbols found in disassembly")
                return False

            all_aligned = True

            for address_str, alignment_str in matches:
                address = int(address_str, 16)
                required_alignment = int(alignment_str)

                # Check alignment
                is_aligned = (address % required_alignment) == 0

                if is_aligned:
                    print(f"✓ Alignment check passed for {target_name}")
                    print(f"  SHOULD_ALIGN_{required_alignment}_HERE: 0x{address:x} (aligned to {required_alignment}-byte boundary)")
                else:
                    print(f"✗ Alignment check failed for {target_name}")
                    print(f"  SHOULD_ALIGN_{required_alignment}_HERE: 0x{address:x} (NOT aligned to {required_alignment}-byte boundary)")
                    print(f"  Offset from {required_alignment}-byte boundary: {address % required_alignment} bytes")
                    all_aligned = False

            return all_aligned

        except FileNotFoundError:
            print(f"✗ Alignment check failed for {target_name}")
            print(f"  Error: Dump file {dump_file} not found")
            return False
        except Exception as e:
            print(f"✗ Alignment check failed for {target_name}")
            print(f"  Error: {e}")
            return False

    def run_all_tests(self, sources: List[str] = None, configs: List[str] = None) -> Dict[str, bool]:
        """Run all specified tests."""
        if sources is None:
            sources = list(self.sources.keys())
        if configs is None:
            configs = list(self.configs.keys())

        results = {}

        for source in sources:
            if source not in self.sources:
                print(f"Warning: Unknown source '{source}', skipping")
                continue

            for config in configs:
                if config not in self.configs:
                    print(f"Warning: Unknown config '{config}', skipping")
                    continue

                test_name = f"{source}-{config}" if source != 'test' else config
                results[test_name] = self.run_test(source, config)

        return results

    def clean(self):
        """Clean generated files."""
        patterns = ['*.o', '*.elf', '*.dump']
        for pattern in patterns:
            for file in Path('.').glob(pattern):
                print(f"Removing {file}")
                file.unlink()

    def get_config_suffix(self, config_name: str) -> str:
        """Map config names to .d file suffixes."""
        config_map = {
            'norelax': 'norelax',
            'norvc-norelax': 'norelax.norvc',
            'norvc': 'norvc',
            'relax-rvc': 'relax.rvc'
        }
        return config_map.get(config_name, config_name)

    def get_as_flags_string(self, config_name: str) -> str:
        """Get assembler flags as string for .d file."""
        if self.use_clang:
            base_flags = "-c -march=rv64gc -mrelax"
            config_flags = self.configs.get(config_name, [])

            # Convert defsym flags for clang format
            clang_flags = []
            i = 0
            while i < len(config_flags):
                flag = config_flags[i]
                if flag == '-defsym' and i + 1 < len(config_flags):
                    # Convert -defsym SYMBOL=1 to -Wa,--defsym,SYMBOL=1
                    defsym_value = config_flags[i + 1]
                    clang_flags.append(f'-Wa,--defsym,{defsym_value}')
                    i += 2  # Skip both -defsym and its value
                else:
                    clang_flags.append(flag)
                    i += 1

            flag_str = " ".join(clang_flags)
            if flag_str:
                return f"{base_flags} {flag_str}"
            return base_flags
        else:
            base_flags = "-mrelax -march=rv64gc"
            config_flags = self.configs.get(config_name, [])

            # Convert list of flags to string
            flag_str = " ".join(config_flags)
            if flag_str:
                return f"{base_flags} {flag_str}"
            return base_flags

    def generate_binutils_testcases(self, sources: List[str] = None, configs: List[str] = None, output_dir: str = ""):
        """Generate binutils testcase .d files."""
        if sources is None:
            sources = [s for s in self.sources.keys() if s != 'test']  # Exclude 'test'
        if configs is None:
            configs = list(self.configs.keys())

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"Generating binutils testcases in {output_path}")

        generated_testcases = []

        for source in sources:
            if source not in self.sources:
                print(f"Warning: Unknown source '{source}', skipping")
                continue
            if source == 'test':
                print(f"Skipping '{source}' as it's not a relax-align test")
                continue

            source_file = self.sources[source]
            # Extract base name (e.g., 'relax-align-1' from 'relax-align-1.s')
            base_name = source_file.replace('.s', '')

            for config in configs:
                if config not in self.configs:
                    print(f"Warning: Unknown config '{config}', skipping")
                    continue

                # Generate .d filename
                config_suffix = self.get_config_suffix(config)
                d_filename = f"{base_name}-{config_suffix}.d"
                d_filepath = output_path / d_filename

                # First run the test to generate the dump file
                success = self.run_test(source, config)
                if not success:
                    print(f"Failed to generate test for {source}-{config}, skipping .d file generation")
                    continue

                # Generate dump filename to read from
                if source == 'test':
                    prefix = 'test'
                else:
                    prefix = source
                dump_file = f"{prefix}.{config.replace('-', '.')}.dump"

                # Generate .d file content
                as_flags = self.get_as_flags_string(config)

                d_content = f"""#source: {source_file}
#as: {as_flags}
#ld: -melf64lriscv -Trelax-align.ld
#objdump: -d
"""

                # Run binutils-gen-dump-scan to get the content
                scan_cmd = ["binutils-gen-dump-scan", dump_file, "--opcode-check", "--addr-check"]
                success, scan_output = self.run_command(scan_cmd, f"generating dump scan for {d_filename}")

                if success:
                    d_content += scan_output
                else:
                    print(f"Warning: binutils-gen-dump-scan failed for {dump_file}, using placeholder")
                    d_content += "# binutils-gen-dump-scan failed\n"

                # Write .d file
                with open(d_filepath, 'w') as f:
                    f.write(d_content)

                print(f"Generated {d_filepath}")

                # Add testcase name to list (without .d extension)
                testcase_name = f"{base_name}-{config_suffix}"
                generated_testcases.append(testcase_name)

        print(f"Binutils testcase generation completed in {output_path}")

        # Output run_dump_test commands
        if generated_testcases:
            print("\nGenerated testcases:")
            for testcase in generated_testcases:
                print(f'    run_dump_test "{testcase}"')

def main():
    parser = argparse.ArgumentParser(description='RISC-V Alignment Test Runner')
    parser.add_argument('--sources', nargs='*', choices=['test', 'relax1', 'relax2', 'relax3', 'relax4', 'relax5', 'relax6', 'relax7', 'relax8', 'relax9', 'relax10', 'relax11', 'relax12'],
                       help='Source files to test (default: all)')
    parser.add_argument('--configs', nargs='*', choices=['norvc', 'norvc-norelax', 'norelax', 'relax-rvc'],
                       help='Configurations to test (default: all)')
    parser.add_argument('--clean', action='store_true', help='Clean generated files')
    parser.add_argument('--list', action='store_true', help='List available tests')
    parser.add_argument('--gen-binutils-test', action='store_true', help='Generate binutils testcases')
    parser.add_argument('--output-dir', help='Output directory for binutils testcases (required with --gen-binutils-test)', default="test-out")
    parser.add_argument('--toolchain-base', help='Override toolchain base path')
    parser.add_argument('--clang', action='store_true', help='Use clang instead of gas for assembly')
    parser.add_argument('--clang-path', help='Override clang path (when using --clang)')
    parser.add_argument('--as-path', help='Override assembler path')
    parser.add_argument('--ld-path', help='Override linker path')
    parser.add_argument('--objdump-path', help='Override objdump path')

    args = parser.parse_args()

    runner = RISCVTestRunner(args.toolchain_base, args.clang,
                            args.clang_path, args.as_path,
                            args.ld_path, args.objdump_path)

    if args.clean:
        runner.clean()
        return

    if args.list:
        print("Available sources:", list(runner.sources.keys()))
        print("Available configs:", list(runner.configs.keys()))
        print("\nExample usage:")
        print("  python test_runner.py --sources test relax1 --configs norvc norelax")
        return

    if args.gen_binutils_test:
        if not args.output_dir:
            print("Error: --output-dir is required when using --gen-binutils-test")
            sys.exit(1)
        runner.generate_binutils_testcases(args.sources, args.configs, args.output_dir)
        return

    # Run tests
    results = runner.run_all_tests(args.sources, args.configs)

    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)

    passed = 0
    total = len(results)

    for test_name, success in results.items():
        if success:
            status = "PASS"
            print(f"{test_name:25} {status}")
            passed += 1
        else:
            status = "\033[91mFAIL\033[0m"  # Red color for FAIL
            print(f"{test_name:25} {status}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed! ✓")
        sys.exit(0)
    else:
        print("Some tests failed! ✗")
        sys.exit(1)

if __name__ == '__main__':
    main()
