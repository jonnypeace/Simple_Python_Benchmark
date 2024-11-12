#!/usr/bin/env python3

import time, math, hashlib, os, tempfile, argparse, gzip
from multiprocessing import Pool, cpu_count
from typing import Literal


def timer(mode: Literal['Single Threaded', 'Multiprocessing'], func, *args, repeat=1, **kwargs):
    '''Times Functions with Multiple Iterations'''
    total_time = 0
    for _ in range(repeat):
        start_time = time.time()
        func(*args, **kwargs)
        total_time += time.time() - start_time
    avg_time = total_time / repeat
    print(f"{mode} Time (avg over {repeat} runs): {avg_time:.2f} seconds")


def compression_operations(data_size_mb):
    data = b"A" * (data_size_mb * 1024 * 1024)
    compressed_data = gzip.compress(data)
    decompressed_data = gzip.decompress(compressed_data)
    return len(decompressed_data)

# Integer arithmetic
def integer_operations(n):
    count = 0
    for i in range(n):
        count += i % 2
    return count

# Floating-point arithmetic
def floating_point_operations(n):
    result = 0.0
    for i in range(1, n):
        result += math.sqrt(i) / (i + 1)
    return result

# Encryption benchmark
def encryption_operations(n):
    data = b"A" * 1024  # 1 KB of data
    for _ in range(n):
        hashlib.sha256(data).hexdigest()
    return True

# Disk I/O benchmark
def disk_io_operations(file_size_mb, block_size_kb=64):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    file_path = temp_file.name
    temp_file.close()

    data = b"A" * (block_size_kb * 1024)

    # Write test
    start_time = time.time()
    with open(file_path, "wb") as f:
        for _ in range((file_size_mb * 1024) // block_size_kb):
            f.write(data)
    write_time = time.time() - start_time

    # Read test
    start_time = time.time()
    with open(file_path, "rb") as f:
        while f.read(block_size_kb * 1024):
            pass
    read_time = time.time() - start_time

    os.remove(file_path)
    return write_time, read_time

# Memory speed benchmark
def memory_speed_operations(array_size):
    start_time = time.time()
    data = [0] * array_size
    for i in range(array_size):
        data[i] = i
    total_time = time.time() - start_time
    return total_time

# Multiprocessing wrapper
def run_multiprocessing(task_function, total_iterations, num_processes):
    # Calculate chunks
    chunk_size = total_iterations // num_processes
    chunks = [chunk_size] * num_processes

    # Add remainder to the last chunk
    remainder = total_iterations % num_processes
    if remainder > 0:
        chunks.append(remainder)

    with Pool(processes=num_processes) as pool:
        pool.map(task_function, chunks)    

def main():
    parser = argparse.ArgumentParser(description="Comprehensive Benchmark Script with Multiprocessing")
    parser.add_argument("--iterations", type=int, default=10**8, help="Number of iterations for integer and float tests (default: 100,000,000)")
    parser.add_argument("--encrypt_iterations", type=int, default=10**7, help="Number of iterations for encryption test (default: 10,000,000)")
    parser.add_argument("--file_size", type=int, default=1000, help="File size in MB for Disk I/O test (default: 1000 MB)")
    parser.add_argument("--gzip_size", type=int, default=1000, help="File size in MB for Disk I/O test (default: 1000 MB)")
    parser.add_argument("--array_size", type=int, default=10**8, help="Array size for memory speed test (default: 100,000,000 elements)")
    parser.add_argument("--num_processes", type=int, default=cpu_count(), help=f"Number of processes to use (default: number of CPUs: {cpu_count()})")
    parser.add_argument("--repeat", type=int, default=1, help="Number of times to repeat each benchmark (default: 1)")
    args = parser.parse_args()

    print(f"Starting benchmarks with {args.num_processes} processes...")

    print("\n[1] Integer Operations")
    timer('Single Threaded', integer_operations, args.iterations, repeat=args.repeat)
    timer('Multiprocessing', run_multiprocessing, integer_operations, args.iterations, args.num_processes, repeat=args.repeat)


    print("\n[2] Floating-Point Operations")
    timer('Single Threaded', floating_point_operations, args.iterations, repeat=args.repeat)
    timer('Multiprocessing', run_multiprocessing, floating_point_operations, args.iterations, args.num_processes, repeat=args.repeat)


    print("\n[3] Encryption (SHA-256) Operations")
    timer('Single Threaded', encryption_operations, args.encrypt_iterations, repeat=args.repeat)
    timer('Multiprocessing', run_multiprocessing, encryption_operations, args.encrypt_iterations, args.num_processes, repeat=args.repeat)

    print("\n[4] Compression Operations")
    timer('Single Threaded', compression_operations, args.gzip_size, repeat=args.repeat)
    timer('Multiprocessing', run_multiprocessing, compression_operations, args.gzip_size, args.num_processes, repeat=args.repeat)

    # Disk I/O Operations
    print("\n[5] Disk I/O Operations")
    write_time, read_time = disk_io_operations(args.file_size)
    print(f"Write Time: {write_time:.2f} seconds")
    print(f"Read Time: {read_time:.2f} seconds")

    # Memory Speed Operations
    print("\n[6] Memory Speed Operations")
    timer('Single Threaded', memory_speed_operations, args.array_size, repeat=args.repeat)

if __name__ == "__main__":
    main()
