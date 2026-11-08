def send_event(trace_callback, event_type, **details):

    if trace_callback is not None:
        event = {"type": event_type}
        event.update(details)
        trace_callback(event)


def karatsuba_positive(x, y, trace_callback=None, depth=0, branch="root"):

    send_event(
        trace_callback,
        "recursive_start",
        x=x,
        y=y,
        depth=depth,
        branch=branch
    )

    # Base case: multiply directly when either operand has at most 2 digits.
    if x < 100 or y < 100:
        result = x * y
        send_event(
            trace_callback,
            "base_case",
            x=x,
            y=y,
            result=result,
            depth=depth,
            branch=branch
        )

        send_event(
            trace_callback,
            "recursive_complete",
            x=x,
            y=y,
            result=result,
            depth=depth,
            branch=branch
        )

        return result

    # Split both operands.
    n = max(len(str(x)), len(str(y)))
    m = n // 2
    power = 10 ** m

    a, b = divmod(x, power)
    c, d = divmod(y, power)

    send_event(
        trace_callback,
        "split",
        x=x,
        y=y,
        a=a,
        b=b,
        c=c,
        d=d,
        n=n,
        m=m,
        power=power,
        depth=depth,
        branch=branch
    )

    # z0 = b * d
    send_event(
        trace_callback,
        "branch_start",
        branch="z0",
        formula=f"{b} x {d}",
        depth=depth
    )

    z0 = karatsuba_positive(
        b, d, trace_callback, depth + 1, "z0"
    )

    send_event(
        trace_callback,
        "branch_complete",
        branch="z0",
        result=z0,
        depth=depth
    )

    # z2 = a * c
    send_event(
        trace_callback,
        "branch_start",
        branch="z2",
        formula=f"{a} x {c}",
        depth=depth
    )

    z2 = karatsuba_positive(
        a, c, trace_callback, depth + 1, "z2"
    )

    send_event(
        trace_callback,
        "branch_complete",
        branch="z2",
        result=z2,
        depth=depth
    )

    # z1 = (a + b) * (c + d)
    send_event(
        trace_callback,
        "branch_start",
        branch="z1",
        formula=f"({a} + {b}) x ({c} + {d})",
        depth=depth
    )

    z1_product = karatsuba_positive(
        a + b,
        c + d,
        trace_callback,
        depth + 1,
        "z1"
    )

    send_event(
        trace_callback,
        "branch_complete",
        branch="z1",
        result=z1_product,
        depth=depth
    )

    # Calculate the middle term.
    z1 = z1_product - z2 - z0

    send_event(
        trace_callback,
        "middle_term",
        z1_product=z1_product,
        z2=z2,
        z0=z0,
        result=z1,
        depth=depth
    )

    # Combine the three products.
    result = (
        z2 * (10 ** (2 * m))
        + z1 * power
        + z0
    )

    send_event(
        trace_callback,
        "combine",
        z2=z2,
        z1=z1,
        z0=z0,
        power=power,
        result=result,
        depth=depth,
        branch=branch
    )

    send_event(
        trace_callback,
        "recursive_complete",
        x=x,
        y=y,
        result=result,
        depth=depth,
        branch=branch
    )

    return result


def karatsuba_multiply(x, y, trace_callback=None):

    if not isinstance(x, int) or not isinstance(y, int):
        raise TypeError("Both inputs must be integers.")

    send_event(
        trace_callback,
        "algorithm_start",
        x=x,
        y=y
    )

    negative_result = (x < 0) != (y < 0)

    if x < 0 or y < 0:
        send_event(
            trace_callback,
            "sign_handling",
            x=x,
            y=y,
            negative_result=negative_result
        )

    result = karatsuba_positive(
        abs(x),
        abs(y),
        trace_callback
    )

    if negative_result:
        result = -result

    send_event(
        trace_callback,
        "algorithm_complete",
        x=x,
        y=y,
        result=result,
        correct=(result == x * y)
    )

    return result


if __name__ == "__main__":
    test_cases = [
        (0, 12345),
        (12, 34),
        (99, 99),
        (123, 45678),
        (12345, 6789),
        (123456789, 987654321),
        (-12345, 6789),
        (-12345, -6789),
        (999999999999, 888888888888)
    ]

    for num1, num2 in test_cases:
        result = karatsuba_multiply(num1, num2)

        print("First Number:", num1)
        print("Second Number:", num2)
        print("Result:", result)
        print("Correct:", result == num1 * num2)
        print("-----------------------------")
