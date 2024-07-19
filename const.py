#!/usr/bin/python3
# -*- coding: utf-8 -*-

#/******** MAX14574 Registers  from max14574.h ********* */
M_STATUS =          0x00 # Rg0 for reading ll_th & bst_fail
STATUS_LL_TH =      (1 << 3)  # bit ll_th - thermal overload
STATUS_BST_FAIL	=   (1 << 2) # bit bst_fail - boost voltage failed

FAILRG =            1
FAIL_OP =           (1 << 6)
FAIL_SH =           (1 << 5)
FAIL_COM_FAIL =     (1 << 4)
FAIL_LL4_FAIL =     (1 << 3)
FAIL_LL3_FAIL =     (1 << 2)
FAIL_LL2_FAIL =     (1 << 1)
FAIL_LL1_FAIL =     (1 << 0)
FAIL_LL_FAIL =     FAIL_LL1_FAIL | FAIL_LL2_FAIL | FAIL_LL3_FAIL | FAIL_LL4_FAIL

T_SENSE =           0x02

USERMODE =          0x03
USERMODE_ACTIVE =   (1 << 1)
USERMODE_SM =       (1 << 0)

OIS_LSB =           0x04
LLV1 =              0x05
LLV2 =              0x06
LLV3 =              0x07
LLV4 =              0x08
CMND =              0x09
CMND_UPD_OUT =		(1 << 1)
CMND_CHK_FAIL =		(1 << 0)

DRIVERCONF =            0x0A
DRIVERCONF_TS_INT =	    (1 << 7)
DRIVERCONF_TS_EXT =	    (1 << 6)
DRIVERCONF_FSTU_SHIFT =	2
DRIVERCONF_FSTU_MASK =	0x0C
DRIVERCONF_IL_MASK =    0x03

#/* Definition of min and max voltage : 24,4V and 70V */
CHARGE_MAX_VOLT_MIN = 0
CHARGE_MAX_VOLT_MAX = 1023
VOLT_MIN =          24.4
VOLT_MAX =          69.9

POWERON =           True
POWEROFF =          False

LLVLIST = [LLV1, LLV2, LLV3, LLV4]

