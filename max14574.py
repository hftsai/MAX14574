#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from utility import UTILITY
from const import POWERON, POWEROFF

class MAX14574():
    u = UTILITY()
    
    def __init__( self, device, addr=0x77, intSensor=True, fstu=0, il=0 ):
        """ MAX14574 chip initilization

        device - I2C port Number, i.e. for "/dev/i2c-8" it should be "8"; 
        addr - chip base address [0:127]; 
        intSensor - internal termosensor [True:False];
        fstu - startup time configuration [0:3] (see datasheet);
        il - inductior current limit [0:3] (see datasheet); 
        Raises: ERRORIO exception  """
        self.intSensor = intSensor
        self.fstu = fstu
        self.il = il
        self.u.init(device, addr, intSensor, fstu, il)
       
    def start(self):
        """ Turn On chip and output voltage 

        Returns: - none 
        Raises: ERRORIO exception  """
        self.u.setup(POWERON)
    
    def stop(self):
        """ Turn Off chip and output voltage
        
        Returns: - none 
        Raises: ERRORIO exception  """
        self.u.setup(POWEROFF)

    def status(self):
        """ Check is chip in active state

        Returns: True if active 
        Raises: ERRORIO exception  """
        isActive = self.u.status()
        return isActive
    
    def checkFault(self):
        """ Check fault status procedure
        
        Note: this procedure takes 2ms or more and tread will be blocked!
        Returns: 
        ll_th=True if thermal shutdown
        bst_fail=True if voltage boost < 70V
        circuit_fails[6:0] bits are follwing:
            [FAIL_OP, FAIL_SH, COM_FAIL, LL[4:1]_FAIL]
            i.e. sensor_fail[bit6]=FAIL_OP, sensor_fail[bit5]=FAIL_SH and so on 
        errorsStr -string with all errors decription. String empty, if no errors 
        Raises: ERRORIO exception  """
        ll_th, bst_fail, circuit_fails, errorsStr = self.u.checkFault()
        return ll_th, bst_fail, circuit_fails, errorsStr
    
    def temperature(self):
        """ Get temperature in Celsius for internal Sensor
        
        Returns:
            If internal sensor:
                tempC, rawVal
                where tempC - temperature in float format; rawVal - raw value according to datasheet
            Return -273 if sensor failed 
            If external sensor:
                byte [0:255] for external Sensor.
        Calculates for internal Sensor as following:
            Tj = ((TS - 127)*1.6) - 60
            if TS = 0x7F then Tj = -60C; if TS = 0xFF then Tj = 145C
        Raises: ERRORIO exception  """
        tempC, ravWal = self.u.temperature()
        return tempC, ravWal

    def setLLVAll(self, llv1,llv2, llv3, llv4, doUpdate=True):
        """ Setup output volatage for all 4 channels
        
        Arguments:
        llv format is 10 bits [0:1023]
        If llv=0 then Vrms=24.4V
        If llv=1023 then Vrms=69.7V
        Flag doUpdate set to True for normal work
        If doUpdate=False then llv does not updated
        Returns: None
        Raises: ERRORIO exception  """
        self.u.setLLVAll(llv1,llv2, llv3, llv4, doUpdate)

    def setLLV(self, ch, llv, doUpdate):
        """ Setup output volatage for one channel
        
        Arguments:
        ch - Channnel Number [1:4] 
        llv format is 10 bits [0:1023]
        If llv=0 then Vrms=24.4V
        If llv=1023 then Vrms=69.7V
        Flag doUpdate set to True for normal work
        If doUpdate=False then llv does not updated
        Returns: None
        Raises: ERRORIO exception  """
        self.u.setLLV(ch, llv, doUpdate)

    def getLLV(self):
        """ Get output setup values

        Returns: llv format is 10 bits [0:1023] 
        Raises: ERRORIO exception  """
        llv1, llv2, llv3, llv4 = self.u.getLLV()
        return llv1, llv2, llv3, llv4

    def setVoltageAll(self, v1,v2, v3, v4, doUpdate=True):
        """ Setup output volatage for all 4 channels
        
        Arguments:
        v format is float [24.4:69.7] in Volts
        If v < VOLT_MIN then v=VOLT_MIN
        If v > VOLT_MAX then v=VOLT_MAX
        Flag doUpdate set to True for normal work
        If doUpdate=False then v does not updated
        Returns: None
        Raises: ERRORIO exception  """
        self.u.setVoltageAll(v1,v2, v3, v4, doUpdate)
        
    def setVoltage(self, ch, v, doUpdate=True):
        """ Send Voltage Value for one channel
        
        Arguments:
        ch - Channnel Number [1:4] 
        v format is float [24.4:69.7] in Volts
        If v < VOLT_MIN then v=VOLT_MIN
        If v > VOLT_MAX then v=VOLT_MAX
        Flag doUpdate set to True for normal work
        If doUpdate=False then v does not updated
        Returns: None
        Raises: ERRORIO exception """
        self.u.setVoltage(ch, v, doUpdate)


    def getVoltageAll (self):
        """ Get output setup values

        Returns: v in float format
        v = llv * 0.0445 + 24.4
        Raises: ERRORIO exception  """
        v1, v2, v3, v4 = self.u.getVoltage()
        return v1, v2, v3, v4

    def llv2Volt(self, llv):
        return self.u.llv2Volt(llv)

    def volt2LLV(self, v):
        return self.u.volt2LLV(v)

if __name__ == '__main__':
    # test format: 
    # python3 max14574.py <device__bus#> <hex_device_address>
    print(f'arguments: 1st={sys.argv[1]} 2nd={int(sys.argv[2],16)}')
    mm = MAX14574 (int(sys.argv[1]), int(sys.argv[2], 16), True, 0x0, 0x0)
    mm.start()
#    mm.stop()
    print (f'status={mm.status()}')
    print (f'temperature={mm.temperature()}')
    mm.setLLVAll(900,200,300,400, True)
    llv1, llv2, llv3, llv4 = mm.getLLV()
    print(f'llv1/2/3/4 = {llv1} {llv2} {llv3} {llv4}')
    ll_th, bst_fail, circuit_fails, errorsStr = mm.checkFault()
    print(f'checkFault() ll_th, bst_fail, circuit_fails, errorsStr{ll_th, bst_fail, circuit_fails, errorsStr}')

