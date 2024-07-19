#!/usr/bin/python3
# -*- coding: utf-8 -*-

import smbus
import os
import sys
import traceback
from const import *

_I2C_ADDR = None
_bus = None
_DEBUG_NOWRITE = False # For debugging without write to I2C should set False

class I2CIOError(Exception):
    pass
#    traceback.print_exc()

class UTILITY():
    def init(self, device, addr, intSensor, fstu, il):
        """ MAX14574 init procedure
        
        Args:
            see __init__()
        Returns: None
        Raises: ERRORIO exception  """
        global _I2C_ADDR 
        global _bus

        _I2C_ADDR = addr
        _bus = smbus.SMBus(device)
        byte = 0
        if(intSensor == True):
            byte = byte | DRIVERCONF_TS_INT
        else:
            byte = byte | DRIVERCONF_TS_EXT
        fstu = (fstu << DRIVERCONF_FSTU_SHIFT) & DRIVERCONF_FSTU_MASK
        byte = byte | fstu
        il = il & DRIVERCONF_IL_MASK
        byte = byte | il
        print(f'init: address={DRIVERCONF} byte=0x{byte:x}')
        self.wByte(DRIVERCONF, byte)

    def rByte(self, addr):
        """ Read byte from add 

        Args: addr [0:1023]
        Returns: byte if OK or raise exception
        Raises: ERRORIO exception """
        byte = _bus.read_byte_data(_I2C_ADDR, addr)
        if (byte < 0):
            raise I2CIOError(os.strerror(-byte))
        return byte

    def wByte(self, addr, byte):
        """ Write byte to addr
            
        Args: 
            addr [0:1023]
            byte
        Returns: No
        Raises: ERRORIO exception  """
        if (_DEBUG_NOWRITE == False):
            _bus.write_byte_data(_I2C_ADDR,addr,byte)
        else:
            print(f'wByte() without write to I2C; addr={addr} byte=0x{byte:x}')

    def checkFault(self):
        """ See API description at max14574.py """

        ll_th = False
        bst_fail = False
        circuit_fails = 0
        errorsStr = ""
        status = 0x01
        self.wByte(CMND, CMND_CHK_FAIL)
        while ( status != 0 ):
            status = self.rByte(CMND) & CMND_CHK_FAIL
        byte = self.rByte(M_STATUS)
        if ( byte & STATUS_LL_TH != 0 ):
            ll_th = True
            errorsStr = errorsStr + "Thermal shutdown event has occurred\r\n"
        if ( byte & STATUS_BST_FAIL != 0 ):
            bst_fail = True
            errorsStr = errorsStr + "B5 bump is not able to reach the Vpeak voltage\r\n"
        byte = self.rByte(FAILRG)
        if ( byte & FAIL_OP != 0 ):
            circuit_fails = circuit_fails | FAIL_OP
            errorsStr = errorsStr + "Open connection detected between the outputs\r\n"
        if ( byte & FAIL_SH != 0 ):
            circuit_fails = circuit_fails | FAIL_SH
            errorsStr = errorsStr + "Short-circuit connection detected between the outputs\r\n"
        if ( byte & FAIL_COM_FAIL != 0 ):
            circuit_fails = circuit_fails | FAIL_COM_FAIL
            errorsStr = errorsStr + "Fail connection detected on the C1 bump (COM)\r\n"
        if ( byte & FAIL_LL_FAIL != 0 ):
            circuit_fails = circuit_fails | FAIL_LL_FAIL
            errorsStr = errorsStr + "Fail connection detected on the C2/C3/C4/C5 bump (LL1/2/3/4)\r\n"
        return ll_th, bst_fail, circuit_fails, errorsStr

    def getLLV(self):
        """ See API description at max14574.py """

        llv1 = llv2 = llv3 = llv4 = 0
        byte = self.rByte(OIS_LSB)
        llv1 = ( (self.rByte(LLV1) <<2) + ( (byte >> 0) & 0x03) ) & 0x3FF
        llv2 = ( (self.rByte(LLV2) <<2) + ( (byte >> 2) & 0x03) ) & 0x3FF
        llv3 = ( (self.rByte(LLV3) <<2) + ( (byte >> 4) & 0x03) ) & 0x3FF
        llv4 = ( (self.rByte(LLV4) <<2) + ( (byte >> 6) & 0x03) ) & 0x3FF
        return llv1, llv2, llv3, llv4

    def setLLVAll(self, llv1,llv2, llv3, llv4, doUpdate):
        """ See API description at max14574.py """

        # llv input format [0:1023] split to two LSBs and eight MSBs
        lsb1 = (llv1 & 0x03) << 0
        lsb2 = (llv2 & 0x03) << 2
        lsb3 = (llv3 & 0x03) << 4
        lsb4 = (llv4 & 0x03) << 6
        byte = lsb1 | lsb2 | lsb3 | lsb4
#        print(f'setLLV() byte=0x{byte:x} lsb1=0x{lsb1:x} lsb2=0x{lsb2:x} lsb3=0x{lsb3:x} lsb4=0x{lsb4:x}')
        self.wByte(OIS_LSB, byte)
        self.wByte(LLV1, (llv1 >> 2) & 0xFF)
        self.wByte(LLV2, (llv2 >> 2) & 0xFF)
        self.wByte(LLV3, (llv3 >> 2) & 0xFF)
        self.wByte(LLV4, (llv4 >> 2) & 0xFF)
        if (doUpdate == True):
            self.wByte(CMND, CMND_UPD_OUT)    

    def setLLV(self, ch, llv, doUpdate):
        """ See API description at max14574.py """

        LLV = LLVLIST[ch-1]
        # llv input format [0:1023] split to two LSBs and eight MSBs
        channel = ch % 4
        byte = (llv & 0x03) << channel*2
#        print(f'setLLV() byte=0x{byte:x} llv={llv} ch={ch}')
        self.wByte(OIS_LSB, byte)
        self.wByte(LLV, (llv >> 2) & 0xFF)
        if (doUpdate == True):
            self.wByte(CMND, CMND_UPD_OUT)    

    def getVoltage(self):
        """ See API description at max14574.py """

        # v = llv * 0.0445 + 24.4
        v1 = v2 = v3 = v4 = 0
        llv1, llv2, llv3, llv4 = self.getLLV()
        v1 = self.llv2Volt(llv1)
        v2 = self.llv2Volt(llv2)
        v3 = self.llv2Volt(llv3)
        v4 = self.llv2Volt(llv4)
        return v1, v2, v3, v4

    def setVoltageAll(self, v1,v2, v3, v4, doUpdate):
        """ See API description at max14574.py """

        # Let calculate 10bits llv code from voltage:
        # v = llv * 0.0445 + 24.4 therefore: llv = (v - 24.4) / 0.0445
        # for example: 
        # v=24.4 llv=(24.4-24.4)/0.0445=0
        # v69.8 llv=(69.9-24.4)/0.0445=1022
        #########################
        llv1 = self.volt2LLV(v1)
        llv2 = self.volt2LLV(v2)
        llv3 = self.volt2LLV(v3)
        llv4 = self.volt2LLV(v4)
        self.setLLVAll(llv1,llv2, llv3, llv4, doUpdate)

    def setVoltage(self, ch, v, doUpdate):
        """ See API description at max14574.py """

        llv = self.volt2LLV(v)
        self.setLLV(ch, llv, doUpdate)

    def setup(self, isPowerON):
        """ Power Turn On/Off

        isPowerON if True then MAX14574 PowerOn. If False then MAX14574 PowerOff
        Returns: None
        Raises: ERRORIO exception """
        if (isPowerON):
            byte = USERMODE_ACTIVE | USERMODE_SM # Active & no-sleep
        else:
            byte = USERMODE_SM # no-sleep, but not active
        self.wByte(USERMODE, byte)
        self.wByte(OIS_LSB, 0)    
        self.wByte(LLV1, 0)
        self.wByte(LLV2, 0)
        self.wByte(LLV3, 0)
        self.wByte(LLV4, 0)
        self.wByte(CMND, CMND_UPD_OUT)    

    def status(self):
        """ See API description at max14574.py """

        val = self.rByte(USERMODE)
        if ((val & USERMODE_ACTIVE) == USERMODE_ACTIVE):
            return True
        else:
            return False
        
    def temperature(self):
        """ See API description at max14574.py """

        tempC = -273
        rawVal = self.rByte(T_SENSE)
        if (rawVal > 127):
            tempC = ((rawVal-127)*1.6)-60 # ((val-127)*1.6)-60
        return tempC, rawVal

    def llv2Volt(self, llv):
        return llv*0.0445 + 24.4

    def volt2LLV(self, v):
#        print(f'volt2LLV() v={v} (v-24.4)/0.0445={(v-24.4)/0.0445} round((v-24.4)/0.0445)={round((v-24.4)/0.0445)} return={round((v-24.4)/0.0445)}')
        return round((v-24.4)/0.0445)


if __name__ == '__main__':
    pass
