
import math


def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def send_event(trace_callback, event_type, **details):

    if trace_callback is not None:
        event = {"type": event_type}
        event.update(details)
        trace_callback(event)


def closest_pair_brute_force(points, trace_callback=None, depth=0):

    minimum_distance = float("inf")
    closest_pair = None

    send_event(
        trace_callback,
        "base_start",
        depth=depth,
        points=points
    )

    for i in range(len(points)):

        for j in range(i + 1, len(points)):

            point1 = points[i]
            point2 = points[j]

            distance = calculate_distance(point1, point2)

            send_event(
                trace_callback,
                "compare",
                depth=depth,
                point1=point1,
                point2=point2,
                distance=distance
            )

            if distance < minimum_distance:

                minimum_distance = distance
                closest_pair = (point1, point2)

                send_event(
                    trace_callback,
                    "new_minimum",
                    depth=depth,
                    pair=closest_pair,
                    distance=minimum_distance
                )

    send_event(
        trace_callback,
        "base_complete",
        depth=depth,
        pair=closest_pair,
        distance=minimum_distance
    )

    return closest_pair, minimum_distance


def closest_pair_recursive(px, py, trace_callback=None, depth=0):

    send_event(
        trace_callback,
        "recursive_start",
        depth=depth,
        points=[(x, y) for x, y, index in px]
    )

    # Base case: use brute force for three or fewer points.
    if len(px) <= 3:

        points = [
            (x, y)
            for x, y, index in px
        ]

        pair, distance = closest_pair_brute_force(
            points,
            trace_callback,
            depth
        )

        send_event(
            trace_callback,
            "recursive_complete",
            depth=depth,
            pair=pair,
            distance=distance
        )

        return pair, distance

    # Divide the points into left and right halves.
    mid = len(px) // 2

    left_x = px[:mid]
    right_x = px[mid:]

    mid_x = px[mid][0]

    left_ids = set(
        point[2]
        for point in left_x
    )

    left_y = [
        point
        for point in py
        if point[2] in left_ids
    ]

    right_y = [
        point
        for point in py
        if point[2] not in left_ids
    ]

    send_event(
        trace_callback,
        "divide",
        depth=depth,
        mid_x=mid_x,
        left_points=[(x, y) for x, y, index in left_x],
        right_points=[(x, y) for x, y, index in right_x]
    )

    # Find the closest pair in the left half.
    left_pair, left_distance = closest_pair_recursive(
        left_x,
        left_y,
        trace_callback,
        depth + 1
    )

    # Find the closest pair in the right half.
    right_pair, right_distance = closest_pair_recursive(
        right_x,
        right_y,
        trace_callback,
        depth + 1
    )

    # Select the smaller distance from both halves.
    if left_distance < right_distance:

        minimum_pair = left_pair
        minimum_distance = left_distance

    else:

        minimum_pair = right_pair
        minimum_distance = right_distance

    send_event(
        trace_callback,
        "combine",
        depth=depth,
        left_distance=left_distance,
        right_distance=right_distance,
        pair=minimum_pair,
        distance=minimum_distance
    )

    # Create a strip around the middle dividing line.
    strip = []

    for point in py:

        if abs(point[0] - mid_x) < minimum_distance:
            strip.append(point)

    send_event(
        trace_callback,
        "strip",
        depth=depth,
        mid_x=mid_x,
        minimum_distance=minimum_distance,
        strip=[(x, y) for x, y, index in strip]
    )

    # Compare each point with the next seven points in the strip.
    for i in range(len(strip)):

        for j in range(
            i + 1,
            min(i + 8, len(strip))
        ):

            point1 = (
                strip[i][0],
                strip[i][1]
            )

            point2 = (
                strip[j][0],
                strip[j][1]
            )

            distance = calculate_distance(
                point1,
                point2
            )

            send_event(
                trace_callback,
                "strip_compare",
                depth=depth,
                point1=point1,
                point2=point2,
                distance=distance
            )

            if distance < minimum_distance:

                minimum_distance = distance

                minimum_pair = (
                    point1,
                    point2
                )

                send_event(
                    trace_callback,
                    "new_minimum",
                    depth=depth,
                    pair=minimum_pair,
                    distance=minimum_distance
                )

    send_event(
        trace_callback,
        "recursive_complete",
        depth=depth,
        pair=minimum_pair,
        distance=minimum_distance
    )

    return minimum_pair, minimum_distance


def closest_pair(points, trace_callback=None):

    if len(points) < 2:
        raise ValueError("At least two points are required.")

    indexed_points = [
        (point[0], point[1], index)
        for index, point in enumerate(points)
    ]

    # Sort points by X-coordinate and Y-coordinate.
    px = sorted(
        indexed_points,
        key=lambda point: point[0]
    )

    py = sorted(
        indexed_points,
        key=lambda point: point[1]
    )

    send_event(
        trace_callback,
        "algorithm_start",
        total_points=len(points)
    )

    result = closest_pair_recursive(
        px,
        py,
        trace_callback
    )

    send_event(
        trace_callback,
        "algorithm_complete",
        pair=result[0],
        distance=result[1]
    )

    return result


# Testing
if __name__ == "__main__":

    points = [
        (0, 0),
        (0, 5),
        (0, 2),
        (0, 3),
        (5, 5),
        (5, 6)
    ]

    pair, distance = closest_pair(points)

    print("Closest Pair:", pair)
    print("Minimum Distance:", distance)
    print("Time Complexity: O(n log n)")
