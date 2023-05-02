import pyvisa
class SiglentSDS2104X:
    '''
    Class to create user-fiendly interface with the SiglentSDS2104X scope.
    Has the get waveform subroutine for use once a connection has been established these functions can 
    be used inside of the measurement file / GUI.
    note! cursors must be on for this method to work!
  
    '''
    def __init__(self):
        rm = pyvisa.ResourceManager()
        self.resource_adress = 'not found'
        resources = rm.list_resources()
        for i in range(len(resources)):
            my_instrument = rm.open_resource(resources[i])
            query = my_instrument.query('*IDN?').strip()
            #print(query)
            if query == 'Siglent Technologies,SDS2104X Plus,SDS2PDDQ6R2565,5.0.1.5.2':
                self.resource_adress = resources[i]
                self.instrument = my_instrument
        if self.resource_adress == 'not found':
            print('Siglent Technologies,SDS2104X Plus not found, try reconecting. If issues persist, restart python')
        
        return 
    def get_waveform(self,channel = 'c1'):
         
        # Change the way the scope responds to queries. For example, 'chdir off'
        # Will result in a returned value like 200E-3, instead of 'C1:VOLT_DIV 200E-3 V'
        self.instrument.write("chdr off")
        
        # Query the volts/division for channel 1
        vdiv = self.instrument.query("c1:vdiv?")
        
        # Query the vertical offset for channel 1
        ofst = self.instrument.query("c1:ofst?")
        
        # Query the time/division
        tdiv = self.instrument.query("tdiv?")
        
        # Query the sample rate of the scope
        sara = self.instrument.query("sara?")
        
        
        sara_unit = {'G':1E9,'M':1E6,'k':1E3}
        for unit in sara_unit.keys():
            if sara.find(unit)!=-1:
                sara = sara.split(unit)
                sara = float(sara[0])*sara_unit[unit]
                break
        sara = float(sara)
        
        horizontal_offset = self.instrument.query('C1:CRVA? HREL').strip()
        
        horizontal_offset = horizontal_offset.split(',')
        horizontal_offset = float(horizontal_offset[4].replace('s', ''))
        #print(horizontal_offset)
        # Query the waveform of channel 1 from the scope to the controller. This write command
        # and the next read command act like a single query command. We are telling the scope
        # to get the waveform data ready, then reading the raw data into 'recv'
        self.instrument.write(channel+":wf? dat2")
          
        recv = list(self.instrument.read_raw())[16:]
        
        # Removes elements in 'recv', although can't remember why this is here
        recv.pop()
        recv.pop()
         
        # Creating and empty list of y-axis and x-axis data and appending it per iteration. 
        # The reason for the if statements is on page 142 of the programming manual
        volt_value = []
        for data in recv:
            if data > 127:
                data = data - 256
            else:
                pass
            volt_value.append(data)
            
         
        time_value = []
        for idx in range(0,len(volt_value)):
            volt_value[idx] = volt_value[idx]/25*float(vdiv)-float(ofst)
            time_data = -(float(tdiv)*10/2)+idx*(1/sara) - horizontal_offset
            time_value.append(time_data)
        
        volt_value = np.asarray(volt_value)
        time_value  = np.asarray(time_value)
        return time_value , volt_value  

