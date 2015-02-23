from pyrocko import trace
from pyrocko.snuffling import Snuffling
import string

class CorrectRotate(Snuffling):
    """
    Rotates traces with azimiuth given for each station.
    In case of already rotated traces (N,E already exist), it assumes
    that traces were rotated in the wrong way.
    """
    def setup(self):
        self.set_name('Re-rotate traces')
        self.set_live_update(False)        

    def call(self):
        fn = self.input_filename()
        with open(fn) as f:
               read_data = f.readlines()	
	    
        allaz = {}
        for i, line in enumerate(read_data):
            fields = string.split(line)
            k = string.lower(fields[0])
            if not k=='#':
                allaz[k] = float(fields[1])

        p = self.get_pile()

        key = lambda tr: (tr.network, tr.station) 	
        
        tmin, tmax = self.get_selected_time_range(fallback=True)
        for traces in p.chopper_grouped(tmin=tmin, tmax=tmax, gather=key):            
            if not traces:
                continue
            
            # rotate all stations except d05
            if self.d05_included(traces):
                continue
           
            if self.want_pre_rotate(traces):
                az = -1 * allaz[traces[0].station]
                rotated = trace.rotate(traces,az,('E', 'N'),('EX', 'NY'))
                print 'using pre-rotated traces\n%s %s ' % tuple(rotated)
                rot_from = ('NY', 'EX')
                rot_to =('NN', 'EN')
            else:
                rotated = [tr.copy() for tr in traces if tr.channel[-1] in '34']
                for tr in rotated:
                    tr.set_channel(tr.channel.upper())
                
                print 'using UN-pre-rotated traces\n%s %s ' % tuple(rotated)
                rot_from = ('HH4', 'HH3')
                rot_to =('N', 'E')
            
             
            az = allaz[traces[0].station]
             
            n_new,e_new = trace.rotate(rotated, az, rot_from, rot_to)
            n_new.set_codes(station=traces[0].station)
            e_new.set_codes(station=traces[0].station)
            self.add_traces([n_new,e_new])

    def want_pre_rotate(self, tr_group):
        return any(map(lambda x: x.channel[0] in 'EN', tr_group))
    
    def d05_included(self,tr_group):
        return any(map(lambda x: x.station[-1] in '5', tr_group))
    
def __snufflings__():
    return [ CorrectRotate() ]