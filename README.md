# DAA Closest Pair and Karatsuba Project

A Python implementation of two divide-and-conquer algorithms for the **CS302 – Design and Analysis of Algorithms** project:

1. **Closest Pair of Points** using a divide-and-conquer approach.
2. **Integer Multiplication** using the Karatsuba algorithm.

The project also includes random dataset generation, execution-time experiments, CSV result files, and a graphical user interface built with Tkinter.

## Features

- Finds the closest pair among a set of 2D points.
- Multiplies large integers using Karatsuba multiplication.
- Generates 10 input datasets for each algorithm.
- Runs experiments and records execution times in CSV files.
- Displays algorithm results and performance charts in a desktop GUI.
- Allows the user to select an input dataset from the GUI.

## Algorithms and Complexity

| Algorithm | Approach | Time Complexity |
|---|---|---|
| Closest Pair of Points | Divide and Conquer | O(n log n) |
| Karatsuba Integer Multiplication | Divide and Conquer | O(n^log₂3), approximately O(n^1.585) |

Here, **n** represents the number of points for Closest Pair and the number of digits in the operands for Karatsuba.

## Project Structure

```text
DAA_Project_02/
├── algorithms/
│   ├── __init__.py
│   ├── closest_pair.py
│   └── integer_multiplication.py
├── datasets/
│   ├── closest_pair/
│   │   ├── cp_01.txt
│   │   └── ... cp_10.txt
│   └── integer_multiplication/
│       ├── im_01.txt
│       └── ... im_10.txt
├── results/
│   ├── closest_pair_results.csv
│   └── integer_multiplication_results.csv
├── gui/
│   ├── __init__.py
│   └── app.py
├── generate_datasets.py
├── run_experiments.py
├── main.py
├── README.md
└── .gitignore
```

## Requirements

- Python 3.10 or later
- Tkinter (normally included with the standard Python installation)

The project uses Python standard-library modules and does not require additional third-party packages.

## How to Run

Open a terminal in the project directory.

### 1. Launch the GUI

On Windows:

```bash
py main.py
```

The GUI provides these sections:

- **Dashboard** – project overview and dataset information.
- **Closest Pair** – select a point dataset and run the algorithm.
- **Integer Multiplication** – select an operand dataset and run Karatsuba multiplication.
- **Performance Analysis** – view execution-time charts generated from the CSV results.
- **About Project** – project and algorithm information.

### 2. Generate Datasets

To generate the 10 datasets for each algorithm:

```bash
py generate_datasets.py
```

The generator creates input sizes from 200 to 1,100:

- Closest Pair: 10 files containing 200–1,100 points.
- Integer Multiplication: 10 files containing operands of 200–1,100 digits.

**Note:** Running the dataset generator again replaces the existing generated dataset files.

### 3. Run Performance Experiments

After generating the datasets, run:

```bash
py run_experiments.py
```

The script executes both algorithms on their respective datasets and saves the measured execution times and results in:

- `results/closest_pair_results.csv`
- `results/integer_multiplication_results.csv`

The multiplication experiment also checks the Karatsuba result against Python's built-in integer multiplication.

## Dataset Formats

### Closest Pair

Each file starts with the number of points. Every following line contains the x and y coordinates of one point.

Example:

```text
4
2 3
12 30
40 50
5 1
```

### Integer Multiplication

Each file contains two large integer operands, one per line.

Example:

```text
12345678901234567890
98765432109876543210
```

## Technologies Used

- **Language:** Python
- **GUI:** Tkinter
- **Data storage:** Text files and CSV
- **Version control:** Git and GitHub

## Notes

- Run commands from the project root directory.
- The GUI reads the datasets and experiment results stored in the project folders.
- If you regenerate datasets, run the experiments again to refresh the CSV result files and performance charts.

## Academic Project

**Course:** CS302 – Design and Analysis of Algorithms  
**Project:** Closest Pair of Points and Integer Multiplication  
**Semester:** Fall 2026
