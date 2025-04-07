# Understanding Binary Size and Memory Usage for Microcontrollers

This guide explains how binary size is measured, what stripped binaries are, and how to interpret memory usage metrics for microcontroller deployment.

## Binary Segments and Memory Layout

When a C program is compiled, it's divided into several segments:

| Segment | Description | Memory Type | Example Content |
|---------|-------------|-------------|-----------------|
| `.text` | Executable code | ROM/Flash | Functions, code logic |
| `.rodata` | Read-only data | ROM/Flash | Constants, string literals, neural network weights |
| `.data` | Initialized variables | ROM + RAM | Global variables with initial values |
| `.bss` | Uninitialized variables | RAM | Global variables without initial values |

### Memory Impact

- **ROM/Flash Memory** usage = `.text` + `.rodata` + `.data`
- **RAM Memory** usage = `.data` + `.bss` + stack + heap

## What is a "Stripped" Binary?

### Definition
A stripped binary has debugging symbols and non-essential information removed from the executable.

### What Gets Removed
- Function and variable names
- Line number information
- Debug information
- Type descriptions
- Source file references

### Benefits for Microcontrollers
- **Smaller file size**: Often 20-50% smaller than non-stripped binaries
- **Faster loading**: Less data to transfer to the device
- **More efficient memory use**: Only essential code and data remain

### What's Preserved
- All functional code
- All necessary data
- The program's behavior remains identical

### How Stripping is Done
The `strip` command removes this information:
```bash
strip executable_name
```

## Understanding Size Command Output

When you run `size executable_name`, you'll see output like this:

```
   text    data     bss     dec     hex filename
  10285     616     112   11013    2b05 minimal_nn
```

### Explanation of Columns
- **text**: Size of code and read-only data (in bytes)
- **data**: Size of initialized data (in bytes)
- **bss**: Size of uninitialized data (in bytes)
- **dec**: Total size in decimal (sum of text, data, and bss)
- **hex**: Total size in hexadecimal

## Understanding Objdump Output

The `objdump -h` command shows detailed information about each section:

```
Idx Name          Size      VMA       LMA       File off  Algn
  1 .text         00002815  00401000  00401000  00001000  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
  2 .rodata       00000123  00404000  00404000  00004000  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
```

### Key Fields
- **Name**: Section name
- **Size**: Size in bytes (hexadecimal)
- **CONTENTS**: Section contains data
- **ALLOC**: Section occupies memory during execution
- **LOAD**: Section will be loaded from the executable file
- **READONLY**: Section cannot be modified during execution

## How Memory Usage is Calculated

The compile script calculates estimated memory usage with:

```bash
# Extract section sizes (in hex)
TEXT_SIZE=$(objdump -h binary | grep "\.text" | awk '{print $3}')
RODATA_SIZE=$(objdump -h binary | grep "\.rodata" | awk '{print $3}')
DATA_SIZE=$(objdump -h binary | grep "\.data" | awk '{print $3}')
BSS_SIZE=$(objdump -h binary | grep "\.bss" | awk '{print $3}')

# Convert hex to decimal
TEXT_DEC=$((16#$TEXT_SIZE))
RODATA_DEC=$((16#${RODATA_SIZE:-0}))
DATA_DEC=$((16#${DATA_SIZE:-0}))
BSS_DEC=$((16#${BSS_SIZE:-0}))

# Calculate memory usage
ROM_USAGE=$((TEXT_DEC + RODATA_DEC + DATA_DEC))
RAM_USAGE=$((DATA_DEC + BSS_DEC))
```

### Why This Matters for Microcontrollers

Microcontrollers have two critical memory constraints:

1. **Flash/ROM**: Stores the program and constants
   - Limited (typically 16KB-2MB)
   - Must fit entire program and constant data
   - Neural network weights are stored here

2. **RAM**: Stores variables and temporary data
   - Very limited (typically 2KB-512KB)
   - Must accommodate all runtime data needs
   - Critical for neural network calculations

## Optimization Flags Explained

The compilation script uses these flags:

```bash
gcc -Os -fdata-sections -ffunction-sections -Wl,--gc-sections
```

### What Each Flag Does

- **-Os**: Optimize for size (rather than speed)
  - Reduces code size by using more compact instructions
  - May slightly reduce performance

- **-fdata-sections -ffunction-sections**: 
  - Places each function and data item in its own section
  - Enables fine-grained removal of unused code/data

- **-Wl,--gc-sections**: 
  - "Garbage collects" unused sections during linking
  - Removes any functions or data not referenced in the code

## Real-world Implications for Microcontrollers

### MSP430 Example
- Flash memory: Usually 16KB-256KB
- RAM: Usually 512B-8KB 
- If your neural network uses 10KB ROM and 1KB RAM:
  - It would fit on an MSP430F5529 (128KB Flash, 8KB RAM)
  - It would NOT fit on an MSP430G2553 (16KB Flash, 512B RAM)

### Practical Considerations

1. **Reserve headroom**: Leave ~20% memory free for:
   - Future code updates
   - Stack usage during function calls
   - Additional variables

2. **Consider dynamic ranges**:
   - Stack usage varies during execution
   - Additional temporary variables
   - Memory fragmentation

3. **Further optimization techniques**:
   - Quantization (float32 → int8)
   - Pruning (removing unnecessary weights)
   - Loop unrolling and constant folding

## Example: Interpreting Compilation Output

```
ROM (Flash) usage: ~10901 bytes
RAM usage: ~728 bytes
```

This means:
- You need at least 11KB of Flash memory
- You need at least 0.8KB of RAM
- Plus extra for stack and any dynamic allocations
- For safety, target a microcontroller with at least 16KB Flash and 2KB RAM

## Conclusion

Understanding binary size metrics is crucial for successful microcontroller deployment. The stripped binary provides the most accurate representation of your neural network's memory footprint, helping you select an appropriate microcontroller for your application.
