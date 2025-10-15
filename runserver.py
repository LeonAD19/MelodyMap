#!/usr/bin/env python -B
# Instructions for running and debugging this python file in VSCode
# The program assumes that you have python3 and pip3 installed on your machine.
# In the VSCode terminal window type the following:
#    pip3 install -r requirements.txt
# In VSCode, press Cmd-Shift-P (on Mac) or Ctrl-Shift-P (on Windows).
#   In the command selection text box, type "Python Create"
#   From the options dropdown select "Python Create Environment"
#   From the next options dropdown select "venv"

# After the above and setting up the database, you should be able to run and debug this program
import sys 
sys.dont_write_bytecode = True
from flask_folder import create_app

app = create_app()

if __name__ == "__main__":      # if hosted locally
    print("===Running locally===")
    app.run(host="127.0.0.1", port=5000, debug=True)