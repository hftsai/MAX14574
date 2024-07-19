#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import tkinter as tk
from max14574 import MAX14574
from const import VOLT_MIN, VOLT_MAX

window = tk.Tk()
window.title('LLV1 SETUP')
window.geometry('650x150')  # 擴展窗口寬度以適應右側的文本框

l = tk.Label(window, bg='white', fg='black', width=30, text='empty')
l.pack()

def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0或更多.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor

def update_voltage():
    llv1 = scaleCoarse
    fine_adjustment = scaleFine
    adjusted_llv = llv1 + fine_adjustment
    if adjusted_llv < 0:
        adjusted_llv = 0
    elif adjusted_llv > 1023:
        adjusted_llv = 1023
    voltage = adjusted_llv * 0.0445 + 24.4
    mm.setVoltage(ch, voltage)
    llv1TRunc = truncate(adjusted_llv, 0)
    voltageTRunc = truncate(voltage, 1)
    l.config(text=f'LLV={llv1TRunc}, Voltage={voltageTRunc}V')
    print(f'Set LLV={llv1TRunc}, Voltage={voltageTRunc}V')

def coarse_tune(vCoarse):
    global scaleCoarse
    scaleCoarse = int(vCoarse)
    update_voltage()

def fine_tune(vFine):
    global scaleFine
    scaleFine = int(vFine)
    update_voltage()

def set_llv_from_entry(event):
    try:
        value = int(entry.get())
        if 0 <= value <= 1023:
            global scaleCoarse
            scaleCoarse = value
            coarse.set(scaleCoarse)
            update_voltage()
        else:
            l.config(text='Invalid input: 0-1023 only')
    except ValueError:
        l.config(text='Invalid input: integers only')

ch = int(sys.argv[1])
mm = MAX14574(int(sys.argv[2]), int(sys.argv[3], 16), True, 0x0, 0x0)
mm.start()
print(f'status={mm.status()}')

maxCoarse = 1023
minCoarse = 0
minFine = -5
maxFine = 5
tickCoarse = 250
tickFine = 1
scaleCoarse = 250
scaleFine = 0
resolutionCoarse = 1
resolutionFine = 1

# 計算細調滑塊和文本框的總寬度
fine_slider_width = 450
entry_width = 20  # 假設文本框寬度為 20 單位
total_width = fine_slider_width + entry_width +160

coarse = tk.Scale(window, label='COARSE, LLV', 
    from_=minCoarse, to=maxCoarse, orient=tk.HORIZONTAL, length=total_width, showvalue=0, tickinterval=tickCoarse, resolution=resolutionCoarse, command=coarse_tune)
coarse.set(scaleCoarse)
coarse.pack(side='top', anchor='nw')

frame = tk.Frame(window)
frame.pack(side='top', fill='x')

fine = tk.Scale(frame, label='FINE, LLV', 
    from_=minFine, to=maxFine, orient=tk.HORIZONTAL, length=fine_slider_width, showvalue=0, tickinterval=tickFine, resolution=resolutionFine, command=fine_tune)
fine.set(scaleFine)
fine.pack(side='left')

entry = tk.Entry(frame)
entry.pack(side='left', padx=10)  # 將文本框放在細調滑塊右側

entry.bind('<Return>', set_llv_from_entry)

fine_tune(str(scaleFine))
coarse_tune(str(scaleCoarse))

window.mainloop()
