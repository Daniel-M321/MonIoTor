# adapted from sandboxelectronics.com/?p=165

import time
import math
from gpiozero import MCP3008            # type: ignore


class MQ:
    ######################### Hardware Related Macros #########################
    MQ_PIN = 0  # analog input channel (MCP3008)
    RL_VALUE = 5  # define the load resistance on the board, in kilo ohms  #todo find this
    RO_CLEAN_AIR_FACTOR = 9.83  # RO_CLEAR_AIR_FACTOR=(Sensor resistance in clean air)/RO,
    # which is derived from the chart in datasheet https://www.elecrow.com/download/MQ-2.pdf

    ######################### Software Related Macros #########################
    CALIBARAION_SAMPLE_TIMES = 50  # samples to take in the calibration phase
    CALIBRATION_SAMPLE_INTERVAL = 500  # time interval(in millisecond) between samples in the calibration phase
    READ_SAMPLE_INTERVAL = 50  # time interval(in millisecond) between each samples in normal operation
    READ_SAMPLE_TIMES = 5  # define how many samples you are going to take in normal operation

    ######################### Application Related Macros ######################
    GAS_LPG = 0
    GAS_CO = 1
    GAS_SMOKE = 2

    def __init__(
            self,
            Ro: int = 10,
            analogPin: int = 0,
            READ_SAMPLE_INTERVAL: int = 50,
            CALIBRATION_SAMPLE_INTERVAL: int = 500
    ):
        self.Ro = Ro
        self.MQ_PIN = analogPin
        self.adc = MCP3008(channel=self.MQ_PIN, clock_pin=18, mosi_pin=15, miso_pin=17, select_pin=14)
        self.READ_SAMPLE_INTERVAL = READ_SAMPLE_INTERVAL
        self.CALIBRATION_SAMPLE_INTERVAL = CALIBRATION_SAMPLE_INTERVAL

        self.LPGCurve = [2.3, 0.21, -0.47]  # two points are taken from the curve.
        # with these two points, a line is formed which is "approximately equivalent"
        # to the original curve.
        # data format:{ x, y, slope}; point1: (lg200, 0.21), point2: (lg10000, -0.59)
        self.COCurve = [2.3, 0.72, -0.34]  # two points are taken from the curve.
        # with these two points, a line is formed which is "approximately equivalent"
        # to the original curve.
        # data format:[ x, y, slope]; point1: (lg200, 0.72), point2: (lg10000,  0.15)
        self.SmokeCurve = [2.3, 0.53, -0.44]  # two points are taken from the curve.
        # with these two points, a line is formed which is "approximately equivalent"
        # to the original curve.
        # data format:[ x, y, slope]; point1: (lg200, 0.53), point2: (lg10000,  -0.22)

        print("Calibrating MQ-2...")
        self.Ro = self.MQCalibration()
        print("MQ-2 Calibration is done...\n")
        print("Ro=%f kohm" % self.Ro)

    ######################### MQCalibration ####################################
    # Input:   mq_pin - analog channel
    # Output:  Ro of the sensor
    # Remarks: This function assumes that the sensor is in clean air. It use
    #          MQResistanceCalculation to calculates the sensor resistance in clean air
    #          and then divides it with RO_CLEAN_AIR_FACTOR. RO_CLEAN_AIR_FACTOR is about
    #          10, which differs slightly between different sensors.
    ############################################################################
    def MQCalibration(self):
        val = 0.0
        for i in range(self.CALIBARAION_SAMPLE_TIMES):  # take multiple samples
            val += self.MQResistanceCalculation(self.adc.voltage)
            time.sleep(self.CALIBRATION_SAMPLE_INTERVAL / 1000.0)

        val = val / self.CALIBARAION_SAMPLE_TIMES  # calculate the average value

        val = val / self.RO_CLEAN_AIR_FACTOR  # divided by RO_CLEAN_AIR_FACTOR yields the Ro
        # according to the chart in the datasheet

        return val

    #########################  MQRead ##########################################
    # Input:   mq_pin - analog channel
    # Output:  Rs of the sensor
    # Remarks: This function use MQResistanceCalculation to calculate the sensor resistence (Rs).
    #          The Rs changes as the sensor is in the different concentration of the target
    #          gas. The sample times and the time interval between samples could be configured
    #          by changing the definition of the macros.
    ############################################################################
    def MQRead(self):
        rs = 0.0

        for i in range(self.READ_SAMPLE_TIMES):
            rs += self.MQResistanceCalculation(self.adc.voltage)
            time.sleep(self.READ_SAMPLE_INTERVAL / 1000.0)

        rs = rs / self.READ_SAMPLE_TIMES

        return rs

    def MQPercentage(self):
        val = {}
        read_val = self.MQRead()
        val["GAS_LPG"] = self.MQGetGasPercentage(read_val/self.Ro, self.GAS_LPG)
        val["CO"] = self.MQGetGasPercentage(read_val/self.Ro, self.GAS_CO)
        val["SMOKE"] = self.MQGetGasPercentage(read_val/self.Ro, self.GAS_SMOKE)
        return val

    ######################### MQResistanceCalculation #########################
    # Input:   raw_adc - raw value read from adc, which represents the voltage
    # Output:  the calculated sensor resistance
    # Remarks: The sensor and the load resistor forms a voltage divider. Given the voltage
    #          across the load resistor and its resistance, the resistance of the sensor
    #          could be derived.
    ############################################################################
    def MQResistanceCalculation(self, raw_adc):
        return float(self.RL_VALUE * (1023.0 - raw_adc) / float(raw_adc))

    #########################  MQGetGasPercentage ##############################
    # Input:   rs_ro_ratio - Rs divided by Ro
    #          gas_id      - target gas type
    # Output:  ppm of the target gas
    # Remarks: This function passes different curves to the MQGetPercentage function which
    #          calculates the ppm (parts per million) of the target gas.
    ############################################################################
    def MQGetGasPercentage(self, rs_ro_ratio: float, gas_id: int):
        if gas_id == self.GAS_LPG:
            return self.MQPercentageCalc(rs_ro_ratio, self.LPGCurve)
        elif gas_id == self.GAS_CO:
            return self.MQPercentageCalc(rs_ro_ratio, self.COCurve)
        elif gas_id == self.GAS_SMOKE:
            return self.MQPercentageCalc(rs_ro_ratio, self.SmokeCurve)
        return 0

    #########################  MQGetPercentage #################################
    # Input:   rs_ro_ratio - Rs divided by Ro
    #          pcurve      - pointer to the curve of the target gas
    # Output:  ppm of the target gas
    # Remarks: By using the slope and a point of the line. The x(logarithmic value of ppm)
    #          of the line could be derived if y(rs_ro_ratio) is provided. As it is a
    #          logarithmic coordinate, power of 10 is used to convert the result to non-logarithmic
    #          value.
    ############################################################################
    def MQPercentageCalc(self, rs_ro_ratio: float, pcurve: list[float]):
        return math.pow(10, (((math.log(rs_ro_ratio) - pcurve[1]) / pcurve[2]) + pcurve[0]))
