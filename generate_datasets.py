import os
import random

# Project directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CLOSEST_PAIR_DIR = os.path.join(
    BASE_DIR, "datasets", "closest_pair"
)
INTEGER_MULTIPLICATION_DIR = os.path.join(
    BASE_DIR, "datasets", "integer_multiplication"
)

# Dataset configuration
INPUT_SIZES = [200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100]
RANDOM_SEED = 42
# Karatsuba operands will have varying digit lengths
KARATSUBA_DIGIT_SIZES = [110, 120, 130, 140, 150,
                         160, 170, 180, 190, 200]

# Use a fixed seed for reproducible datasets
random.seed(RANDOM_SEED)

def create_directories():
    os.makedirs(CLOSEST_PAIR_DIR, exist_ok=True)
    os.makedirs(INTEGER_MULTIPLICATION_DIR, exist_ok=True)


def random_integer_with_digits(digits):
    # Random integer with exactly `digits` digits (first digit is never 0).
    return random.randint(10 ** (digits - 1), 10 ** digits - 1)


def generate_closest_pair_datasets():
    print("\nGenerating Closest Pair datasets...")

    for index, size in enumerate(INPUT_SIZES, start=1):

        filename = f"cp_{index:02d}.txt"
        filepath = os.path.join(CLOSEST_PAIR_DIR, filename)

        points = []

        for _ in range(size):
            x = round(random.uniform(-1000, 1000), 2)
            y = round(random.uniform(-1000, 1000), 2)

            points.append((x, y))

        with open(filepath, "w") as file:

            file.write(f"{size}\n")

            for x, y in points:
                file.write(f"{x} {y}\n")

        print(f"Created {filename} with {size} points")


def generate_integer_multiplication_datasets():
    print("\nGenerating Karatsuba datasets...")

    for index, digits in enumerate(KARATSUBA_DIGIT_SIZES, start=1):

        filename = f"im_{index:02d}.txt"
        filepath = os.path.join(
            INTEGER_MULTIPLICATION_DIR,
            filename
        )

        # Generate two integers, each with the required number of digits
        x = random_integer_with_digits(digits)
        y = random_integer_with_digits(digits)

        with open(filepath, "w") as file:

            file.write(f"{x}\n")
            file.write(f"{y}\n")

        print(f"Created {filename}: two {digits}-digit integers")


def main():

    print("=" * 50)
    print("       DAA PROJECT DATASET GENERATOR")
    print("=" * 50)

    create_directories()

    generate_closest_pair_datasets()

    generate_integer_multiplication_datasets()

    print("\n" + "=" * 50)
    print("All datasets generated successfully!")
    print(f"Closest Pair datasets: {len(INPUT_SIZES)}")
    print(f"Karatsuba datasets: {len(KARATSUBA_DIGIT_SIZES)}")
    print(f"Karatsuba operand sizes: {KARATSUBA_DIGIT_SIZES[0]} to "
          f"{KARATSUBA_DIGIT_SIZES[-1]} digits")
    print("=" * 50)


if __name__ == "__main__":
    main()