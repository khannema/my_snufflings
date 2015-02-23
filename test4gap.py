# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 20:04:57 2015

@author: katrin
"""

from pyrocko import util
from pyrocko.snuffling import Snuffling

#import numpy as num

# open file to write time gaps

# when pile.make_pile() is called without any arguments, the command line
# parameters given to the script are searched for waveform files and directories
class Test4Gap(Snuffling):
    
    def setup(self):
        self.set_name('List Gaps')
        self.set_live_update(False)


    def call(self):
        fn = self.output_filename()
        
        out = open(fn,'w')
        
        p = self.get_pile()

        # get timestamp for full hour before first data sample in all selected traces
        #tmin = calendar.timegm( time.gmtime(p.tmin)[:4] + ( 0, 0 ) )
        tpad = 10


        key = lambda tr: (tr.station,tr.channel)
        all_ranges = {}
        gaps = {}
        cnt = 0
         

        for traces in p.chopper(load_data=False,trace_selector=key):
            if traces:
                for tr in traces:
                    cnt += 1
                    mi, ma = tr.tmin, tr.tmax
                    k = key(tr)
                    if k not in all_ranges:
                        all_ranges[k] = [[mi, ma]]
                    else:
                        time_list = all_ranges[k]
                        time_list.append([mi, ma])
                        all_ranges[k] = time_list
                    if cnt % 100 == 0:
                        print "trace {} done".format(cnt)

            channels = all_ranges.keys()
      
    
            for i in range(len(channels)):
                #gaps.append([])
                if channels[i] not in all_ranges:
                    pass                    
                    #line = 'no time information for component {} of station {}\n'.format(channels[i][1],channels[i][0])
                    #out.write(line)
                else:
                    #print type(all_ranges[k])
                    time_list = all_ranges[channels[i]]
                    time_list = sorted(time_list)
                    for j in range(1,len(time_list)):
                        if time_list[j][0]-time_list[j-1][1]>tpad:
                            if channels[i] not in gaps:
                                gaps[channels[i]] = [[time_list[j-1][1],time_list[j][0]]]
                            else:
                                gap_list = gaps[channels[i]]
                                gap_list.append([time_list[j-1][1],time_list[j][0]])
                                gaps[channels[i]] = gap_list

            for i in range(len(channels)):
                if channels[i] not in gaps:
                    pass                    
                    #line = 'component {} of station {} has no gap\n'.format(channels[i][1],channels[i][0])
                    #out.write(line)
                else:
                    gap_list = gaps[channels[i]]
                    #print gap_list
                    for j in range(len(gap_list)):
                        line = '{} {} {} {}\n'.format(channels[i][0],channels[i][1],util.time_to_str(gap_list[j][0]),util.time_to_str(gap_list[j][1]))
                        out.write(line)
        
        out.close
#        
def __snufflings__():
    return [ Test4Gap() ]
