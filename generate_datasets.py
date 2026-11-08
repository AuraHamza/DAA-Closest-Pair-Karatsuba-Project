
import os
import random


CLOSEST_PAIR_FOLDER = "datasets/closest_pair"
INTEGER_MULTIPLICATION_FOLDER = "datasets/integer_multiplication"


INPUT_SIZES = [200, 300, 400, 500, 600,
               700, 800, 900, 1000, 1100]

def generate_closest_pair_datasets():

    os.makedirs(CLOSEST_PAIR_FOLDER, exist_ok=True)

    for index, size in enumerate(INPUT_SIZES, start=1):

        filename = "cp_" + str(index).zfill(2) + ".txt"
        filepath = os.path.join(CLOSEST_PAIR_FOLDER, filename)

        with open(filepath, "w") as file:

            file.write(str(size) + "\n")

            for i in range(size):

                x = random.randint(-100000, 100000)
                y = random.randint(-100000, 100000)

                file.write(str(x) + " " + str(y) + "\n")

        print("Generated: " + filename + " (" + str(size) + " points)")


def generate_integer_multiplication_datasets():

    os.makedirs(INTEGER_MULTIPLICATION_FOLDER, exist_ok=True)

    for index, size in enumerate(INPUT_SIZES, start=1):

        filename = "im_" + str(index).zfill(2) + ".txt"
        filepath = os.path.join(INTEGER_MULTIPLICATION_FOLDER, filename)

        with open(filepath, "w") as file:

            first_number = str(random.randint(1, 9))

            for i in range(size - 1):
                first_number += str(random.randint(0, 9))

            second_number = str(random.randint(1, 9))

            for i in range(size - 1):
                second_number += str(random.randint(0, 9))

            file.write(first_number + "\n")
            file.write(second_number + "\n")

        print("Generated: " + filename + " (" + str(size) + "-digit operands)")


def main():

    random.seed(42)

    print("Generating Closest Pair datasets...")
    generate_closest_pair_datasets()

    print("\nGenerating Integer Multiplication datasets...")
    generate_integer_multiplication_datasets()

    print("\nAll 20 datasets generated successfully!")


if __name__ == "__main__":
    main()
