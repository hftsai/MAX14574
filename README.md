# MAX14574 library
This is driver for MAX14574 chip with I2C bus

## Developer:
ssriblo
hftsai


***
## Requirements:
Python 3
***
## Installation procedure:
Dependencies, if not installed:
```bash
$ sudo apt-get install python3-smbus
$ sudo apt-get install python3-tk
```
***
## Example without GUI:
```python
mm = MAX14574 (8, 0x77, 16), True, 0x0, 0x0)
mm.start()
print (f'status={mm.status()}')
print (f'temperature={mm.temperature()}')
mm.setVoltage(ch, llv1)
llv1, llv2, llv3, llv4 = mm.getLLV()
print(f'llv1/2/3/4 = {llv1} {llv2} {llv3} {llv4}')
```

### MAX14574() Class contructor Arguments:
* device - I2C port Number, i.e. for "/dev/i2c-8" it should be "8"
* addr - chip base address [0:127]. Default address 0x77
* intSensor - internal termosensor [True:False]. For internal termosensor shoud be True. For external termosensor should be False
* fstu - startup time configuration [0:3] (see datasheet)
* il - inductior current limit [0:3] (see datasheet)
***
## Example with GUI:
```python
python3 gui.py 1 8 0x77
```
### Arguments: 
* 1 - Channel number (MAX14574 chip support channels [1:4])
* 8 - device bus number
* 0x77 - device address




***
# Methods
***
### `start`()

Turn On chip and output voltage
***
### `status()`

Check is chip in active state
***
### ll_th, bst_fail, circuit_fails, errorsStr = `checkFault` ()

Check fault status procedure
        
Note: this procedure takes 2ms or more and tread will be blocked!

Returns: 

* ll_th=True if thermal shutdown
* bst_fail=True if voltage boost < 70V
* circuit_fails[6:0] bits are follwing:

    [FAIL_OP, FAIL_SH, COM_FAIL, LL[4:1]_FAIL]
    
    sensor_fail[bit6]=FAIL_OP

    sensor_fail[bit5]=FAIL_SH and so on 

* errorsStr -string with all errors decription. String empty, if no errors 
***
### t = `temperature`()

 Get temperature in Celsius for internal Sensor
***
### `setLLVAll` ( llv1,llv2, llv3, llv4, doUpdate=True )

Setup output volatage for all 4 channels      
Arguments:

* llv format 10 bits [0:1023]

If llv=0 then Vrms=24.4V

If llv=1023 then Vrms=69.7V

* doUpdate Flag 

set to True for normal work. 
If doUpdate=False then output does not updated
***
### `setLLV` ( ch, llv, doUpdate=True )

Setup output volatage for one channel

Arguments:
* ch - Channnel Number [1:4] 
* llv format 10 bits [0:1023]

If llv=0 then Vrms=24.4V

If llv=1023 then Vrms=69.7V

* doUpdate Flag 

set to True for normal work. 
If doUpdate=False then output does not updated
***
### llv = `getLLV` ()

Get output setup value

Returns: 

* llv format 10 bits [0:1023] 
***
### `setVoltageAll` (v1,v2, v3, v4, doUpdate=True )

Setup output volatage for all 4 channels
        
Arguments:

* v format is float [24.4:69.7] in Volts

If v < VOLT_MIN then v=VOLT_MIN

If v > VOLT_MAX then v=VOLT_MAX

* doUpdate Flag

set to True for normal work.
If doUpdate=False then output does not updated
***        
### `setVoltage` ( ch, v, doUpdate=True )

Send Voltage Value for one channel
       
Arguments:

* ch - Channnel Number [1:4] 
* v format is float [24.4:69.7] in Volts

If v < VOLT_MIN then v=VOLT_MIN

If v > VOLT_MAX then v=VOLT_MAX

* doUpdate Flag

set to True for normal work.
If doUpdate=False then output does not updated
***
### v1, v2, v3, v4 = `getVoltageAll` (  )

Get output setup values in Voltage

Returns: 

* v in float format

v = llv * 0.0445 + 24.4
***
### v = `llv2Volt` ( llv )

Argument:

* llv [0:1023]

v = llv * 0.0445 + 24.4

Return: 

* v - Voltage in float format
***
### llv = `volt2LLV` ( v)

Argument:

* v - Voltage in float format

llv = round((v-24.4)/0.0445)

Return: 

* llv [0:1023]
***
