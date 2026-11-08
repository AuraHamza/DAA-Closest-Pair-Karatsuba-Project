
def karatsuba_multiply(x, y):

    if not isinstance(x, int) or not isinstance(y, int):
        raise TypeError("Both inputs must be integers.")

    if x < 0 or y < 0:
        if x < 0 and y < 0:
            return karatsuba_multiply(-x, -y)
        elif x < 0:
            return -karatsuba_multiply(-x, y)
        else:
            return -karatsuba_multiply(x, -y)

    if x < 10 or y < 10:
        return x * y

    n = max(len(str(x)), len(str(y)))
    m = n // 2

    power = 10 ** m

    a = x // power
    b = x % power

    c = y // power
    d = y % power

    z0 = karatsuba_multiply(b, d)
    z2 = karatsuba_multiply(a, c)
    z1 = karatsuba_multiply(a + b, c + d) - z2 - z0

    result = (z2 * (10 ** (2 * m))) + (z1 * power) + z0

    return result


# Edge Case Testing
test_cases = [
    (0, 12345),
    (123, 45678),
    (12345, 6789),
    (123456789, 987654321),
    (-12345, 6789),
    (-12345, -6789)
]

for num1, num2 in test_cases:
    result = karatsuba_multiply(num1, num2)

    print("First Number:", num1)
    print("Second Number:", num2)
    print("Result:", result)
    print("Correct:", result == num1 * num2)
    print("-----------------------------")
