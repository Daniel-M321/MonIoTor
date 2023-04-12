# MonIoTor

This is the application code for my raspberry pi. This code contains the logic for connecting to my sensors and reading the data, eventhandlers that are activated on alarming data and the process of sending the sensor data to an influx database stored on AWS.

## Tests
Inside the updateMyStuff bat and sh file, the requirements are installed, the type checker is called on the program and lastly the unit tests are ran with a coverage report.

## Main
The main file consists of the loop that run throughs the sensors, eventhandlers and database writing. The calibration for the sensors can be switched out with the boolean before the loop. 

## Fixes

- For testing outside the raspberry pi:<br>
    <p style="color:blue">board:</p> ("C:\collegeGitProjects\iot_system\MonIoTor\venv\Lib\site-packages\board.py")<br>
        When checking for board_id, put a `pass` where check is board_id == None.<br>
    <p style="color:blue">import uname:</p> ("C:\collegeGitProjects\iot_system\MonIoTor\venv\Lib\site-packages\adafruit_dht.py")<br>
        Not supported by windows, replace `from os import uname` with `from platform import uname`

- Set up env variables
