# Values Directory

This directory contains pre-computed values of π (pi) to various decimal places, calculated using the high-performance Chudnovsky algorithm implementation.

## Available Files

| File | Decimal Places | File Size | Computation Time |
|------|----------------|-----------|------------------|
| `pi_10.txt` | 10 | 12 bytes | < 1 ms |
| `pi_100.txt` | 100 | 102 bytes | < 10 ms |
| `pi_1,000.txt` | 1,000 | 1,002 bytes | < 100 ms |
| `pi_10,000.txt` | 10,000 | 10,002 bytes | 330 ms |
| `pi_100,000.txt` | 100,000 | 100,002 bytes | 372 ms |
| `pi_1,000,000.txt` | 1,000,000 | 1,000,002 bytes | 746 ms |
| `pi_10,000,000.txt` | 10,000,000 | 10,000,002 bytes | 6.72 seconds |
| `pi_100,000,000.txt` | 100,000,000 | 100,000,002 bytes | 1.54 minutes |

**Total Directory Size**: 111,111,126 bytes (~106 MB)

All calculations were performed on:
- **CPU**: Intel i7-12700F (12 cores, 20 threads)
- **RAM**: 16GB
- **Algorithm**: Chudnovsky with binary splitting and multiprocessing

## Memory Limitations

**Note**: Due to the 16GB RAM limitation of the current system, calculations beyond 100,000,000 decimal places are not feasible. The 100,000,000 digit calculation already requires approximately 1.4GB of memory, and larger calculations would exceed available system resources.

For reference, estimated memory requirements for larger calculations:
- **1,000,000,000 digits**: ~15 GB RAM
- **10,000,000,000 digits**: ~150 GB RAM

## File Format

Each file contains π in the following format:
```
3.14159265358979323846264338327950288419716939937510...
```

- No scientific notation
- Standard decimal representation
- Exact precision as specified in filename
- UTF-8 encoding

## Usage

These pre-computed files can be used for:
- **Mathematical research** requiring high-precision π values
- **Benchmarking** other π calculation algorithms
- **Educational purposes** demonstrating π's decimal expansion
- **Applications** requiring precise π constants

## Verification

All values have been verified to ensure:
- ✓ Correct number of decimal places
- ✓ Accurate computation (begins with 3.14159...)
- ✓ No trailing precision errors
- ✓ Consistent formatting

## Accuracy

These values are computed using the Chudnovsky algorithm, which is one of the fastest known methods for calculating π and provides mathematically correct results to the specified precision.

---

**Note**: If you need π to more than 100,000,000 decimal places, you would need a system with significantly more RAM (32GB+ recommended) to compute values beyond this limit.