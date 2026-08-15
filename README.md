# RMP Lookup Tool for Houston City College (HCC)

This is a Python-based desktop application designed specifically for Houston City College (HCC) students to bulk-query RateMyProfessors (RMP) ratings. It uses a JavaScript snippet to extract professor names directly from the HCC course catalog and fetches their RMP statistics via a graphical interface.

## Disclaimer

This project is strictly for educational and research purposes. It is not affiliated with or endorsed by RateMyProfessors or Houston City College. Users are responsible for complying with the target platform's Terms of Service. The code is provided "AS IS" without any liability. 

## Prerequisites

* Python 3.x installed on your system.
* MacOS or Windows operating system.

## Installation

1. Clone this repository to your local machine.
2. Navigate to the project directory.
3. Create and activate a virtual environment.
4. Install the required dependencies using pip.

    ```bash
    git clone <Your-Repository-URL>
    cd <Your-Directory-Name>
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

## Usage Instructions

1. Navigate to the Houston City College course search portal in your web browser.
2. Press F12 (or Cmd+Option+I on Mac) to open the Developer Tools, and switch to the "Console" tab.
3. Run the desktop application using the command: `python app.py`.
4. Click the "Copy JS Extraction Code" button in the application, paste it into your browser's Console, and press Enter.
5. Paste the copied output directly into the text box of the Python application.
6. Click "Search Ratings" to view the statistics.

## License

This project is licensed under the MIT License. See the LICENSE file for details.