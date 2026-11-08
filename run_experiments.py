
import os
import csv
import time
import io
from contextlib import redirect_stdout

# Import algorithms without displaying their testing output
with redirect_stdout(io.StringIO()):
    from algorithms.closest_pair import closest_pair
    from algorithms.integer_multiplication import karatsuba_multiply


CLOSEST_PAIR_FOLDER = "datasets/closest_pair"
INTEGER_MULTIPLICATION_FOLDER = "datasets/integer_multiplication"
RESULTS_FOLDER = "results"


def run_closest_pair_experiments():

    filename = os.path.join(RESULTS_FOLDER, "closest_pair_results.csv")

    with open(filename, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Dataset",
            "Input Size",
            "Execution Time (seconds)",
            "Closest Pair",
            "Minimum Distance"
        ])

        for name in sorted(os.listdir(CLOSEST_PAIR_FOLDER)):

            if name.endswith(".txt"):

                filepath = os.path.join(CLOSEST_PAIR_FOLDER, name)

                with open(filepath, "r") as dataset:

                    size = int(dataset.readline())

                    points = []

                    for line in dataset:
                        x, y = map(int, line.split())
                        points.append((x, y))

                start_time = time.perf_counter()

                pair, distance = closest_pair(points)

                end_time = time.perf_counter()

                execution_time = end_time - start_time

                writer.writerow([
                    name,
                    size,
                    "{:.10f}".format(execution_time),
                    str(pair),
                    distance
                ])

                print("Dataset: " + name)
                print("Input Size: " + str(size))
                print("Execution Time: " + str(execution_time) + " seconds")
                print("Minimum Distance: " + str(distance))
                print("-----------------------------")

    print("\nClosest Pair experiments completed!")


def run_integer_multiplication_experiments():

    filename = os.path.join(RESULTS_FOLDER, "integer_multiplication_results.csv")

    with open(filename, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Dataset",
            "Input Size",
            "Execution Time (seconds)",
            "Multiplication Result",
            "Correct Result"
        ])

        for name in sorted(os.listdir(INTEGER_MULTIPLICATION_FOLDER)):

            if name.endswith(".txt"):

                filepath = os.path.join(INTEGER_MULTIPLICATION_FOLDER, name)

                with open(filepath, "r") as dataset:

                    num1 = int(dataset.readline().strip())
                    num2 = int(dataset.readline().strip())

                input_size = len(str(num1))

                start_time = time.perf_counter()

                result = karatsuba_multiply(num1, num2)

                end_time = time.perf_counter()

                execution_time = end_time - start_time

                correct_result = result == num1 * num2

                writer.writerow([
                    name,
                    input_size,
                    "{:.10f}".format(execution_time),
                    str(result),
                    correct_result
                ])

                print("Dataset: " + name)
                print("Input Size: " + str(input_size) + " digits")
                print("Execution Time: " + str(execution_time) + " seconds")
                print("Correct Result: " + str(correct_result))
                print("-----------------------------")

    print("\nInteger Multiplication experiments completed!")


def main():

    os.makedirs(RESULTS_FOLDER, exist_ok=True)

    print("Starting Closest Pair experiments...\n")

    run_closest_pair_experiments()

    print("\nStarting Integer Multiplication experiments...\n")

    run_integer_multiplication_experiments()

    print("\nAll experiments completed successfully!")
    print("Results saved in the results folder.")


if __name__ == "__main__":
    main()
