import os
from Helix.biowulf import Swarm

path = '/data/alstottj/Culture/Data/'


#bands = ('delta', 'theta', 'alpha', 'beta', 'raw', 'gamma', 'high-gamma', 'broad')
bands = ['broad',]
window='hamming'
filter_type = 'FIR'
taps = 512
downsample=1000.0
sampling_rate = 4000.0
swarm = Swarm(memory_requirement=8)

dirList=os.listdir(path)
for file in dirList:
    job_string = "from avalanchetoolbox import preprocessing as preproc\n" +\
    "file = %r\n" % (path+file) +\
    "bands = ['broad',]\n" +\
    "window = %r\n" % (window) +\
    "filter_type = %r\n" % (filter_type) +\
    "taps = %r\n" % (taps) +\
    "downsample  = %r\n" % (downsample) +\
    "sampling_rate = %r\n" %(sampling_rate) +\
    "preproc.HDF5_filter(file, sampling_rate, window=window, taps=taps, filter_type=filter_type,\
        bands = bands, downsample=downsample)"
    swarm.add_job(job_string)

swarm.submit()
