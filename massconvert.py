import MCS
import h5py
import os
from scipy.io import loadmat
from numpy import array
from avalanchetoolbox import preprocessing as preproc
import re

path = '/data/alstottj/Culture/Original/'
output_path = '/data/alstottj/Culture/Data/'
group_name = 'NIMH'
species = 'rat_culture'
location = 'NIMH'

dirList=os.listdir(path)

#bands = ('delta', 'theta', 'alpha', 'beta', 'raw', 'gamma', 'high-gamma', 'broad')
bands = ('raw',)
window='hamming'
#taps=25
taps = 512
#downsample=100.0
downsample=False
#sampling_rate = 600.0

for dirname in dirList:
    if not dirname.endswith('.raw'):
        continue
    print dirname
    file = path+dirname
    data, sampling_rate, electrode_names = MCS.raw_import(file)


    components = re.split('\.|_', dirname)
    name = components[0]
    number = components[0]
    output_file = output_path+name

    drug = ''
    date = ''
    visit = ''

    for i in components[1:]:
        if i.startswith('DNQX'):
            drug = 'DNQX'
            if i[4:].isdigit():
                visit = i[4:]
        if i.startswith('AP5'):
            drug = 'AP5'
            if i[3:].isdigit():
                visit = i[3:]
        if i.startswith('PTX'):
            drug = 'PTX'
            if i[3:].isdigit():
                visit = i[3:]
        if i.startswith('C'):
            drug = 'C'
            if i[1:].isdigit():
                visit = i[1:]
        if i.startswith('CC'):
            drug = 'CC'
            if i[2:].isdigit():
                visit = i[2:]
        if i.isdigit():
            date = i
        if i.startswith('spon') and i[4:].isdigit():
            visit = i[4:]

    #Some files did not incorporate multiple visits into their filenames, instead relying on dates to identify different runs
    #We use date as an attribute, not a directory name, so we can't rely on that. If we don't have visit information, we check 
    #if we've written any of this type previously, and if so increment the visit count.
    if visit == '':
        try:
            f = h5py.File(output_file+'.hdf5', 'r')
            n = 0
            for i in list(f):
                components = i.split('_')
                #Remove the cases that aren't the present case
                if drug!='' and not components[0].startswith(drug):
                    continue
                else:
                #Anything that remains is the same drug condition as the present case
                    n+=1
            assert n!=0
            visit = str(n+1)
        except (IOError, AssertionError):
            visit = '1'

    if drug!='':
        task = drug+'_spontaneous'+visit
    else:
        task = 'spontaneous'+visit

    preproc.write_to_HDF5(data,output_file, task, sampling_rate=sampling_rate, bands=bands,\
            window=window, taps=taps,\
            downsample=downsample,
            group_name=group_name, species=species, location=location,\
                    number_in_group=number, name=name, date=date, drug=drug)

    badelec_mat = loadmat(file[:-4]+'badelec.mat')
    badelec = badelec_mat['badelec']
    if not badelec.any():
        badelec = array([-1])
    else:
        for i in range(len(badelec[0])):
            if badelec[0][i]<=8:
                badelec[0][i]-=2
            elif badelec[0][i]<=56:
                badelec[0][i]-=3
            else:
                badelec[0][i]-=4
    f = h5py.File(output_file+'.hdf5')
    f[task+'/bad_channels'] = badelec
    f.close()
