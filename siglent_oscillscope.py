import time
import pandas as pd
import numpy as np

class SiglentOscilloscope:
    def __init__(self, resource_manager):
        resources = resource_manager.list_resources()
        for visa_addr in resources:
            if ('USB' in visa_addr) and ('SDS' in visa_addr):
                self.instr = resource_manager.open_resource(visa_addr)
                addr_expand = visa_addr.split('::')
        if self.instr is not None:  
            id_string = self.instr.query('*IDN?')
            id_expand = id_string.split(',')
            if 'SIGLENT' in id_expand[0]:
                self.model = id_expand[1]
                self.sn = id_expand[2]
                print('Connected to', self.model,'with S/N', self.sn)
                self.echo_command(False)
            else:
                raise Exception("Failed to connect to a Siglent instrument")

    def echo_command(self, enable):
        if enable:
            self.instr.write('COMM_HEADER LONG')
            self.quiet = False
        else:
            self.instr.write('COMM_HEADER OFF')
            self.quiet = True

    def close(self):
        time.sleep(0.01) # delay to give time for previous command to finish
        self.instr.close()

    def __del__(self):
        self.close()

    def set_coupling(self, channel: int, coupling: str):
        if coupling in ['AC', 'DC']:
            self.instr.write('C%d:COUPLING %c1M' % (channel, coupling[0]))
        else:
            raise Exception("Invalid coupling string. Only 'AC' or 'DC' are permitted.")

    def set_offset(self, channel: int, value: float, units: str):
        if units in ['V','mV','uV']:
            self.instr.write('C%d:OFFSET %f%s' % (channel, value, units))
        else:
            raise Exception("Invalid units string. Only 'V', 'mV', or 'uV' are permitted.")
    
    def get_offset(self, channel):
        if channel in [1,2]:
            if (self.quiet):
                volt_offset = self.instr.query('C%d:OFFSET?' % channel)
        return float(volt_offset)

    def set_volt_per_div(self, channel: int, value: float, units: str):
        if units in ['V','mV','uV']:
            self.instr.write('C%d:VOLT_DIV %f%s' % (channel, value, units))
        else:
            raise Exception("Invalid units string. Only 'V', 'mV', or 'uV' are permitted.")
    
    def get_volt_per_div(self, channel):
        if channel in [1,2]:
            if (self.quiet):
                volt_per_div = self.instr.query('C%d:VOLT_DIV?' % channel)
        return float(volt_per_div)
    
    def set_time_per_div(self, value: float, units: str):
        units = units.upper()
        unit_opts = ['NS','US','MS','S']
        val_opts = [1, 2.5, 5, 10, 25, 50, 100, 250, 500]
        if (units in unit_opts) and (value in val_opts):
            self.instr.write('TIME_DIV %.1f%s' % (value, units))
        else:
            if not (units in unit_opts):
                raise Exception("Invalid units string. Only 'ns', 'us', 'ms' and 's' are permitted.")
            if not (value in val_opts):
                raise Exception("Illegal value. Only 1, 2.5, 5, 10, 25, 50, 100, 250, or 500 are permitted.")
    
    def get_time_per_div(self):
        if (self.quiet):
            time_per_div = self.instr.query('TIME_DIV?')
        return float(time_per_div)

    def set_trigger_delay(self, value: float, units: str):
        units = units.upper()
        unit_opts = ['NS','US','MS','S']
        if (units in unit_opts):
            self.instr.write('TRIG_DELAY %.1f%s' % (value, units))
        else:
            raise Exception("Invalid units string. Only 'ns', 'us', 'ms' and 's' are permitted.")

    def get_trigger_delay(self):
        if (self.quiet):
            trig_delay_string = self.instr.query('TRIG_DELAY?')
        if ('n' in trig_delay_string):
            trig_delay = float(trig_delay_string.split('n')[0])*1e-9
        elif ('u' in trig_delay_string):
            trig_delay = float(trig_delay_string.split('u')[0])*1e-6
        elif ('m' in trig_delay_string):
            trig_delay = float(trig_delay_string.split('m')[0])*1e-3
        else:
            trig_delay = float(trig_delay_string.split('s')[0])
        return trig_delay

    def set_trigger_coupling(self, channel, coupling: str):
        ch_opts = [1, 2, 'EX']
        coupling_opts = ['AC', 'DC', 'HFREJ','LFREJ']
        if (channel in ch_opts) and (coupling in coupling_opts):
            if channel in [1,2]:
                self.instr.write('C%d:TRIG_COUPLING %s' % (channel, coupling))
            else:
                self.instr.write('%s:TRIG_COUPLING %s' % (channel, coupling))
        else:
            if not (channel in ch_opts):
                raise Exception("Invalid channel. Only 1, 2 or 'EX' are permitted.")
            if not (coupling in coupling_opts):
                raise Exception("Invalid coupling option. Only 'AC', 'DC', 'HFREJ', and 'LFREJ' are permitted.")
    
    def set_trigger_level(self, channel, value, units: str):
        ch_opts = [1, 2, 'EX']
        unit_opts = ['V','mV','uV']
        if (channel in ch_opts) and (units in unit_opts):
            if channel in [1,2]:
                self.instr.write('C%d:TRIG_LEVEL %.2f%s' % (channel, value, units))
            else:
                self.instr.write('%s:TRIG_LEVEL %.2f%s' % (channel, value, units))
        else:
            if not (channel in ch_opts):
                raise Exception("Invalid channel. Only 1, 2 or 'EX' are permitted.")
            if not (units in unit_opts):
                raise Exception("Invalid units. Only 'V', 'mV', and 'uV' are permitted.")
    
    def set_trigger_mode(self, mode: str):
        mode_opts = ['AUTO','NORM','SINGLE']
        if (mode in mode_opts):
            self.instr.write('TRIG_MODE %s' % mode)
        else:
            raise Exception("Invalid mode. Only 'AUTO', 'NORM', and 'SINGLE' are permitted.")

    def set_trigger_slope(self, channel, slope: str):
        ch_opts = [1, 2, 'EX']
        slope_opts = ['NEG','POS','WINDOW']
        if (channel in ch_opts) and (slope in slope_opts):
            if channel in [1,2]:
                self.instr.write('C%d:TRIG_SLOPE %s' % (channel, slope))
            else:
                self.instr.write('%s:TRIG_SLOPE %s' % (channel, slope))
        else:
            if not (channel in ch_opts):
                raise Exception("Invalid channel. Only 1, 2 or 'EX' are permitted.")
            if not (slope in slope_opts):
                raise Exception("Invalid slope option. Only 'NEG', 'POS', or 'WINDOW' are permitted.")
        
    def get_sample_rate(self):
        if (self.quiet):
            rate_string = self.instr.query('SAMPLE_RATE?')
            if ('G' in rate_string):
                sample_rate = float(rate_string.split('M')[0])*1e9
            elif ('M' in rate_string):
                sample_rate = float(rate_string.split('M')[0])*1e6
            elif ('K' in rate_string):
                sample_rate = float(rate_string.split('K')[0])*1e3
            else:
                sample_rate = float(rate_string.split('Sa')[0])
        return sample_rate

    def get_sample_length(self, channel):
        if channel in [1,2]:
            if (self.quiet):
                length_string = self.instr.query('SAMPLE_NUM? C%d' % channel)
        return int(length_string)

    def get_wave(self, channel):
        if not self.quiet:
            self.echo_command(False)
            chatty = True
        else:
            chatty = False
        self.instr.timeout = 3000 # wait up to 3 s
        self.instr.chunk_size = 20*1024*1024
        rate = self.get_sample_rate()
        length = self.get_sample_length(channel)
        self.instr.write('C%d:WF? DAT2' % channel)
        recv = self.instr.read_raw()
        head = recv[0:3].decode()
        num_bytes = int(recv[6:15].decode())
        tail = recv[-2:].hex()
        wave_bytes = recv[15:-2]
        # Integrity check
        if (head == 'ALL') and (num_bytes == len(wave_bytes)) and (tail == '0a0a'):
            # only export data visible on oscilloscope screen
            volts = np.empty(length, dtype=float)
            t = np.empty(length, dtype=float)
            start_byte = int(num_bytes/2-length/2)

            volt_per_div = self.get_volt_per_div(channel)
            volt_offset = self.get_offset(channel)
            for i in range(length):
                if wave_bytes[i+start_byte] > 127:
                    volts[i] = (wave_bytes[i + start_byte]-256)/25*volt_per_div-volt_offset
                else:
                    volts[i] = wave_bytes[i + start_byte]/25*volt_per_div-volt_offset
                t[i] = (i-length/2)/rate
        else:
            raise Exception('Invalid wave data received from oscilloscope.')
        data = pd.DataFrame({'Time (s)': t, 'Volts (V)': volts})
        if chatty:
            self.echo_command(True)
        return data


    def query(self,cmd_string):
        response = self.instr.query(cmd_string)
        print(response[:-1])
        return response[:-1]

    def read_raw(self):
        response = self.instr.read_raw()
        return response

    def command(self,cmd_string):
        self.instr.write(cmd_string)
            

