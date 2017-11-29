from needle import pairwise_prot as nw_prot
from needle import pairwise_rna as nw_rna
from needle import sekwencja as Sekwencja
from needle import consensus

from math import sqrt
try:
    from Bio.SeqUtils import seq1
except:
    from BioPythonStub import seq1
import numpy as np
import Tkinter as Tk
from platform import system as platform_system
import time

import matplotlib.pyplot as plt
#import matplotlib as mpl
import tkMessageBox

from pymol import cmd,preset

from helper_functions import minRMSD,RMSD,similarEnough

global nw
nw = nw_prot

WC_PAIRS = [ "GC","CG","AU","UA","AT","TA"]
OTHER_PAIRS = ["GU","UG"]

def getChainMap(objId, my_chains):
    my_chains = list(my_chains)
    refs = {c: ["".join(cmd.get_fastastr('({} and c. {})'.format(objId, c)).split()[1:])] for c in my_chains}
    to_keep = set([])
    to_keep_idx_ref = {}
    for chain in cmd.get_chains(objId):
        if chain in my_chains:
            continue
        seq = "".join(cmd.get_fastastr('({} and c. {})'.format(objId, chain)).split()[1:])
        for r in refs:
            se, sir = similarEnough(seq, refs[r][0])
            if se:
                refs[r].append(chain)
                to_keep.add(chain)
                space = {"out": []}
                okc = cmd.iterate("first %s and c. %s and polymer and n. CA" % (objId, chain), "out.append(resv)",
                                  space=space)
                okr = cmd.iterate("first %s and c. %s and polymer and n. CA" % (objId, r), "out.append(resv)",
                                  space=space)
                to_keep_idx_ref[(r, chain)] = sir - space['out'][1] + space['out'][0]

    return {r: refs[r][1:] for r in refs}, to_keep, to_keep_idx_ref


def make_a_snowman(starting_struct, further_structs, seqName):
    id, chain = starting_struct
    chain = chain.split(".")[0] if chain else cmd.get_chains(id)[0]
    selection = "({} and c. {} and polymer)".format(id, chain)
    cnt = 1
    OTHER_NUMBERING = 1  # False
    space = {"resvs": []}  # TODO renumber keeping numbering gaps?
    _lens = []

    newName = [id+chain]


    cmd.iterate(selection + " and name ca and elem c", "resvs.append(resi)", space=space)
    _lens.append(len(space['resvs']))
    if OTHER_NUMBERING:
        cnt = int(filter(lambda x: x.isdigit(), space["resvs"][-1]))
        cnt += 1000 - (cnt % 1000)
    else:
        for res in space["resvs"]:
            cmd.alter(selection + "and i. %s" % res, 'resi="%d"' % cnt)
            cnt += 1

    for x in further_structs:
        space = {"resvs": []}
        xid, xch = x[:2]
        newName.append(xid+xch)
        xch = xch.split(".")[0] if xch else cmd.get_chains(xid)[0]
        sel = "({} and c. {} and polymer)".format(xid, xch)
        space = {"resvs": []}  # TODO renumber keeping numbering gaps?
        cmd.iterate(sel + " and name ca and elem c", "resvs.append(resi)", space=space)
        for res in space["resvs"]:
            if OTHER_NUMBERING:
                cmd.alter(sel + "and i. %s" % res, 'resi="%s"' % res.replace(filter(lambda x: x.isdigit(), res), str(
                    int(filter(lambda x: x.isdigit(), res)) + cnt)))
            else:
                cmd.alter(sel + "and i. %s" % res, 'resi="%d"' % cnt)
                cnt += 1
        if OTHER_NUMBERING:
            cnt += int(filter(lambda x: x.isdigit(), space["resvs"][-1]))
            cnt += 1000 - (cnt % 1000)
        selection += " OR " + sel
        _lens.append(len(space['resvs']))
    newName = "_".join(newName)
    cmd.create(newName, selection, quiet=0)
    cmd.get_fastastr(seqName)
    # TODO remove source objects
    for x in [[id]] + further_structs:
        cmd.delete(x[0])
    cmd.alter("(%s)" % seqName, "chain='A'", quiet=0)
    return _lens,newName

def mapping(align_sequence,str_sequence, seqName, objId):

    (astr, aseq), _ = nw(str_sequence, align_sequence)
    mismatch = any([a != b and a not in [".", "-"] and b not in [".", "-"] for (a, b) in zip(astr, aseq)])
    blaseq = Tk.StringVar()## aseq
    blaseq.set(aseq)
    blastr = Tk.StringVar()#astr
    blastr.set(astr)
    if mismatch:
        mmwindow = Tk.Toplevel()
        e = Tk.Text(mmwindow, width=80,font=("Monospace" if platform_system()!="Windows" else "Consolas"))
        e.insert(Tk.END, """There is a mismatch in the sequence for {} ({}).\n
        Aligned sequences:\n
        From fasta: \n{}\n
         From .pdb: \n{}
        """.format(seqName, objId, aseq, astr))
        e.config(state='disabled')
        e.pack(side=Tk.TOP)
        def _mm_quit(*args):
            aseq = blaseq.get()
            astr = blastr.get()
            if e.cget('state') == 'normal':
                naseq = ""
                nastr = ""
                cnt = 0
                for line in e.get(1.0, Tk.END).split("\n"):
                    if "From" in line:
                        cnt+=1
                    elif cnt == 1:
                        naseq+=line.strip()
                    elif cnt == 2:
                        nastr += line.strip()
                err = 0
                if naseq.replace("-","") != aseq.replace("-",""):
                    tkMessageBox.showinfo("Error","Sequence 'From fasta' differs from the one that was here before!")
                    err += 1
                if nastr.replace("-","") != astr.replace("-",""):
                    tkMessageBox.showinfo("Error","Sequence 'From pdb' differs from the one that was here before!")
                    err+=1
                if len(naseq)!=len(nastr):
                    tkMessageBox.showinfo("Error","Aligned sequences have different lengths! {} and {}".format(len(naseq),len(nastr)))
                    err+=1
                if ("-","-") in zip(naseq,nastr):
                    naseq, nastr = zip(*[x for x in zip(naseq,nastr) if x!=("-","-")])
                if err:
                    return
                blaseq.set(naseq)
                blastr.set(nastr)
                ## TODO do smthing with it

            mmwindow.quit()
            mmwindow.destroy()
        def _correct(*args):
            e.config(state='normal')
            e.delete(1.0, Tk.END)
            e.insert(Tk.END, """
                        >From fasta: \n{}\n
                        >From .pdb: \n{}
                        """.format(aseq, astr))


        Tk.Button(mmwindow, text="Accept", command=_mm_quit).pack()
        Tk.Button(mmwindow, text="Correct by hand", command=_correct).pack()
        mmwindow.mainloop()
    return blaseq.get(),blastr.get()

class Atom:
    def __init__(self,name,elem,x,y,z):
        self.name = name
        self.elem = elem
        self.x = x
        self.y = y
        self.z = z
        self.list = [x,y,z]
    def __getitem__(self, key):
        return self.list[key]

class Residue:
    def __init__(self, res_name, str_resid, seq_resid, ss):
        self.name = res_name
        self.seqid = seq_resid
        self.pdbid = str_resid
        self.ss = ss  # boolean
        self.insert = False



class Residue_old:
    def __init__(self, res_name, str_resid, seq_resid, atoms, insert, ss):
        self.name = res_name
        self.seqid = seq_resid
        self.pdbid = str_resid
        self.atoms = atoms
        self.Calpha = None  # smthing from atoms
        self.Cbeta = None  # smthing from atoms
        self.insert = insert  # boolean
        self.ss = ss
        self.prepare_atoms()

    def prepare_atoms(self):
        atoms = []
        self.heavy_atoms = []
        self.Calpha = None
        self.Cbeta = None
        #            n,rn,rv,a,e,q,s,x,y,z
        tmp = []
        for a in self.atoms:
            if not a[3]:
                if tmp:
                    x = sorted(tmp, key=lambda y: y[5])[0]
                    atoms.append(Atom(x[0], x[4], x[7], x[8], x[9]))
                atoms.append(Atom(a[0], a[4], a[7], a[8], a[9]))
            else:
                tmp.append(a)
        for atom in atoms:
            if atom.name != "H":
                self.heavy_atoms.append(atom)
            if atom.name == "CA" and atom.elem == "C":
                self.Calpha = atom
            if atom.name == "CB":
                self.Cbeta = atom
        #if not self.Calpha:
        #    print self.atoms
        self.atoms = atoms

    def within_distance(self, other_res, distance=8., mode="CA"):
        if mode == "CA":
            return RMSD(self.Calpha, other_res.Calpha) < distance
        elif mode == "CB":
            return RMSD(self.Cbeta, other_res.Cbeta) < distance
        elif mode == "heavy":
            for i in self.heavy_atoms:
                for j in other_res.heavy_atoms:
                    if RMSD(i, j) < distance:
                        return True
            return False
        else:
            raise ValueError("Not implemented")


class Translation:
    def __init__(self):
        self.alignment2full_di = []
        self.unal2alignment = []
        self.unal_fasta2structseq = []
        self.pdb2structseq = []
        self.structseq2pdb = []
        self.structseq2unal_fasta = []
        self.fasta2unal_fasta = []

        #USELESS?
        self.fasta2full_di = []
        self.unal_fasta2fasta = []
        self.alignment2unal = []
        self.alignment2structseq = []
        self.structseq2alignment = []
        self.shortfasta = ""
        self.unal_fasta = ""


    def a2fd(self, sequence):
        self.shortfasta = "".join([i for i in sequence if i not in ".qwertyuiopasdfghjklzxcvbnm"])
        self.unal_fasta = "".join([i for i in self.shortfasta if i != "-"])
        _cnt = 0
        _cntf = 0
        for i in sequence:
            if i not in ".qwertyuiopasdfghjklzxcvbnm":
                self.alignment2full_di.append(_cnt)
                _cnt += 1
            else:
                self.alignment2full_di.append(None)

        _cnt = 0
        for i in self.shortfasta:
            if i != "-":
                self.fasta2unal_fasta.append(_cnt)
                _cnt += 1
            else:
                self.fasta2unal_fasta.append(None)

        ###PROBABLY USELESS <
        for (i, j) in zip(self.shortfasta, self.alignment2full_di):
            if i != "-":
                self.fasta2full_di.append(j)


        self.unal_fasta2fasta = [None for i in self.unal_fasta]
        for i, e in enumerate(self.fasta2unal_fasta):
            if e is not None:
                self.unal_fasta2fasta[e] = i
        ### <

    def u2s(self, me, splits=None):
    #def u2s(self, alignseq, structseq, splits=None):
        alignseq = me.sequence
        structseq = me.str_sequence
        ualignseq = "".join([i for i in alignseq if i not in [".", "-"]])
        print ualignseq
        print structseq
        print nw
        if splits is None:
            (uaseq, sseq), _ = nw(ualignseq, structseq)
        elif not splits[0]:  # Im feeling lucky
            (uaseq, sseq), _ = nw(ualignseq, structseq)

        else:  # user-specified
            ualignseqs = [x.replace(".", "-").replace("-", "") for x in splits[0]]
            _tmp = [0] + splits[1] + [0]
            structseqs = [x for x in [structseq[sum(_tmp[:i]):sum(_tmp[:i + 1])] for i in xrange(len(_tmp))] if x]
            uaseq, sseq = zip(*(nw(x, y)[0] for x, y in zip(ualignseqs, structseqs)))
            uaseq, sseq = map(lambda a: "".join(a), (uaseq, sseq))
        _cnt = 0
        uaseq,sseq = mapping(uaseq,sseq,me.seqName,me.objId)


        for i in alignseq: # TODO probably useless
            if i not in ["-", "."]:
                self.alignment2unal.append(_cnt)
                _cnt += 1
            else:
                self.alignment2unal.append(None)

        self.unal2alignment = [None for i in ualignseq]
        for i, e in enumerate(self.alignment2unal):
            if e is not None:
                self.unal2alignment[e] = i

        _cnts = -1
        _cntu = -1

        self.unal_fasta = ualignseq
        for i, j in zip(uaseq, sseq):
            if i != "-":
                _cntu += 1
            if j != "-":
                _cnts += 1
            if (i, j) == (i, "-"):
                self.unal_fasta2structseq.append(None)
            elif (i, j) == ("-", j):
                self.structseq2unal_fasta.append(None)
            else:
                assert "-" not in [i, j]
                self.structseq2unal_fasta.append(_cntu)
                self.unal_fasta2structseq.append(_cnts)


    def p2s(self, residues, structseq):
        self.structseq2cmap=[]
        if Structure.isRNA:
            fseq = lambda x: x[-1]
        else:
            if len(residues[0].name) > 1:
                fseq = seq1
            else:
                fseq = lambda x: x
        rseq = "".join([fseq(i.name) for i in residues])
        if rseq == structseq:
            _tmp = range(len(structseq))
            _tmp.reverse()
            self.structseq2pdb = [i.pdbid for i in residues]
            self.pdb2structseq = {i: _tmp.pop() for i in self.structseq2pdb}
            self.structseq2cmap = range(len(residues))
        else:
            Structure.version = 1.8
            (arseq,astructseq),_ = nw(rseq,structseq)
            assert astructseq == astructseq.replace("-","") ### Dziwne, ze struktura ma cos wiecej niz sekwencja, raczej jest to error
            #print "struct_seq",astructseq
            #print "rseq",arseq
            #print "p2s"
            _rcnt = -1
            _scnt = -1

            self.structseq2pdb = []
            self.pdb2structseq = {}
            for i,(r,s) in enumerate(zip(arseq,astructseq)):
                _rcnt += (r!="-")
                _scnt += (s != "-")
                if r!="-":
                    if s!="-":
                        self.pdb2structseq[residues[_rcnt].pdbid] = _scnt
                    else:
                        self.pdb2structseq[residues[_rcnt].pdbid] = None
                if s != "-":
                    if r != "-":
                        self.structseq2pdb.append(residues[_rcnt].pdbid)
                        self.structseq2cmap.append(_rcnt)
                    else:
                        self.structseq2pdb.append(None)
                        self.structseq2cmap.append(None)


    def fullplot(self, idx):
        return idx

    def fullplot2struct(self,idx):
        try:
            return self.unal_fasta2structseq[self.fasta2unal_fasta[idx]]
        except TypeError:
            return None

    def singleplot_old(self, idx_with_inserts):
        try:
            return self.alignment2full_di[idx_with_inserts]
        except TypeError:
            return None

    def singleplot_native(self, idx_with_inserts):
        try:
            return self.structseq2cmap[self.unal_fasta2structseq[idx_with_inserts]]
            #return self.structseq2pdb[self.unal_fasta2structseq[idx_with_inserts]]
            #return self.unal_fasta2structseq[idx_with_inserts]
        # return self.structseq2pdb[self.unal_fasta2structseq[self.alignment2unal[idx_with_inserts]]]
        except TypeError:
            return None
        """except e:
            raise e
            print self.unal_fasta2structseq, len(self.unal_fasta2structseq), idx_with_inserts
            print self.unal_fasta, len(self.unal_fasta)
            print self.unal_fasta2structseq[idx_with_inserts]
            print self.structseq2pdb, len(self.structseq2pdb)"""

    def singleplot(self, unal_idx):
        try:
            return self.alignment2full_di[self.unal2alignment[unal_idx]]
        except TypeError:
            return None
    def singleplot_bonds(self, unal_idx):
        try:
            return self.unal_fasta2structseq[unal_idx]
        except TypeError:
            return None

    def singleplot_cursor(self, unal_idx):
        if unal_idx == len(self.unal_fasta2structseq):#  -=1
            return None
        try:
            x = self.unal_fasta2structseq[unal_idx]
            return self.structseq2pdb[x]
        except TypeError:
            return None
        except IndexError:
            print unal_idx
            print self.unal_fasta2structseq
            raise IndexError

    def singleplot_restrict(self, struct_idx):
        try:
            return self.alignment2full_di[self.unal2alignment[self.structseq2unal_fasta[struct_idx]]]
        except TypeError:
            return None

    def singleplot_restrict_native(self, pdb_resid):
        return pdb_resid

    def resid2unal_fasta(self, resid):
        try:
            return self.structseq2unal_fasta[self.pdb2structseq[resid]]
        except TypeError:
            return None

    """def unal_fasta2resid(self, alnid):
        try:
            return self.structseq2pdb[self.unal_fasta2structseq[alnid]]
        except TypeError:
            return None
        except KeyError:
            return None
        except IndexError:
            print alnid
            print self.unal_fasta2structseq,len(self.unal_fasta2structseq)
            print self.unal_fasta2structseq[alnid]
            print self.structseq2pdb"""

    def struct2pdb(self,sid):
        try:
            #print sid, self.structseq2pdb
            return self.structseq2pdb[sid]
        except TypeError:
            return None
        except:
            print sid, self.structseq2pdb
            raise IndexError


def verify_nw():
    global nw
    if Structure.isRNA:
        nw = nw_rna
    else:
        nw = nw_prot

class Structure:
    available_modes = [u"C\u03B1",u"C\u03B2","All heavy atoms"]
    flat_modes = {u"C\u03B1":"CA",u"C\u03B2":"CB","All heavy atoms":'heavy',"C1'":"C1","C4'":"C4","O5'":"O5","All heavy atoms":"heavy","Canonical base pairing":"canonical" }
    mode = available_modes[0]
    version = 1.7
    isRNA = False #must be boolean
    mode_rna = "C1'"
    available_modes_rna = ["C1'","C4'","O5'","All heavy atoms","Canonical base pairing"] #TODO N1/N9 purine/pyrimidine?

    def __init__(self, objId, chain, seqName, sequence,keep_others=False,further_structs=False,splits=None):
        verify_nw()
        seqName = seqName.replace(" ","_").replace("/","_").replace("\\","_")
        #print "FS:",bool(further_structs)
        if further_structs:
            _lens,newName = make_a_snowman((objId,chain),further_structs,seqName)
            objId = newName
            chain="A"
            if splits is not None:
                splits = [splits,_lens]


        self.objId = objId
        self.chain_list = ([chain] if "." not in chain else chain.split(".")) if chain else cmd.get_chains(objId)
        #self.chain = "(" + " or ".join(["c. "+x for x in self.chain_list]) + ")"
        self.chain_simple = self.chain_list[0]
        self.chain = "( c. {} )".format(self.chain_simple)
        self.seqName = seqName
        self.sequence = sequence
        self.str_sequence = "".join(cmd.get_fastastr("(%s and c. %s)" % (objId,self.chain_simple)).split()[1:])

        self.residues_mapping()
        if not self.str_sequence:
            self.str_sequence = "".join(x.name[-1] for x in self.residues)
        #print "Sequence is", self.str_sequence

        self.temp_path = ""

        self.translations = Translation()
        self.translations.a2fd(sequence)
        self.translations.u2s(self,splits)
        #self.translations.u2s(self.sequence,self.str_sequence,splits)
        already_there = "DM_" in objId and objId.strip("DM_") in cmd.get_object_list('(all)')

        self.sequence_residues = []
        self.active = True
        self.maps = {}
        self.any_maps = {}
        self.interchain_maps = {}
        self.chain_map = {}
        self.chains_to_keep = [] #TODO - the longest one should be reference, or the selected?
        self.chain_idx_ref = None
        if keep_others:
            self.chain_map,self.chains_to_keep,self.chain_idx_ref = getChainMap(objId, (chain.split(".") if "." in chain else chain) if chain else
            cmd.get_chains(objId)[0])

        #self.residues_mapping()
        self.translations.p2s(self.residues,self.str_sequence)
        #self.mapping()

        self.num_states = cmd.count_states(selection="(%s and %s)"%(self.objId,self.chain))
        self.current_state = 1

        if already_there:
            cmd.hide("everything",objId.strip("DM_"))
        else:
            preset.pretty(self.objId)
            preset.pretty("(%s and %s)"%(self.objId,self.chain))
            for c in self.chains_to_keep:
                preset.pretty("(%s and c. %s)"%(self.objId,c))
        cmd.center("(%s and %s)"%(self.objId,self.chain))
#        cmd.hide("cartoon","(%s and not  %s)"%(self.objId,
#            self.chain if not self.chains_to_keep else "( %s or %s )"%(self.chain,"c. "+(" or c. ".join(self.chains_to_keep))) ))
        cmd.remove("(%s and not  %s)"%(self.objId,
            self.chain if not self.chains_to_keep else "( %s or %s )"%(self.chain,"c. "+(" or c. ".join(self.chains_to_keep))) ))

        self.paintInserts()
        #self.makeContactMap()

        if 0:
            m = cmd.get_model(
            "(%s and %s) and polymer and (elem C or elem N or elem O or elem P) " % (self.objId, self.chain),
            state=1)
            #print vars(m).keys()
            #print vars(m.molecule)
            print vars(m.atom[0])
            exit(1)


    def residues_mapping(self):
        space = {'residues': []}
        cmd.iterate_state(1, "( %s and %s ) and polymer" % (self.objId, self.chain),
                          "residues.append([name,resn,resv,alt,elem,q,ss,x,y,z])",
                          space=space)
        tmp = []
        self.residues = []
        cnt_resv = "s"
        for res in space["residues"]:
            n, rn, rv, a, e, q, s, _, _, _ = res
            if rn == "HOH": continue
            if cnt_resv != "s" and cnt_resv != rv:
                self.residues.append(Residue(brn, brv, None, bs))
                tmp = []
            cnt_resv = rv
            tmp.append(res)
            bn, brn, brv, ba, be, bq, bs = n, rn, rv, a, e, q, s
        if brn != "HOH": self.residues.append(Residue(brn, brv, None, bs))  # brv was None

    def read_in_map_oneliner_arr(self,line):
        ## line = "num_line dist(last_idx,last_idx-1) . . . dist(1,0)"
        size = len(self.translations.pdb2structseq) ### TODO probably better that structseq2pdb
        mapa = np.zeros((size, size))
        mapa.fill(-1.)
        line = line.split()[1:]
        for x in xrange(size):
            for y in xrange(x):
                d = float(line.pop())
                mapa[x][y] = d
                mapa[y][x] = d#float(line.pop())
        return mapa

    def read_in_any_map_oneliner(self,mapa,line):
        size = mapa.shape[0]
        line = line.split()[1:]
        for x in xrange(size):
            for y in xrange(x):
                d = float(line.pop())
                if d<mapa[x][y]:
                    mapa[x][y] = d
                    mapa[y][x] = d#float(line.pop())
        return mapa

    def makeContactMap(self, state, mchain=False):
        self.current_state = state
        name = self.temp_path + "/_temp_" + self.objId + "{}_{}.map"
        with open(name.format("_multichain" if mchain else "", Structure.flat_modes[Structure.mode])) as mapfile:
            for x, line in enumerate(mapfile):
                #print "Reading in contact map from file: ","state",state,"multichain :",mchain
                if x+1 == state:
                #    print "Found state",x+1
                    if mchain:
                #        print "Reading in multichain from ",name.format("_multichain" if mchain else "", Structure.mode)
                        self.interchain_maps[Structure.flat_modes[Structure.mode]] = self.read_in_map_oneliner_arr(line)
                #        print "done", self.interchain_maps.keys()

                    else:
                        self.maps[Structure.flat_modes[Structure.mode]] = self.read_in_map_oneliner_arr(line)
                elif x >= state:
                    break

    def makeAnyContactMaps(self, mchain=False):
        if Structure.isRNA:
            self.makeAnyContactMaps_rna(mchain)
        else:
            self.makeAnyContactMaps_protein(mchain)


    def makeAnyContactMaps_rna(self, mchain=False):
        size = len(self.translations.pdb2structseq)
        for mode in Structure.available_modes_rna:
            mode = Structure.flat_modes[mode]
            name = self.temp_path + "/_temp_" + self.objId + "{}_{}.map"
            mapa = np.zeros((size, size))
            mapa.fill(1000.)
            with open(name.format("_multichain" if mchain else "", mode.strip("'"))) as mapfile:
                for x, line in enumerate(mapfile):
                        self.read_in_any_map_oneliner(mapa, line)
            self.any_maps[mode] = mapa

    def makeAnyContactMaps_protein(self, mchain=False):
        size = len(self.translations.pdb2structseq)
        for mode in Structure.available_modes:
            mode = Structure.flat_modes[mode]
            name = self.temp_path + "/_temp_" + self.objId + "{}_{}.map"
            mapa = np.zeros((size, size))
            mapa.fill(1000.)
            with open(name.format("_multichain" if mchain else "", mode)) as mapfile:
                for x, line in enumerate(mapfile):
                        self.read_in_any_map_oneliner(mapa, line)
            self.any_maps[mode] = mapa

    def makeMultiStateContactFile(self, step = False,progress=False):
        if Structure.isRNA:
            self.makeMultiStateContactFile_rna(step, progress)
        else:
            self.makeMultiStateContactFile_protein(step, progress)

    def makeMultiStateContactFile_rna(self, step=False, progress=False):
        name = self.temp_path + "/_temp_" + self.objId + "_{}.map"
        with open(name.format("C1"), "w", 1) as output_C1, open(name.format("C4"), "w", 1) as output_C4, \
                open(name.format("O5"), "w", 1) as output_O5, open(name.format("heavy"), "w", 1) as output_heavy, \
                open(name.format("canonical"), "w", 1) as output_canon:
            for stan in xrange(0, self.num_states, step if step else 1):
                if progress:
                    progress("State: {}/{}".format(stan + 1, self.num_states))
                    #                space = {'residues': []}
                    #                cmd.iterate_state(1, "( %s and %s )" % (self.objId, self.chain),
                    #                          "residues.append([name,resn,resv,alt,elem,q,ss,x,y,z])",
                    #                          space=space)

                #########   C1
                #print "state", stan, "C1"
                output_C1.write(str(stan+1))
                lista = cmd.get_model(
                    "(%s and %s) and polymer and elem C and name C1' " % (self.objId, self.chain),
                    state=stan).get_coord_list()
                ll = len(lista)
                for i in xrange(ll - 1, -1, -1):
                    for j in xrange(i - 1, -1, -1):
                        output_C1.write("\t%08.3f" % RMSD(lista[i], lista[j]))
                output_C1.write("\n")
                output_C1.flush()

                #########   C4
                #print "state", stan, "C4"
                output_C4.write(str(stan+1))
                lista = cmd.get_model(
                    "(%s and %s) and polymer and elem C and name C4' " % (self.objId, self.chain),
                    state=stan).get_coord_list()
                ll = len(lista)
                for i in xrange(ll - 1, -1, -1):
                    for j in xrange(i - 1, -1, -1):
                        output_C4.write("\t%08.3f" % RMSD(lista[i], lista[j]))
                output_C4.write("\n")
                output_C4.flush()
                #########   O5

                #print "state", stan, "O5"
                output_O5.write(str(stan+1))
                lista = cmd.get_model(
                    "(%s and %s) and polymer and elem O and name O5' " % (self.objId, self.chain),
                    state=stan).get_coord_list()
                ll = len(lista)
                for i in xrange(ll - 1, -1, -1):
                    for j in xrange(i - 1, -1, -1):
                        output_O5.write("\t%08.3f" % RMSD(lista[i], lista[j]))
                output_O5.write("\n")
                output_O5.flush()

                #########   canon

                #print "state", stan, "canonical"
                output_canon.write(str(stan+1))
                model = cmd.get_model(
                    "(%s and %s) and polymer and (name C1' or ((name N1 and (resn G or resn A)) or (name N3 and (resn C or resn T or resn U)))) " % (self.objId, self.chain),
                    state=stan)#.get_coord_list()
                #lista = [(a.resn, a.coord) for a in lista.atom]
                residues = {}
                for a in model.atom:
                    residues[a.resi] = residues.get(a.resi, []) + ([a.resn[-1],a.coord] if a.name != "C1'" else [])
                # print residues
                lista = sorted(residues.keys(),key=lambda x: int(x))
                ll = len(lista)
                for i in xrange(ll - 1, -1, -1):
                    for j in xrange(i - 1, -1, -1):
                        if residues[lista[i]] and residues[lista[j]] and residues[lista[i]][0]+residues[lista[j]][0] in WC_PAIRS:
                            rmsd = 1. if RMSD(residues[lista[i]][1], residues[lista[j]][1]) < 3. else 1000.
                        elif residues[lista[i]] and residues[lista[j]] and residues[lista[i]][0]+residues[lista[j]][0] in OTHER_PAIRS:
                            rmsd = 2. if RMSD(residues[lista[i]][1], residues[lista[j]][1]) < 3. else 1000.
                        else:
                            rmsd = 1000.
                        if rmsd < 100.:
                            self.residues[i].ss = "H"
                            self.residues[j].ss = "H"
                        output_canon.write("\t%08.3f" % rmsd)
                output_canon.write("\n")
                output_canon.flush()

                #########   heavy
                #print "state", stan, "heavy"
                output_heavy.write(str(stan+1))
                model = cmd.get_model(
                    "(%s and %s) and polymer and (elem C or elem N or elem O or elem P) " % (
                    self.objId, self.chain), state=stan)
                residues = {}
                for a in model.atom:
                    residues[a.resi] = residues.get(a.resi, []) + [a.coord]

                lista = sorted(residues.keys(),key=lambda x: int(x))
                ll = len(lista)
                for i in xrange(ll - 1, -1, -1):
                    for j in xrange(i - 1, -1, -1):
                        output_heavy.write("\t%08.3f" % minRMSD(residues[lista[i]], residues[lista[j]]))
                output_heavy.write("\n")
                output_heavy.flush()
                del model
                del lista

    def makeMultiStateContactFile_protein(self, step=False, progress=False):
        name =  self.temp_path + "/_temp_" + self.objId + "_{}.map"
        with open(name.format("CA"), "w", 1) as output_CA, open(name.format("CB"), "w", 1) as output_CB, open(name.format("heavy"), "w", 1) as output_heavy:
            for stan in xrange(0,self.num_states, step if step else 1):
                if progress:
                    progress("State: {}/{}".format(stan+1,self.num_states))
#                space = {'residues': []}
#                cmd.iterate_state(1, "( %s and %s )" % (self.objId, self.chain),
#                          "residues.append([name,resn,resv,alt,elem,q,ss,x,y,z])",
#                          space=space)

                #########   CA
                #print "state",stan,"CA"
                output_CA.write(str(stan+1))
                lista = cmd.get_model(
                    "(%s and %s) and polymer and elem C and name CA " % (self.objId, self.chain), state=stan).get_coord_list()
                ll = len(lista)
                for i in xrange(ll-1,-1,-1):
                    for j in xrange(i-1,-1,-1):
                        output_CA.write("\t%08.3f" % RMSD(lista[i],lista[j]))
                output_CA.write("\n")
                output_CA.flush()


                #########   CB
                #print "state",stan,"CB"
                output_CB.write(str(stan+1))
                """lista = cmd.get_model(
                    "(%s and %s) and polymer and elem C and name CB " % (self.objId, self.chain), state=stan).get_coord_list()
                ll = len(lista)
                for i in xrange(ll-1,-1,-1):
                    for j in xrange(i-1,-1,-1):
                        output_CB.write("\t%08.3f" % RMSD(lista[i],lista[j]))
                print "Num of resids cb", ll"""
                model = cmd.get_model(
                    "(%s and %s) and polymer and elem C and (name CA or name CB) " % (self.objId, self.chain),
                    state=stan)
                residues = {}
                for a in model.atom:
                    residues[a.resi] = residues.get(a.resi, []) + (a.coord if a.name == "CB" else [])
                #print residues
                lista = sorted(residues.keys(),key=lambda x: int(x))
                ll = len(lista)
                print lista,ll
                print residues
                for i in xrange(ll - 1, -1, -1):
                    for j in xrange(i - 1, -1, -1):
                        output_CB.write("\t%08.3f" % (RMSD(residues[lista[i]], residues[lista[j]]) if residues[lista[i]] and residues[lista[j]] else 1000.))

                output_CB.write("\n")
                output_CB.flush()
                #########   heavy

                #print "state", stan, "heavt"
                output_heavy.write(str(stan+1))
                model  = cmd.get_model(
                    "(%s and %s) and polymer and (elem C or elem N or elem O or elem S) " % (self.objId, self.chain), state=stan)
                residues = {}
                for a in model.atom:
                    residues[a.resi] = residues.get(a.resi, []) + [a.coord]

                lista = sorted(residues.keys(),key=lambda x: int(x))
                ll = len(lista)
                for i in xrange(ll - 1, -1, -1):
                    for j in xrange(i - 1, -1, -1):
                        output_heavy.write("\t%08.3f" % minRMSD(residues[lista[i]], residues[lista[j]]))
                #print "Num of resids heavy", ll
                output_heavy.write("\n")
                output_heavy.flush()
                del model
                del lista

    def makeMultiChainContactFile(self, step=False,progress=False):
        if Structure.isRNA:
            self.makeMultiChainContactFile_rna(step, progress)
        else:
            self.makeMultiChainContactFile_protein(step,progress)

    def makeMultiChainContactFile_rna(self, step=False,progress=False):
        name =  self.temp_path + "/_temp_" + self.objId + "_multichain_{}.map"
        #print "Calculating multichain contact map"
        with open(name.format("C1"), "w", 1) as output_C1, open(name.format("C4"), "w", 1) as output_C4, \
                open(name.format("O5"), "w", 1) as output_O5, open(name.format("heavy"), "w", 1) as output_heavy, \
                open(name.format("canonical"), "w", 1) as output_canon:
            for stan in [1]: ### TODO potentially multichain multistate
                #xrange(0, self.num_states, step if step else 1):
                #                space = {'residues': []}
                #                cmd.iterate_state(1, "( %s and %s )" % (self.objId, self.chain),
                #                          "residues.append([name,resn,resv,alt,elem,q,ss,x,y,z])",
                #                          space=space)
                #########   CA
                base_model = cmd.get_model(
                    "(%s and c. %s) and polymer and (elem C or elem N or elem O or elem P) " % (
                    self.objId, self.chain_simple), state=stan).atom

                base_residues = {}
                for a in base_model:
                    base_residues[(int(a.resi),a.resn)] = base_residues.get((int(a.resi),a.resn), []) + [(a.name, a.coord)]
                #print "".join([x[1] for x in sorted(base_residues)])
                #print seq1("".join([x[1] for x in sorted(base_residues)]))
                num_res = len(base_residues)
                base_seq = Sekwencja("base", seq1("".join([x[1] for x in sorted(base_residues)])))
                base_residues = list(zip(*sorted(base_residues.items(), key=lambda x: x[0][0]))[1])
                del base_model

                other_models = []
                other_seqs = []
                for ch in self.chains_to_keep:
                    model = cmd.get_model(
                    "(%s and c. %s) and polymer and (elem C or elem N or elem O or elem P) " % (
                    self.objId, ch), state=stan).atom
                    residues = {}
                    for a in model:
                        residues[(int(a.resi), a.resn)] = residues.get((int(a.resi), a.resn), []) + [(a.name, a.coord)]
                    other_models.append(list(zip(*sorted(residues.items(), key=lambda x: x[0][0]))[1]))
                    other_seqs.append(Sekwencja(len(other_seqs), seq1("".join([x[1] for x in sorted(residues)]))))
                del residues

                alignment,names = consensus([base_seq]+other_seqs)
                base_idx = names.index("base")
                names = [base_residues if x=="base" else other_models[x] for x in names]
                alignment = [list(x)[::-1] for x in alignment]
                for s,seq in enumerate(alignment):
                    for i,e in enumerate(seq):
                        if e!="-":
                            seq[i] = names[s].pop()
                        else:
                            seq[i] = False
                assert len(alignment[0])  == max((len(x.seq) for x in [base_seq]+other_seqs)) ### TODO: temporarily, all relative to base_model

                #### CA
                output_C1.write(str(stan))
                output_C4.write(str(stan))
                output_O5.write(str(stan))
                output_heavy.write(str(stan))
                output_canon.write(str(stan))
                ll = len(alignment[0])
                #print stan,"lens",[len(x) for x in alignment],"and there are",len(alignment)
                lc = len(alignment)
                for i in xrange(ll-1,-1,-1):
                    if not alignment[base_idx][i]:
                        continue
                    if progress:
                        progress("Matrix row: {}/{}".format(num_res-i, num_res))
                    for j in xrange(i-1,-1,-1):
                        if not alignment[base_idx][j]:
                            continue
                        d1 = 1000.
                        d4 = 1000.
                        d5 = 1000.
                        dh = 1000.
                        dc = 1000.
                        for x in xrange(lc):
                            for y in xrange(lc):
                                if x==y: continue
                                if not alignment[x][i] or not alignment[y][j]:
                                    continue
                                x1 = [tmp for tmp in alignment[x][i] if tmp[0]=="C1'"][0][1]
                                y1 = [tmp for tmp in alignment[y][j] if tmp[0] == "C1'"][0][1]
                                d1 = min(d1, RMSD(x1,y1))

                                x4 = [tmp for tmp in alignment[x][i] if tmp[0] == "C4'"][0][1]
                                y4 = [tmp for tmp in alignment[y][j] if tmp[0] == "C4'"][0][1]
                                d4 = min(d4, RMSD(x4, y4))

                                x5 = [tmp for tmp in alignment[x][i] if tmp[0] == "O5'"][0][1]
                                y5 = [tmp for tmp in alignment[y][j] if tmp[0] == "O5'"][0][1]
                                d5 = min(d5, RMSD(x5, y5))

                                xh = [tmp[1] for tmp in alignment[x][i]]
                                yh =[tmp[1] for tmp in alignment[y][j]]
                                dh = min(dh,minRMSD(xh, yh))

                                xc = [tmp[1] for tmp in alignment[x][i] if tmp[0] in ["N1","N3"]] # TODO no canon control
                                yc =[tmp[1] for tmp in alignment[y][j] if tmp[0] in ["N1","N3"]]
                                dc = min(dc,minRMSD(xc, yc))

                                """xb = [tmp for tmp in alignment[x][i] if tmp[0] == "CB"]
                                if xb:
                                    xb = xb[0][1]
                                else:
                                    continue
                                yb = [tmp for tmp in alignment[y][j] if tmp[0] == "CB"]
                                if yb:
                                    yb = yb[0][1]
                                else:
                                    continue
                                db = min(db, RMSD(xb, yb))"""
                        #if min(da,db,dh) < 40: print i,j,da,db,dh
                        output_C1.write("\t%08.3f" % d1)
                        output_C4.write("\t%08.3f" % d4)
                        output_O5.write("\t%08.3f" % d5)
                        output_heavy.write("\t%08.3f" % dh)
                        output_canon.write("\t%08.3f" % dc)
                output_C1.write("\n")
                output_C4.write("\n")
                output_O5.write("\n")
                output_heavy.write("\n")
                output_canon.write("\n")
                output_C1.flush()
                output_C4.flush()
                output_O5.flush()
                output_canon.flush()
                del alignment
        #print "doen calculating multichain map"



    def makeMultiChainContactFile_protein(self, step=False,progress=False):
        name =  self.temp_path + "/_temp_" + self.objId + "_multichain_{}.map"
        #print "Calculating multichain contact map"
        with open(name.format("CA"), "w", 1) as output_CA, open(name.format("CB"), "w", 1) as output_CB, open(
                name.format("heavy"), "w", 1) as output_heavy:
            for stan in [1]: ### TODO potentially multichain multistate
                #xrange(0, self.num_states, step if step else 1):
                #                space = {'residues': []}
                #                cmd.iterate_state(1, "( %s and %s )" % (self.objId, self.chain),
                #                          "residues.append([name,resn,resv,alt,elem,q,ss,x,y,z])",
                #                          space=space)
                #########   CA
                base_model = cmd.get_model(
                    "(%s and c. %s) and polymer and (elem C or elem N or elem O or elem S) " % (
                    self.objId, self.chain_simple), state=stan).atom

                base_residues = {}
                for a in base_model:
                    base_residues[(int(a.resi),a.resn)] = base_residues.get((int(a.resi),a.resn), []) + [(a.name, a.coord)]
                #print "".join([x[1] for x in sorted(base_residues)])
                #print seq1("".join([x[1] for x in sorted(base_residues)]))
                num_res = len(base_residues)
                base_seq = Sekwencja("base", seq1("".join([x[1] for x in sorted(base_residues)])))
                base_residues = list(zip(*sorted(base_residues.items(), key=lambda x: x[0][0]))[1])
                del base_model

                other_models = []
                other_seqs = []
                for ch in self.chains_to_keep:
                    model = cmd.get_model(
                    "(%s and c. %s) and polymer and (elem C or elem N or elem O or elem S) " % (
                    self.objId, ch), state=stan).atom
                    residues = {}
                    for a in model:
                        residues[(int(a.resi), a.resn)] = residues.get((int(a.resi), a.resn), []) + [(a.name, a.coord)]
                    other_models.append(list(zip(*sorted(residues.items(), key=lambda x: x[0][0]))[1]))
                    other_seqs.append(Sekwencja(len(other_seqs), seq1("".join([x[1] for x in sorted(residues)]))))
                del residues

                alignment,names = consensus([base_seq]+other_seqs)
                base_idx = names.index("base")
                names = [base_residues if x=="base" else other_models[x] for x in names]
                alignment = [list(x)[::-1] for x in alignment]
                for s,seq in enumerate(alignment):
                    for i,e in enumerate(seq):
                        if e!="-":
                            seq[i] = names[s].pop()
                        else:
                            seq[i] = False
                assert len(alignment[0])  == max((len(x.seq) for x in [base_seq]+other_seqs)) ### TODO: temporarily, all relative to base_model

                #### CA
                output_CA.write(str(stan))
                output_CB.write(str(stan))
                output_heavy.write(str(stan))
                ll = len(alignment[0])
                #print stan,"lens",[len(x) for x in alignment],"and there are",len(alignment)
                lc = len(alignment)
                for i in xrange(ll-1,-1,-1):
                    if not alignment[base_idx][i]:
                        continue
                    if progress:
                        progress("Matrix row: {}/{}".format(num_res-i, num_res))
                    for j in xrange(i-1,-1,-1):
                        if not alignment[base_idx][j]:
                            continue
                        da = 1000.
                        db = 1000.
                        dh = 1000.
                        for x in xrange(lc):
                            for y in xrange(lc):
                                if x==y: continue
                                if not alignment[x][i] or not alignment[y][j]:
                                    continue
                                xa = [tmp for tmp in alignment[x][i] if tmp[0]=="CA"][0][1]
                                ya = [tmp for tmp in alignment[y][j] if tmp[0] == "CA"][0][1]
                                da = min(da, RMSD(xa,ya))

                                xh = [tmp[1] for tmp in alignment[x][i]]
                                yh =[tmp[1] for tmp in alignment[y][j]]
                                dh = min(dh,minRMSD(xh, yh))

                                xb = [tmp for tmp in alignment[x][i] if tmp[0] == "CB"]
                                if xb:
                                    xb = xb[0][1]
                                else:
                                    continue
                                yb = [tmp for tmp in alignment[y][j] if tmp[0] == "CB"]
                                if yb:
                                    yb = yb[0][1]
                                else:
                                    continue
                                db = min(db, RMSD(xb, yb))
                        #if min(da,db,dh) < 40: print i,j,da,db,dh
                        output_CA.write("\t%08.3f" % da)
                        output_CB.write("\t%08.3f" % db)
                        output_heavy.write("\t%08.3f" % dh)
                output_CA.write("\n")
                output_CB.write("\n")
                output_heavy.write("\n")
                output_CA.flush()
                output_CB.flush()
                output_heavy.flush()
                del alignment
        #print "doen calculating multichain map"

    def paintInserts(self):
        for res in self.residues:
            if res.insert:
                cmd.select("tmp_select", "%s and  %s and i. %s" % (self.objId, self.chain, res.pdbid))
                cmd.color("gray70", "tmp_select")
                # TODO maybe transparency?
                cmd.deselect()

    def recolorSSarray(self, data, vmin, distance_intra=8., distance_inter=24., restricted=False, comparison=False,
                       all_combos=True,state = 1, any=any, nonwc = False):
        """-1. - not important
        0. - FP
        1. - TP intra
        2. - TP inter
        3. - TP both
        """
        if state != self.current_state:
            self.makeContactMap(state)
        #print "restricted",self.residues,len(self.residues)
        #print "notrestricted",self.sequence.replace(".", "-").replace("-", ""), len(self.sequence.replace(".", "-").replace("-", ""))
        #print "restricted is", restricted
        #print data,type(data),data.shape
        #print "##"
        size = len(self.sequence.replace(".", "-").replace("-", "") if not restricted else self.residues)
        out = np.zeros((size, size))
        out.fill(-1.)
        for x in xrange(size):
            for y in xrange(x, size):
                xh =x
                yh = y
                #if not restricted:
                #    xh = self.translations.unal_fasta2structseq[x]
                #    yh = self.translations.unal_fasta2structseq[y]


                if data[xh][yh] < vmin or type(data[xh][yh]) == np.ma.core.MaskedConstant:
                    pass
                else:
                    if restricted:
                        ssx = x
                        ssy = y
                        px = self.translations.structseq2pdb[x]# residues[x].pdbid
                        py = self.translations.structseq2pdb[y]# residues[y].pdbid
                        if px is None or py is None:
                            continue
                    else:
                        ssx = self.translations.singleplot_native(x) #self.sequence_residues[x]
                        ssy = self.translations.singleplot_native(y) #self.sequence_residues[y]
                        py = self.translations.singleplot_native(y)
                        px = self.translations.singleplot_native(x)
                        #if not px or not py or px is None or py is None:
                        if px is None or py is None:
                            #if x==0 : print data[x][y], x, y, ssx, ssy, px, py
                            continue
                    sc = 0.1
                    if (any and 0. < self.any_maps[Structure.flat_modes[Structure.mode]][ssx][ssy] < distance_intra) or \
                            (not any and 0. < self.maps[Structure.flat_modes[Structure.mode]][ssx][ssy] < distance_intra):
                        sc = 1.
                    ##
                    if len(self.chains_to_keep)>1:
                        #if 0. < self.multichain_min_rmsd(px, py, all_combos=all_combos) < distance_inter:
                        #print self.interchain_maps[Structure.mode][ssx][ssy]
                        if 0. < self.interchain_maps[Structure.flat_modes[Structure.mode]][ssx][ssy] < distance_inter:
                            #                        print "will rms",distance_intra,px,py,ssx,ssy
                            sc += 2.
                    out[x][y] = sc
                    #if x==0:
                    #    print out[x][y],x,y,ssx,ssy,px,py
        for x in xrange(size):
            for y in xrange(0, x):
                #if y <= x:
                    if comparison:
                        contacts = self.maps[Structure.flat_modes[Structure.mode]]
                        if restricted:
                            ax = self.translations.singleplot_restrict_native(x)
                            ay = self.translations.singleplot_restrict_native(y)
                            if ax is not None and ay is not None:
                                if Structure.flat_modes[Structure.mode] == "canonical":
                                    if nonwc:
                                        out[x][y] = 5 if contacts[x][y] and (contacts[x][y] < 5.) else -1.
                                    else:
                                        out[x][y] = 5 if contacts[x][y] and (contacts[x][y] < 2.) else -1.
                                else:
                                    out[x][y] = 5 if contacts[x][y] and (contacts[x][y] < distance_intra) else -1.
                            else:
                                out[x][y] = -1.
                        else:
                            ax = self.translations.singleplot_native(x)
                            ay = self.translations.singleplot_native(y)
                            if ax is not None and ay is not None:
                                if Structure.flat_modes[Structure.mode] == "canonical":
                                    if nonwc:
                                        out[x][y] = 5 if contacts[ax][ay] and (contacts[ax][ay] < 5.) else -1.
                                    else:
                                        out[x][y] = 5 if contacts[ax][ay] and (contacts[ax][ay] < 2.) else -1.
                                else:
                                    out[x][y] = 5 if contacts[ax][ay] and (contacts[ax][ay] < distance_intra) else -1.
                            else:
                                out[x][y] = -1.
                    else:
                        out[x][y] = out[y][x]
        out = np.ma.masked_where(out < 0., out)
        return out

    def makeSSarray(self,data,comparison=False,distance=8.,restricted=False, state=1, nonwc = False):
        #print "COMPARISON",comparison,restricted
        if state != self.current_state:
            self.makeContactMap(state)

        if restricted:
            return self.makeSSarray_restricted(data,comparison,distance,nonwc)
        else:
            return self.makeSSarray_unrestricted(data,comparison,distance,nonwc)


    def makeSSarray_restricted(self,data,comparison=False,distance=8.,nonwc=False,state=1):
        size =  len(self.residues)
        output = np.zeros((size,size))
        output.fill(-1.)
        for x in xrange(size):
            for y in xrange(x,size):
                ax = self.translations.singleplot_restrict(x)
                ay = self.translations.singleplot_restrict(y)
                if ax is not None and ay is not None:
                    output[x][y] = data[ax][ay]
                else:
                    output[x][y] = -1.
        TP = None
        if comparison:
            TP = 0
            #print "COMPARISON"
            contacts = self.maps[Structure.flat_modes[Structure.mode]]
            #print "contacts",contacts,len(contacts)
            for x in xrange(size):
                for y in xrange(0,x):
                    ax = self.translations.singleplot_restrict_native(x)
                    ay = self.translations.singleplot_restrict_native(y)
                    if ax is not None and ay is not None:
                        if Structure.flat_modes[Structure.mode] == "canonical":
                            if nonwc:
                                output[x][y] = 5*(contacts[x][y] < 5.) if contacts[x][y] else -1.
                            else:
                                output[x][y] = 5*(contacts[x][y] < 2.) if contacts[x][y] else -1.
                        else:
                            output[x][y] = 5*(contacts[x][y]<distance) if contacts[x][y] else -1.
                    else:
                        output[x][y] = -1.

        else:
            for x in xrange(size):
                for y in xrange(x,size):
                    output[y][x] = output[x][y]
        output = np.ma.masked_where(output < 0., output)

        return output#,TP

    def makeSSarray_unrestricted(self,data,comparison=False,distance=8.,nonwc=False):
        size =  len(self.sequence.replace("-","").replace(".",""))
        output = np.zeros((size,size))
        output.fill(-1.)
        for x in xrange(size):
            for y in xrange(x,size):
                ax = self.translations.singleplot(x)
                ay = self.translations.singleplot(y)
                if ax is not None and ay is not None:
                    output[x][y] = data[ax][ay]
                else:
                    output[x][y] = -1.

        TP = None
        if comparison:
            TP = 0
            contacts = self.maps[Structure.flat_modes[Structure.mode]]
            for x in xrange(size):
                for y in xrange(0,x):
                    ax = self.translations.singleplot_native(x)
                    ay = self.translations.singleplot_native(y)
                    if ax is not None and ay is not None:
                        if Structure.flat_modes[Structure.mode] == "canonical":
                            if nonwc:
                                output[x][y] = 5*(contacts[ax][ay] < 5.) if contacts[ax][ay]else -1.
                            else:
                                output[x][y] = 5*(contacts[ax][ay] < 2.) if contacts[ax][ay] else -1.
                        else:
                            output[x][y] = 5*(contacts[ax][ay]<distance) if contacts[ax][ay] else -1.
                    else:
                        output[x][y] = -1.
                    TP += (output[x][y] > 1)
        else:
            for x in xrange(size):
                for y in xrange(x,size):
                    output[y][x] = output[x][y]
        output = np.ma.masked_where(output < 0., output)
        return output

    def plotSS(self, figure, hmap, restricted=False):

        size = len(self.sequence.replace(".", "-").replace("-", "") if not restricted else self.residues)

        plt.figure(figure.number)
        assert plt.gcf() == figure

#        print self.residues
#        print [vars(i) for i in self.residues]
#        print "###"
#        print [vars(i) for i in self.residues if i.ss == '.']

        if restricted:
            beta = [idx+0.5 for idx, s in enumerate(self.residues) if s.ss == "S"]
            alpha = [idx+0.5 for idx, s in enumerate(self.residues) if s.ss == "H"]
            gap = [idx+0.5 for idx, s in enumerate(self.residues) if s.ss == "."]
        else:
            beta = [x+0.5 for x in [self.translations.resid2unal_fasta(s.pdbid) for s in self.residues if s.ss == "S"]
                    if x is not None]
            gap = [x+0.5 for x,e in enumerate(self.translations.unal_fasta2structseq) if e is None]
#                   [self.translations.resid2unal_fasta(s.pdbid) for s in self.residues if s.ss == "."] if
#                   x is not None]
            alpha = [x+0.5 for x in [self.translations.resid2unal_fasta(s.pdbid) for s in self.residues if s.ss == "H"]
                     if x is not None]
        ##BELOW XAXIS ####
        m = plt.subplot2grid((60, 60), (56, 6), colspan=55, rowspan=4, sharex=hmap)
        m.plot(range(size), [1 for x in xrange(size)], color='grey')
        m.plot(beta, [1] * len(beta), marker=ur'$\u21D2$', linestyle='None', color='blue')
        #m.plot(beta, [1] * len(beta), 'y>')
        m.plot(alpha, [1] * len(alpha), marker=ur'$\u056E$', linestyle='None',color='red')
        #m.plot(alpha, [1] * len(alpha), 'gv')
        m.plot(gap, [1] * len(gap), 'x', color='grey',linestyle='None')
        #m.plot(gap, [1] * len(gap), 'x', color='grey')
        m.set_ylim(0.9999, 1.000004)
        m.set_xlim([0, size])
        m.axis('off')
        hmap.tick_params(axis='x', pad=22)
        plt.setp(m.get_xticklabels(), visible=True)
        plt.setp(m.get_yticklabels(), visible=False)
        plt.subplots_adjust(hspace=0, wspace=0)
        #plt.subplots_adjust(left=0.03, bottom=0.03, right=1, top=1, wspace=0, hspace=0)
        ##LEFT TO XAXIS ####
        n = plt.subplot2grid((60, 60), (0, 0), colspan=4, rowspan=55, sharey=hmap)
        n.plot([1 for x in xrange(size)], range(size), color='grey')
        n.plot([1] * len(beta), beta, linestyle='None', marker=ur'$\u21D1$',color='blue') #E017 #221D
        n.plot([1] * len(alpha), alpha, linestyle='None', marker=ur'$\u221D$',color='red')#10454
        n.plot([1] * len(gap), gap, marker='x',linestyle='None',  color='grey')
        n.set_xlim(0.9999, 1.000004)
        n.set_ylim([0, size])
        n.axis('off')
        plt.setp(n.get_yticklabels(), visible=True)
        plt.setp(n.get_xticklabels(), visible=False)
        plt.subplots_adjust(hspace=0, wspace=0)
        hmap.tick_params(axis='y', pad=22)
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        #plt.tight_layout()

        return [m, n]