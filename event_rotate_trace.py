from pyrocko import trace
from pyrocko.snuffling import Snuffling

class RotateTraceAzimuth(Snuffling):
    """
    Rotates traces according to azimuth of active event
    """

    def setup(self):
        self.set_name('Rotate trace with event azimuth')
        self.set_live_update(False)        

    def call(self):
                   
        event, stations = self.get_active_event_and_stations()	
            
        if not stations:
            self.fail('No station information available.')
            
        allstats = {}
        for station in stations:
            if station.station not in allstats:
                allstats[station.station] = station
                print station.station
                
        key = lambda tr: (tr.network, tr.station) 
        
        p = self.get_pile()
        
        tmin, tmax = self.get_selected_time_range(fallback=True)
        print tmin,tmax
        print p
        for tr in p.iter_all():
            print tr
        for traces in p.chopper_grouped(tmin=tmin,
                                        tmax=tmax,
                                        gather=key,
                                        want_incomplete=True,
                                        maxgap=1000.): 
            #print 'sdfsdf'
            #print traces            
            if not traces:
                continue
            
            # rotate all stations except d05
            if self.d05_included(traces):
                continue
            
            key_new = lambda tr: (tr.station, tr.channel)
            tr_chan = {}
            for tr in traces:
                k = key_new(tr)
                if k not in tr_chan:
                    tr_chan[k] = tr
            
            k_chan = tr_chan.keys()
            k_stat = []
            k_comp = []
            for k in k_chan:
                if len(k_stat) == 0:
                    k_stat.append(k[0])
                else:
                    flag = 0
                    for i in range(len(k_stat)):
                        if k[0] != k_stat[i] and flag == 0:
                            k_stat.append(k[0])
                            flag = 1
                if len(k_comp) == 0:
                    k_comp.append(k[1])
                else:
                    flag = 0
                    for i in range(len(k_comp)):
                        if k[1] != k_comp[i] and flag == 0:
                            k_comp.append(k[1])
                            flag = 1
            
            flag = 0
            for k in k_comp:
                if k == 'NN' or k =='EN':
                    flag = 1		
            
            for k in k_stat:
                print k
                if flag == 1:
                    r,t = trace.rotate_to_rt(tr_chan[(k,'NN')],tr_chan[(k,'EN')],event,allstats[k])
                else:
                    r,t = trace.rotate_to_rt(tr_chan[(k,'N')],tr_chan[(k,'E')],event,allstats[k])
                    
                r.set_codes(station=k,location='rot')
                t.set_codes(station=k,location='rot')
                self.add_traces([r,t])
        
    
    def d05_included(self,tr_group):
        return any(map(lambda x: x.station[-1] in '5', tr_group))
    
        	       
def __snufflings__():
    return [ RotateTraceAzimuth() ]


