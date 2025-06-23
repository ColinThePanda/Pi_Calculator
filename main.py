from gmpy2 import mpz, mpfr
import time
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    BarColumn,
    TaskProgressColumn,
)
import multiprocessing as mp
import gc
import psutil

# Pre-computed constants to avoid repeated calculations
CONST_6 = mpz(6)
CONST_2 = mpz(2)
CONST_5 = mpz(5)
CONST_1 = mpz(1)
CONST_426880 = mpz(426880)
CONST_13591409 = mpz(13591409)
CONST_545140134 = mpz(545140134)
CONST_10939058860032000 = mpz(10939058860032000)


def binary_split(a, b):
    if b == a + 1:
        a_mpz = mpz(a)
        Pab = -(
            (CONST_6 * a_mpz - CONST_5)
            * (CONST_2 * a_mpz - CONST_1)
            * (CONST_6 * a_mpz - CONST_1)
        )
        Qab = CONST_10939058860032000 * (a_mpz**3)
        Rab = Pab * (CONST_545140134 * a_mpz + CONST_13591409)
    else:
        m = (a + b) // 2
        Pam, Qam, Ram = binary_split(a, m)
        Pmb, Qmb, Rmb = binary_split(m, b)
        Pab = Pam * Pmb
        Qab = Qam * Qmb
        Rab = Qmb * Ram + Pam * Rmb
    return Pab, Qab, Rab


def get_optimal_chunk_size(start, end, num_cores):
    total_terms = end - start
    available_memory_gb = psutil.virtual_memory().available / (1024**3)

    # Estimate memory per chunk (very rough)
    memory_per_term_mb = 0.05  # Conservative estimate
    max_terms_by_memory = int(available_memory_gb * 1024 / memory_per_term_mb * 0.7)

    # More chunks for better load balancing
    optimal_chunks = num_cores * 4
    chunk_size_by_cores = total_terms // optimal_chunks
    chunk_size_by_memory = max_terms_by_memory // optimal_chunks

    return max(min(chunk_size_by_cores, chunk_size_by_memory), 1)


def parallel_binary_split(start, end, progress: Progress):
    num_cores = mp.cpu_count()
    chunk_size = (end - start) // (num_cores * 2) or 1
    chunks = [(i, min(i + chunk_size, end)) for i in range(start, end, chunk_size)]

    split_task = progress.add_task("Splitting terms...", total=len(chunks))
    split_start = time.time()

    def task_callback(_):
        progress.update(split_task, advance=1)

    max_workers = min(num_cores * 2, len(chunks))  # Don't exceed chunk count
    with mp.Pool(processes=max_workers) as pool:
        result_objects = [
            pool.apply_async(binary_split, chunk, callback=task_callback)
            for chunk in chunks
        ]
        results = [r.get() for r in result_objects]
    split_end = time.time()

    merge_task = progress.add_task("Merging terms...", total=len(results) - 1)
    merge_start = time.time()

    while len(results) > 1:
        next_results = []
        for i in range(0, len(results), 2):
            if i + 1 < len(results):
                P1, Q1, R1 = results[i]
                P2, Q2, R2 = results[i + 1]
                P = P1 * P2
                Q = Q1 * Q2
                R = Q2 * R1 + P1 * R2
                next_results.append((P, Q, R))
                progress.update(merge_task, advance=1)
            else:
                next_results.append(results[i])
        results = next_results

    merge_end = time.time()

    return results[0], split_end - split_start, merge_end - merge_start


def chudnovsky_pi(digits: int, progress: Progress):
    gmpy2.get_context().precision = digits * 4  # Keep original precision
    n = int(digits * 0.0715) + 50

    for attempt in range(50):
        result, split_time, merge_time = parallel_binary_split(1, n + 1, progress)

        P, Q, R = result

        sqrt_task = progress.add_task("Computing √10005...", total=1)
        sqrt_start = time.time()
        sqrt10005 = gmpy2.sqrt(mpfr(10005))
        sqrt_end = time.time()
        progress.update(sqrt_task, advance=1)

        assemble_task = progress.add_task("Assembling π...", total=3)
        pi_start = time.time()

        # Combine operations to reduce intermediate allocations
        numerator = CONST_426880 * sqrt10005 * Q
        progress.update(assemble_task, advance=1)

        denominator = CONST_13591409 * Q + R
        progress.update(assemble_task, advance=1)

        pi = numerator / denominator
        progress.update(assemble_task, advance=1)
        pi_end = time.time()

        pi_str = format(pi, f".{digits}f")
        decimal_pos = pi_str.find(".")
        if decimal_pos == -1:
            continue
        trimmed = pi_str[decimal_pos + 1 :].rstrip("0")
        if len(trimmed) >= digits:
            return (
                pi_str[: decimal_pos + 1 + digits],
                split_time,
                merge_time,
                sqrt_end - sqrt_start,
                pi_end - pi_start,
            )
        n = int(n * 1.2) + 5

    raise RuntimeError("Failed to compute enough digits of pi")


def benchmark_and_calculate(precision, save_to_file=False):
    formatted_precision = f"{precision:,}"
    console = Console()
    num_cores = mp.cpu_count()
    available_memory_gb = psutil.virtual_memory().available / (1024**3)

    console.print(
        f"[bold blue]Calculating π to {formatted_precision} decimal places using optimized Chudnovsky algorithm...[/bold blue]"
    )
    console.print(
        f"[bold cyan]System has {num_cores} CPU cores available for calculation[/bold cyan]"
    )
    console.print(
        f"[bold cyan]Available memory: {available_memory_gb:.1f} GB[/bold cyan]"
    )

    if precision > 10_000_000:
        estimated_memory_gb = precision * 15 / (1024 * 1024 * 1024)
        console.print(
            f"[bold yellow]WARNING: This calculation may require approximately {estimated_memory_gb:.1f} GB of memory[/bold yellow]"
        )

    start_time = time.time()
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        result, split_time, merge_time, sqrt_time, pi_time = chudnovsky_pi(
            precision, progress
        )
    end_time = time.time()

    elapsed = end_time - start_time
    if elapsed < 1:
        time_str = f"{elapsed * 1000:.2f} ms"
    elif elapsed < 60:
        time_str = f"{elapsed:.2f} seconds"
    else:
        time_str = f"{elapsed / 60:.2f} minutes"

    console.print(f"[cyan]Terms were split in {split_time:.2f} seconds[/cyan]")
    console.print(f"[cyan]Terms were merged in {merge_time:.2f} seconds[/cyan]")
    console.print(f"[cyan]√10005 was computed in {sqrt_time:.2f} seconds[/cyan]")
    console.print(f"[cyan]π was assembled in {pi_time:.2f} seconds[/cyan]")

    console.print(
        f"[bold green]Calculation completed in {time_str} using up to {min(num_cores * 2, mp.cpu_count())} processes[/bold green]"
    )

    decimal_part = result.split(".")[1] if "." in result else ""
    trailing_zeros = 0
    for i in range(len(decimal_part) - 1, -1, -1):
        if decimal_part[i] != "0":
            break
        trailing_zeros += 1

    if trailing_zeros > precision * 0.1:
        console.print(
            f"[bold yellow]Warning: Result has {trailing_zeros:,} trailing zeros, which may indicate precision issues[/bold yellow]"
        )

    pi_start = result[:10]
    if pi_start.startswith("3.14159"):
        console.print(
            "[bold green]Calculation verified: result begins with 3.14159... ✓[/bold green]"
        )
    else:
        console.print(
            f"[bold red]Warning: Result may be incorrect. Expected 3.14159..., got {pi_start}...[/bold red]"
        )

    if len(decimal_part) == precision:
        console.print(
            f"[bold green]Output length verified: {formatted_precision} decimal places ✓[/bold green]"
        )
    else:
        console.print(
            f"[bold red]Warning: Output length incorrect. Expected {formatted_precision}, got {len(decimal_part)}[/bold red]"
        )

    if save_to_file:
        with open(f"pi_{formatted_precision}.txt", "w") as f:
            f.write(result)
        console.print(
            f"[bold green]π to {formatted_precision} decimal places saved to pi_{formatted_precision}.txt[/bold green]"
        )
    else:
        console.print(
            f"\n[bold green]π to {formatted_precision} decimal places:[/bold green]"
        )
        if len(result) <= 1000:
            console.print(result)

    return result


if __name__ == "__main__":
    console = Console()

    try:
        import gmpy2
    except ImportError:
        console.print("[bold red]Error: gmpy2 module not found.[/bold red]")
        console.print("[yellow]Please install it using: pip install gmpy2[/yellow]")
        exit(1)

    precision = int(
        console.input("[bold blue]Enter the number of decimal places for π: ")
    )
    save_to_file = bool(
        int(
            console.input(
                "[bold blue]Do you want to save the result to a file? (1. yes, 0. no): "
            )
            .strip()
            .lower()
        )
    )

    benchmark_and_calculate(precision, save_to_file)
    input()
