import argparse
import numpy as np
import matplotlib.pyplot as plt
import sigproc
import warnings

parser = argparse.ArgumentParser(description="Multi-beam FIL file visualization");
parser.add_argument('infile', type=str, help="FIL file name");
parser.add_argument('-cl', type=int, dest='cl', help="channel low", default = 0);
parser.add_argument("-cu", type=int, dest='cu', help="channel high", default = 1023);
parser.add_argument('-il', type=int, dest='il', help="integration low", default = 0);
parser.add_argument("-iu", type=int, dest='iu', help="integration high", default = 4095);
parser.add_argument('-bl', type=int, dest='bl', help="beam low", default = 0);
parser.add_argument("-bu", type=int, dest='bu', help="beam high", default = 63);
args = parser.parse_args();

cl = args.cl;
cu = args.cu;
bl = args.bl;
bu = args.bu;
il = args.il;
iu = args.iu;

header = sigproc.read_header(args.infile);
nBeams = header['nbeams'];
nChans = header['nchans'];
nInts = header['nsamples'];

print("\nfile contains:");
print(str(nBeams) + " beams");
print(str(nChans) + " channels");
print(str(nInts) + " time samples\n");

if cl > cu:
    cl , cu = cu , cl;
if bl > bu:
    bl , bu = bu , bl;
if il > iu:
    il , iu = iu , il;
if cl < 0: cl = 0;
if cu > nChans-1: cu = nChans-1;
if bl < 0: bl = 0;
if bu > nBeams-1: bu = nBeams-1;
if il < 0: il = 0;
if iu > nInts-1: iu = nInts-1;

if iu > 4096:
    iu = 4096;
    warnings.warn("upper integration sample set to 4096 to analyze first DADA block");

fh  = open(args.infile, 'rb');
while True:
	keyword, value, idx = sigproc.read_next_header_keyword(fh);
	if keyword == 'HEADER_END':
		break;

nStartDataIdx = fh.tell();
fh.seek(0,0);
data = np.fromfile(fh, dtype=np.uint8, count=nBeams*nChans*nInts, offset=nStartDataIdx);
data = np.reshape(data, (nBeams,nInts,nChans), order = 'C');
data = data[bl:bu+1,il:iu+1,cl:cu+1];
data = data.transpose(0,2,1);
data = np.reshape(data,((bu-bl+1)*(cu-cl+1),(iu-il+1)),order='C').T;

plt.figure();
plt.suptitle(args.infile, fontsize=14)
plt.subplot(2,2,1);
plt.imshow(data,aspect='auto');
plt.colorbar();
plt.xlabel('frequency channel');
plt.ylabel('time sample');
plt.subplot(2,2,2);
plt.plot(np.mean(data,axis=1));
plt.grid();
plt.xlabel('time sample');
plt.ylabel('mean power');
plt.subplot(2,2,3);
plt.plot(np.mean(data,axis=0));
plt.grid();
plt.xlabel('frequency channel');
plt.ylabel('mean power');
plt.show();
