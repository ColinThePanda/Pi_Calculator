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


def binary_split(a, b):
    if b == a + 1:
        Pab = mpz(-(6 * a - 5) * (2 * a - 1) * (6 * a - 1))
        Qab = mpz(10939058860032000 * a**3)
        Rab = mpz(Pab * (545140134 * a + 13591409))
    else:
        m = (a + b) // 2
        Pam, Qam, Ram = binary_split(a, m)
        Pmb, Qmb, Rmb = binary_split(m, b)
        Pab = Pam * Pmb
        Qab = Qam * Qmb
        Rab = Qmb * Ram + Pam * Rmb
    return Pab, Qab, Rab


def parallel_binary_split(start, end, progress: Progress):
    num_cores = mp.cpu_count()
    chunk_size = (end - start) // (num_cores * 2) or 1
    chunks = [(i, min(i + chunk_size, end)) for i in range(start, end, chunk_size)]

    split_task = progress.add_task("Splitting terms...", total=len(chunks))
    split_start = time.time()

    def task_callback(_):
        progress.update(split_task, advance=1)

    with mp.Pool(processes=num_cores) as pool:
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
    gmpy2.get_context().precision = digits * 4
    n = digits // 14 + 10

    for attempt in range(50):
        result, split_time, merge_time = parallel_binary_split(1, n + 1, progress)

        P, Q, R = result

        sqrt_task = progress.add_task("Computing √10005...", total=1)
        sqrt_start = time.time()
        sqrt10005 = gmpy2.sqrt(mpfr(10005))
        sqrt_end = time.time()
        progress.update(sqrt_task, advance=1)

        assemble_task = progress.add_task("Assembling π...", total=5)
        pi_start = time.time()
        term1 = mpfr(426880) * sqrt10005
        progress.update(assemble_task, advance=1)
        time.sleep(0.01)  # tiny pause to let the UI catch up
        term1 = term1 * Q
        progress.update(assemble_task, advance=1)
        time.sleep(0.01)
        term2 = 13591409 * Q
        progress.update(assemble_task, advance=1)
        time.sleep(0.01)
        term2 += R
        progress.update(assemble_task, advance=1)
        time.sleep(0.01)
        pi = term1 / term2
        progress.update(assemble_task, advance=1)
        pi_end = time.time()

        pi_str = str(pi)
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
    console.print(
        f"[bold blue]Calculating π to {formatted_precision} decimal places using Chudnovsky algorithm...[/bold blue]"
    )
    console.print(
        f"[bold cyan]System has {num_cores} CPU cores available for calculation[/bold cyan]"
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

    console.print(f"[cyan]Terms were split in {elapsed:.2f} seconds[/cyan]")
    console.print(f"[cyan]Terms were merged in {merge_time:.2f} seconds[/cyan]")
    console.print(f"[cyan]√10005 was computed in {sqrt_time:.2f} seconds[/cyan]")
    console.print(f"[cyan]π was assembled in {pi_time:.2f} seconds[/cyan]")

    console.print(
        f"[bold green]Calculation completed in {time_str} using {num_cores} CPU cores[/bold green]"
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
            f"[bold green]π to {formatted_precision} decimal places saved to pi.txt[/bold green]"
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
