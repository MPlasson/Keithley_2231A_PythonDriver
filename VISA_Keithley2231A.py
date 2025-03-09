import time
import pyvisa


class VISA_Keithley2231A:
    def __init__(self, COMPort):
        rm = pyvisa.ResourceManager()
        self.visa_resource = rm.open_resource(COMPort, baud_rate=9600, data_bits=8)
        self.visa_resource.write_termination = '\n'
        self.visa_resource.read_termination = '\n'
        self.visa_resource.send_end = True
        self.visa_resource.StopBits = 1

        id = self._sendCommandOPC("*IDN?")
        if "Keithley instruments, 2231A-30-3" in id:
            print(f"Successfully connected to {id}")

        self.setMode_remote()
        calDate = self._sendCommandOPC("CAL:STR?")
        print(f"Last calibrated on {calDate}")

        self.reset()

    def _sendCommandOPC(self, commandSTR):
        return self.visa_resource.query(f"{commandSTR};*OPC?")

    def close(self):
        self.setMode_local()
        self.visa_resource.close()

    #reset the instrument to default values
    def reset(self):
        self._sendCommandOPC('*RST')

    #lock the front panel (local mode required to unlock)
    def setMode_remoteLock(self):
        self._sendCommandOPC('SYSTEM:RWLock')

    #release from remote access mode
    def setMode_local(self):
        self.visa_resource.query('SYSTEM:LOCAL') #no *OPC? query as the instrument turns OFF remote serial port

    #go into remote access mode
    def setMode_remote(self):
        self._sendCommandOPC('SYSTEM:REMOTE')

    # select a channel (1 to 3)
    def selectChannel(self, channelNumber):
        if channelNumber > 3 or channelNumber < 1:
            print(f"Invalid channel number selected: {channelNumber}")
            return
        self._sendCommandOPC("INST:NSEL %d" % channelNumber)

    # set the output state of the currently selected channel
    def setChannelOutputState(self, outputState):
        if outputState < 0 or outputState > 1:
            print(f"Invalid outputState value: {outputState}")
            return
        self._sendCommandOPC("CHAN:OUTP %d" % outputState)

    # enable/disable all the output channels
    def setAllChannelsOutputState(self, outputState):
        if outputState < 0 or outputState > 1:
            print(f"Invalid outputState value: {outputState}")
            return
        self._sendCommandOPC("OUTP %d" % outputState)

    # configure a timer delay before turning off the currently selected channel
    def setOutputTimerDelay(self, timerDelay):
        if timerDelay < 0.1 or timerDelay > 9999.9:
            print(f"Invalid timerDelay value: {timerDelay}")
            return
        self._sendCommandOPC("OUTP:TIM:DEL %d" % timerDelay)

    # activate or deactivate the current channel turn-off timer
    def setOutputTimerState(self, timerState):
        if timerState < 0 or timerState > 1:
            print(f"Invalid timerState value: {timerState}")
            return
        self._sendCommandOPC("OUTP:TIM %d" % timerState)

    # makes noize
    def sendBeep(self):
        self._sendCommandOPC("SYST:BEEP")

    # display a custom text
    def displayText(self, text):
        self._sendCommandOPC(f"DISPLAY:TEXT \"{text}\"")

    # clear the display
    def clearText(self):
        self._sendCommandOPC(f"DISPLAY:TEXT:CLEAR")

    # select a channel and set the current & voltage values
    def setChannelSource(self, channelNumber, voltageValue, currentValue):
        if channelNumber > 3 or channelNumber < 1:
            print(f"Invalid channel number selected: {channelNumber}")
            return
        if voltageValue < 0 or voltageValue > 30:
            print(f"Invalid voltageValue: {voltageValue}")
            return
        if currentValue < 0 or currentValue > 3:
            print(f"Invalid currentValue: {currentValue}")
            return

        self._sendCommandOPC("SOURCE:APPLY CH%d,%f,%f" % (channelNumber, voltageValue, currentValue))

    # set the current setpoint of the currently selected channel
    def setCurrentValue(self, currentValue):
        if currentValue < 0 or currentValue > 3:
            print(f"Invalid currentValue: {currentValue}")
            return
        self._sendCommandOPC("SOURCE:CURRENT %f" % currentValue)

    # set the voltage setpoint of the currently selected channel
    def setVoltageValue(self, voltageValue):
        if voltageValue < 0 or voltageValue > 30:
            print(f"Invalid voltageValue: {voltageValue}")
            return
        self._sendCommandOPC("SOURCE:VOLTAGE %f" % voltageValue)


if __name__ == "__main__":
    PS_2231A = VISA_Keithley2231A("COM6")
    PS_2231A.setAllChannelsOutputState(0)

    PS_2231A.setChannelSource(1, 3.3, 1)
    PS_2231A.setChannelOutputState(1)
    PS_2231A.setChannelSource(3, 5, 0.2)
    PS_2231A.setChannelOutputState(1)

    time.sleep(5)

    PS_2231A.setAllChannelsOutputState(0)
    PS_2231A.close()
