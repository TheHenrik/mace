# Installation:

## WINDOWS

1. Install Python 3.11.X 64bit
1. Download the .zip or clone the repository
1. Extract and rename the folder to "mace"
1. Move into the folder
1. Press "Strg"+"L" and type "cmd" + Enter
1. run one after the other:

    ```sh
    python3.11 -m venv .venv
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

### Troubleshooting

1. Matlab won't install:

    Try: ```pip install -U matplotlib --prefer-binary```

1. Scipy won't install:

    Is it really 64bit Python? 

    Try installing a gcc compiler.
    
1. Try installing "wheel" using pip

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

## Apple macOS

Rethink your life choices and then talk to Jannik
