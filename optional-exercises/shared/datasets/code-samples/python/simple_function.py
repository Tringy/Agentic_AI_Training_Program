"""
Simple utility functions for sorting and mathematical operations.
These are basic examples for testing code comprehension and modification.
"""

def bubble_sort(arr):
    """Sort an array using bubble sort algorithm."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


def calculate_factorial(n):
    """Calculate factorial of n recursively."""
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)


def is_prime(num):
    """Check if a number is prime."""
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True
