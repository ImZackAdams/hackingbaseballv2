# Hacking Baseball

## Overview
Hacking Baseball is an application that predicts the outcome of a baseball games and provides users with the best odds from local score books.

## Prerequisites
Before you begin, ensure you have met the following requirements:
- You have installed [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).


## Environment Setup

1. Clone the repository:
    ```sh
    git clone git@github.com:JackHalley/hackingbaseballv2.git
    cd hackingbaseballv2
    ```

2. Create a new Conda environment using the `environment.yml` file:
    ```sh
    conda env create -f environment.yml
    ```

3. Activate the environment:
    ```sh
    conda activate hbv2
    ```

4. Install the dependencies from `requirements.txt`:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration
- Set the required environment variables. You can create a `.env` file in the root directory of the project with the following content:
    ```env
    FLASK_APP=app.py
    FLASK_ENV=development
    ```

## Running the Application
To run the Flask application, use the following command:
```sh
flask run
