from pyrocko import util
from pyrocko.snuffling import Snuffling

class Test4Gap(Snuffling):
    """
    Searches for time gaps in data stream and writes them to a file
    """    
    def setup(self):
        self.set_name('List Gaps')
        self.set_live_update(False)


    def call(self):
        fn = self.output_filename()
        
        out = open(fn,'w')
        
        p = self.get_pile()

        # for test whether there is a gap or not        
        tpad = 10


        key = lambda tr: (tr.station,tr.channel)
        all_ranges = {}
        gaps = {}
        cnt = 0
         
        # call chopper with load_data=False in order to speed up things,
        # loads just metadata of traces
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
                if channels[i] not in all_ranges:
                    pass                    
                else:
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
                else:
                    gap_list = gaps[channels[i]]
                    for j in range(len(gap_list)):
                        line = '{} {} {} {}\n'.format(channels[i][0],channels[i][1],util.time_to_str(gap_list[j][0]),util.time_to_str(gap_list[j][1]))
                        out.write(line)
        
        out.close

        
def __snufflings__():
    return [ Test4Gap() ]
