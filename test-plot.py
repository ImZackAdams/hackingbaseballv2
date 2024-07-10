import matplotlib.pyplot as plt
import os
import sys


def create_simple_plot():
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")

    plt.figure(figsize=(6, 4))
    plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
    plt.title("Simple Test Plot")

    file_path = os.path.join(os.getcwd(), 'test_plot.png')
    print(f"Attempting to save plot to: {file_path}")

    try:
        plt.savefig(file_path)
        print(f"Plot saved successfully")
    except Exception as e:
        print(f"Error saving plot: {e}")

    plt.close()

    if os.path.exists(file_path):
        print(f"File created successfully at {file_path}")
        print(f"File size: {os.path.getsize(file_path)} bytes")
    else:
        print(f"File was not created at {file_path}")

    print("\nContents of current directory:")
    for file in os.listdir(os.getcwd()):
        print(file)


if __name__ == "__main__":
    create_simple_plot()
