# Pi Calculator

A high-performance Python implementation of the Chudnovsky algorithm for computing π (pi) to arbitrary precision, featuring binary splitting optimization and multiprocessing acceleration.

## Overview

This project implements one of the fastest known algorithms for calculating π, the **Chudnovsky algorithm**, combined with **binary splitting** for optimal performance and **multiprocessing** to leverage all available CPU cores. The implementation can compute millions of digits of π efficiently with detailed progress tracking and performance metrics.

## Features

- **Ultra-fast computation** using the Chudnovsky algorithm
- **Binary splitting optimization** for reduced computational complexity
- **Multiprocessing support** utilizing all available CPU cores
- **Real-time progress tracking** with rich terminal interface
- **Arbitrary precision** - compute π to any number of decimal places
- **Memory usage estimation** for large calculations
- **Result verification** with automatic accuracy checks
- **File output option** for saving results
- **Detailed performance metrics** including timing breakdowns

## Algorithm Details

### Chudnovsky Algorithm

The Chudnovsky algorithm is currently one of the fastest known algorithms for computing π. It uses the following series:

```
1/π = 12 * Σ(k=0 to ∞) [(-1)^k * (6k)! * (545140134k + 13591409)] / [(3k)! * k!^3 * 426880^(2k+1/2) * 10005^(k+1/2)]
```

This algorithm converges extremely rapidly, gaining approximately 14.18 decimal digits per term.

### Binary Splitting

Binary splitting is an optimization technique that reduces the computational complexity of evaluating rational series. Instead of computing terms sequentially, it recursively splits the computation into smaller parts that can be efficiently combined.

### Multiprocessing

The implementation distributes the binary splitting computation across multiple CPU cores, significantly reducing calculation time for large precision requirements.

## Installation

### Prerequisites

- Python 3.7 or higher
- GMP library (GNU Multiple Precision Arithmetic Library)

### Install Dependencies

#### Windows (Recommended):

```bash
pip install -r requirements.txt
```

If you encounter issues with gmpy2 installation, you may need to install Microsoft Visual C++ Build Tools.

### Clone Repository

```bash
git clone https://github.com/ColinThePanda/Pi_Calculator.git
cd Pi_Calculator
```

## Usage

### Basic Usage

```bash
python pi.py
```

The program will prompt you for:

1. Number of decimal places to calculate
2. Whether to save the result to a file

### Example Output

```
Enter the number of decimal places for π: 100000000
Do you want to save the result to a file? (1. yes, 0. no): 1
Calculating π to 100,000,000 decimal places using Chudnovsky algorithm...
System has 20 CPU cores available for calculation
WARNING: This calculation may require approximately 1.4 GB of memory
  Splitting terms...  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:06
  Merging terms...    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:44
  Computing √10005... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:06
  Assembling π...     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:09
Terms were split in 92.16 seconds
Terms were merged in 44.41 seconds
√10005 was computed in 6.09 seconds
π was assembled in 9.66 seconds
Calculation completed in 1.54 minutes using 20 CPU cores
Calculation verified: result begins with 3.14159... ✓
Output length verified: 100,000,000 decimal places ✓
π to 100,000,000 decimal places saved to pi.txt
```

### Programmatic Usage

```python
from pi import benchmark_and_calculate

# Calculate π to 10,000 decimal places
result = benchmark_and_calculate(10000, save_to_file=True)
print(f"π = {result}")
```

## Performance

### Benchmarks

Performance varies based on system specifications. Results below are from testing on an Intel i7-12700F (12 cores, 20 threads) with 16GB RAM:

| Decimal Places | Time         | Memory Usage |
| -------------- | ------------ | ------------ |
| 10,000         | 330 ms       | < 10 MB      |
| 100,000        | 372 ms       | < 50 MB      |
| 1,000,000      | 746 ms       | < 100 MB     |
| 10,000,000     | 6.72 seconds | < 150 MB     |
| 100,000,000    | 1.54 minutes | ~1.4 GB      |

### Memory Requirements

The algorithm requires approximately 15 bytes per decimal digit of precision. For the 100 million digit calculation shown above, actual memory usage was approximately 1.4 GB as estimated by the program.

## Technical Implementation

### Key Components

1. **Binary Splitting Function** (`binary_split`): Recursively computes P, Q, R terms for the Chudnovsky series
2. **Parallel Processing** (`parallel_binary_split`): Distributes computation across CPU cores
3. **High-Precision Arithmetic**: Uses gmpy2 for arbitrary precision calculations
4. **Progress Tracking**: Rich console interface with real-time updates

### Dependencies

- **gmpy2**: High-performance multiple precision arithmetic
- **rich**: Beautiful terminal formatting and progress bars

## Error Handling

The program includes several verification steps:

- **Convergence checking**: Ensures sufficient precision is achieved
- **Result verification**: Checks that output begins with correct π digits
- **Length validation**: Confirms output contains requested number of decimal places
- **Trailing zero detection**: Warns about potential precision issues

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/ColinThePanda/Pi_Calculator.git
cd Pi_Calculator
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **David V. Chudnovsky** and **Gregory V. Chudnovsky** for the Chudnovsky algorithm
- **GNU Multiple Precision Arithmetic Library** for high-precision calculations
- **Python multiprocessing** for parallel computation support

## References

- Chudnovsky, D. V., & Chudnovsky, G. V. (1988). "Approximations and complex multiplication according to Ramanujan"
- Borwein, J. M., & Borwein, P. B. (1987). "Pi and the AGM: A Study in Analytic Number Theory and Computational Complexity"
- Bailey, D. H., Borwein, P. B., & Plouffe, S. (1997). "On the rapid computation of various polylogarithmic constants"

---

**Note**: For very large calculations (>10 million digits), ensure you have sufficient RAM available. The program will provide memory usage estimates before beginning calculation.
