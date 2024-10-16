def sum_of_digits(n):
    # Ensure that n is a non-negative integer
    if n < 0:
        raise ValueError("The input must be a non-negative integer.")

    # Convert the integer to a string to iterate over each digit
    digit_sum = sum(int(digit) for digit in str(n))
    return digit_sum