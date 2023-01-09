# MonIoTor

## Fixes

- For testing outside the raspberry pi:<br>
    <p style="color:blue">board:</p> ("C:\collegeGitProjects\iot_system\MonIoTor\venv\Lib\site-packages\board.py")<br>
        When checking for board_id, put a `pass` where check is board_id == None.<br>
    <p style="color:blue">import uname:</p> ("C:\collegeGitProjects\iot_system\MonIoTor\venv\Lib\site-packages\adafruit_dht.py")<br>
        Not supported by windows, replace `from os import uname` with `from platform import uname`

- Set up env variables
