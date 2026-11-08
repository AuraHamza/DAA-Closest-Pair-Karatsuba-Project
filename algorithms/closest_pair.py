import math
def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def closest_pair_brute_force(points):
    minimum_distance = float('inf')
    closest_pair = None

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            distance = calculate_distance(points[i], points[j])

            if distance < minimum_distance:
                minimum_distance = distance
                closest_pair = (points[i], points[j])

    return closest_pair, minimum_distance


def closest_pair_recursive(px, py):
    if len(px) <= 3:
        points = [(x, y) for x, y, index in px]
        return closest_pair_brute_force(points)

    mid = len(px) // 2

    left_x = px[:mid]
    right_x = px[mid:]

    mid_x = px[mid][0]

    left_ids = set(point[2] for point in left_x)

    left_y = [point for point in py if point[2] in left_ids]
    right_y = [point for point in py if point[2] not in left_ids]

    left_pair, left_distance = closest_pair_recursive(left_x, left_y)

    right_pair, right_distance = closest_pair_recursive(right_x, right_y)

    if left_distance < right_distance:
        minimum_pair = left_pair
        minimum_distance = left_distance
    else:
        minimum_pair = right_pair
        minimum_distance = right_distance

    strip = []

    for point in py:
        if abs(point[0] - mid_x) < minimum_distance:
            strip.append(point)

    for i in range(len(strip)):
        for j in range(i + 1, min(i + 8, len(strip))):

            point1 = (strip[i][0], strip[i][1])
            point2 = (strip[j][0], strip[j][1])

            distance = calculate_distance(point1, point2)

            if distance < minimum_distance:
                minimum_distance = distance
                minimum_pair = (point1, point2)

    return minimum_pair, minimum_distance


def closest_pair(points):

    indexed_points = [
        (point[0], point[1], index)
        for index, point in enumerate(points)
    ]

    px = sorted(indexed_points, key=lambda point: point[0])
    py = sorted(indexed_points, key=lambda point: point[1])

    return closest_pair_recursive(px, py)

# Testing
points = [
    (0, 0), (0, 5), (0, 2),
    (0, 3), (5, 5), (5, 6)
]
pair, distance = closest_pair(points)
print("Closest Pair:", pair)
print("Minimum Distance:", distance)
print("Time Complexity: O(n log n)")