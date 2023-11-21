# Installation

## WINDOWS

1. Install Python 3.11.X 64bit
1. During the installation process click the button "Add to path"
1. Download the .zip or clone the repository (skip the next step)
1. Extract and rename the folder to "mace"
1. Move into the folder
1. Press "Strg"+"L" and type "cmd" and hit Enter
1. run one after the other:

    ```sh
    python -m venv .venv
    .venv\Scripts\activate
    pip install -e .[dev]
    ```

1. Now run the following command replacing "0" with the given number:

    ```sh
    .venv\Scripts\python RUN_IN_PYCHARM\ACC24_Baseline\main.py 0
    ```

1. Wait for the program to finish
1. Upload the created .csv file in RUN_IN_PYCHARM/ACC24_Baseline/ to the Google Drive
1. Repeat from step 7 until all numbers are taken.
1. After closing the console you only need to rerun

    ```sh
    .venv\Scripts\activate
    ```

    and continue from step 7

### Troubleshooting

1. Matplotlib won't install:

    Try: ```pip install -U matplotlib --prefer-binary```

1. Scipy won't install:

    Is it really 64bit Python?

    Try installing a gcc compiler.

1. Try installing "wheel" using pip

1. Replace

    ```sh
    python -m venv venv
    ```

    with

    ```sh
    path\to\python\installation\python.exe -m venv   .venv
    ```

## Linux

1. Install Python 3.11.X 64bit
1. Download the .zip or clone the repository
1. Extract and rename the folder to "mace"
1. Move into the folder
1. run one after the other in the console:

    ```sh
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -e .[dev]
    ```

1. Now run the following command replacing "0" with the given number:

    ```sh
    .venv/bin/python RUN_IN_PYCHARM/ACC24_Baseline/main.py 0
    ```

1. Wait for the program to finish
1. Upload the created .csv file in RUN_IN_PYCHARM/ACC24_Baseline/ to the Google Drive
1. Repeat from step 7 until all numbers are taken.

## macOS

Rethink your life choices, then talk to Jannik and prey avl works on your machine
