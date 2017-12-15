from urllib2 import urlopen
from math import sqrt
from needle import pairwise as nw
import matplotlib.path as mpath
import numpy as np
def get_helix():
    u = np.array([[72.238174,149.8959],
            [0,0],
            [5.573096,-5.93928],
            [9.273722,-6.13002],
            [4.557578,-0.23492],
            [9.794367,2.41875],
            [12.1369,6.33528],
            [3.315362,5.54304],
            [2.573496,13.55453],
            [-0.225782,19.37526],
            [-1.44265,2.9998],
            [-4.591615,7.44128],
            [-7.727532,6.32501],
            [-3.950996,-1.40643],
            [-3.217496,-8.19459],
            [-2.510842,-12.32847],
            [0.882997,-5.16549],
            [3.891875,-10.33354],
            [8.076456,-13.48811]])

    u[:, 0] -= 0.098
    codes = [1] + [2] * (len(u) - 2) + [2]
    u = np.append(u, -u[::-1], axis=0)
    codes += codes

    return mpath.Path(3 * u, codes, closed=False)


def read_in_seq(handle):
    l = handle.readline()
    while True:
        if not l or not l[0]==">":
            break
        head = l.strip()
        seq = ''
        l = handle.readline()
        while l and l[0]!=">":
            seq+=l.strip()
            l = handle.readline()
        yield head,seq

def read_in_headers(handle):
    l = handle.readline()
    while True:
        if not l or not l[0]==">":
            break
        head = l.strip()
        l = handle.readline()
        while l and l[0]!=">":
            l = handle.readline()
        yield head.strip(">")

def get_seq_by_head(handle,headers):
    pairs = {}
    l = handle.readline()
    while True:
        if not l or not l[0]==">":
            break
        head = l.strip()[1:]
        seq = ''
        l = handle.readline()
        while l and l[0]!=">":
            seq+=l.strip()
            l = handle.readline()
        if head in headers:
            pairs[head]=seq
    if head in headers:
        pairs[head]=seq
    return pairs

def check_if_in_PDB(pdbId,chain=""):
    address="http://www.rcsb.org/pdb/rest/describeMol?structureId={PDBID}{X}{CHAIN}".format(CHAIN=chain,PDBID=pdbId,X="." if chain else "")
    response = urlopen(address)
    html = response.read()
    return "polymer" in html

def RMSD(a,b):
    return    sqrt( (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

def minRMSD(la,lb):
    minimal = 1000000000.
    for a in la:
        for b in lb:
            minimal = min(minimal, sqrt( (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2))
    return minimal

def similarEnough(s1,s2): #for sequences
    (a1,a2),_ = nw(s1,s2)
    mismatch = sum(["-" not in [a1[i],a2[i]] and a1[i]!=a2[i] for i in xrange(len(s1))])*1.
    idx_ref = a2.index(a2.strip("-")) - a1.index(a1.strip("-"))
    return mismatch/len(a1) < .1,idx_ref


def find_module(modulename, filename=None):
    """Finds a python module or package on the standard path.
       If a filename is specified, add its containing folder
       to the system path.

       Returns a string of the full path to the module/package."""
    import imp
    import sys
    import os

    full_path = []
    if filename:
        full_path.append(os.path.dirname(os.path.abspath(filename)))
    full_path += sys.path
    fname = imp.find_module(modulename, full_path)
    return fname[1]

def find_continuous(lista,ch=False):
    all = []
    current = [lista[0]]
    for i in lista[1:]:
        if i!=(current[-1]+1):
            all.append(current)
            current=[i]
        else:
            current.append(i)
    all.append(current)
    if ch:
        return map(lambda x: (x, ch), all)
    return all

def find_regions(lista):
    lista = sorted(list(set(lista)))
    chains = list(set(x[1] for x in lista))
    regions = []
    #print "lista",lista
    #print "chains are",chains
    for ch in chains:
        regions+=find_continuous(map(lambda y: y[0],filter(lambda x: x[1]==ch,lista)),ch)
    #print "regions",regions
    return regions,chains

