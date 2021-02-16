import time

class BK9172:
    cmd_wait = 0.01

    def __init__(self, resource_manager, visa_addr):
        # Connect to instrument
        self.instr = resource_manager.open_resource(visa_addr)
        self.instr.read_termination = '\r\n'
        self.instr.write_termination = '\r\n'
        self.instr.baud_rate = 57600

        # Verify that this is a BK9172
        id_string = self.instr.query('*IDN?')
        if ('B&K PRECISION' in id_string) and ('9172' in id_string):
            print("Connection to BK 9172 successful")
        else:
            raise Exception("Failed to connect to a BK 9172")

        # Turn off the beep
        self.instr.write('SYS:BEEP OFF')

    def enable(self, enable_output):
        if enable_output:
            self.instr.write('OUT ON')
        else:
            self.instr.write('OUT OFF')
        time.sleep(BK9172.cmd_wait)

    def get_output_state(self):
        return self.instr.query('OUT?')

    def set_current_limit(self, max_current):
        self.instr.write('OUT:LIM:CURR %.3f' % max_current)
        time.sleep(BK9172.cmd_wait)

    def close(self):
        time.sleep(BK9172.cmd_wait) # delay to give time for previous command to finish
        self.instr.close()

    def __del__(self):
        self.close()

    def set_voltage(self, voltage):
        self.instr.write('SOUR:VOLT %.3f' % voltage)
        time.sleep(BK9172.cmd_wait)

    def set_current(self, current):
        if (current < 0.001):
            self.instr.write('SOUR:CURR 0.001')
        else:
            self.instr.write('SOUR:CURR %.3f' % current)
        time.sleep(BK9172.cmd_wait)

    def set_slew_rate(self, slew_rate):
        if (slew_rate is 'MAX'):
            self.instr.write('OUT:SR:VOLT 7.00')
        elif (slew_rate is 'MIN'):
            self.instr.write('OUT:SR:VOLT 0.01')
        else:
            self.instr.write('OUT:SR:VOLT %.3f' % slew_rate)
        time.sleep(BK9172.cmd_wait)

    def get_current(self):
        result = self.instr.query('MEASURE:CURRENT?')
        return float(result)

    def get_voltage(self):
        result = self.instr.query('VOUT?')
        return float(result)
