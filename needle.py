from collections import namedtuple
try:
    from Bio.SubsMat import MatrixInfo as matlist
    matrix_prot = matlist.blosum62
    matrix_pair_prot = matlist.blosum62
except:
    from BioPythonStub import blosum62
    matrix_prot = blosum62
    matrix_pair_prot = blosum62

# matrix={('A','B'):0,('B','A'):0,('A','A'):2,('B','B'):2,('A','-'):-1,('-','A'):-1,('-','B'):-1,('B','-'):-1,("-","-"):0}

Sequence = namedtuple('Sequence', 'id seq')

gappen_prot = -10
gapcont_prot = -0.5
# print matrix
for k, i in matrix_prot.items():
    matrix_prot[k[1], k[0]] = 1 if k[0]==k[1] else -1#i
    matrix_prot[k[0], k[1]] = 1 if k[0]==k[1] else -1#i
    matrix_prot[k[0], "-"] = gappen_prot
    matrix_prot[k[1], "-"] = gappen_prot
    matrix_prot["-", k[0]] = gappen_prot
    matrix_prot["-", k[1]] = gappen_prot
matrix_prot["-", "-"] = 0


for k, i in matrix_pair_prot.items():
    matrix_prot[k[1], k[0]] = i
matrix_prot["-", "-"] = 0
matrix_prot[".", "-"] = 0
matrix_prot["-", "."] = 0


gappen_rna = -2
gapcont_rna = -1
mismatch_rna = -1
match_rna = 1
match_n_rna = 0


matrix_rna = {}
for i in "ACTGUactguNnMm":
    matrix_rna[(i,".")] = gappen_rna
    matrix_rna[(i, "-")] = gappen_rna
    for j in "ACTGUactguNn":
        if i in "nN" or j in "nN":
            matrix_rna[(i,j)] = match_n_rna
        elif i.upper() == j.upper():
            matrix_rna[(i,j)] = match_rna
        else:
            matrix_rna[(i, j)] = mismatch_rna
matrix_rna["-", "-"] = 0
matrix_rna[".", "-"] = 0
matrix_rna["-", "."] = 0
matrix_rna["-", "-"] = 0

gappen = gappen_prot
gapcont = gapcont_prot
matrix = matrix_prot
matrix_pair = matrix_pair_prot

allowed_characters_prot = "".join(sorted(list(set(zip(*matrix_prot.keys())[0]))))
allowed_characters_rna = "".join(sorted(list(set(zip(*matrix_rna.keys())[0]))))


def pairwise_prot(ss1,ss2):
    global gappen
    global gapcont
    global matrix
    gappen = gappen_prot
    gapcont = gapcont_prot
    matrix = matrix_prot
    return try_pairwise(ss1,ss2)

def pairwise_rna(ss1,ss2):
    global gappen
    global gapcont
    global matrix
    gappen = gappen_rna
    gapcont = gapcont_rna
    matrix = matrix_rna
    return try_pairwise(ss1,ss2)

def try_pairwise(ss1,ss2):
    try:
        p= pairwise(ss1,ss2)
        return p
    except KeyError:
        raise TypeError("""There was a problem with similarity matrix during alignment. 
        Are you sure selected sequence and structure are o the same polymer (protein/nucleic acid) type?\n
        Seqs are:\n{}\n{}\n""".format(ss1,ss2))


class sekwencja:
    def __init__(self, id, seq):
        self.id = id
        self.seq = seq

    def __repr__(self):
        return str(self.id) + ":" + self.seq


def posscore(ss1, ss2, dir=2, ls=1):
    score = 0
    if dir == 1 and ss1 == ["-"]:
        score += gapcont * len(ss2) * ls
        return score
    if ss1 == ["-"]: ss1 = ["-" for x in xrange(ls)]
    for i in ss1:
        if i == ".": i = "-"
        if dir == 0 and ss2 == ["-"]:
            score += gapcont * ls
        else:
            if ss2 == ["-"]: ss2 = ["-" for x in xrange(ls)]
            for j in ss2:
                if j == ".": j = "-"
                score += matrix[(i.upper(), j.upper())]
    return score

def posscore_pair(ss1, ss2, dir=2, ls=1):
    score = 0
    if dir == 1 and ss1 == ["-"]:
        score += gapcont * len(ss2) * ls
        return score
    if ss1 == ["-"]: ss1 = ["-" for x in xrange(ls)]
    for i in ss1:
        if i == "-": i = "X"
        if dir == 0 and ss2 == ["-"]:
            score += gapcont * ls
        else:
            if ss2 == ["-"]: ss2 = ["-" for x in xrange(ls)]
            for j in ss2:
                if j == "-": j = "X"
                score += matrix_pair[(i.upper(), j.upper())]
    return score


def napraw(x, y, dists):
    new = {}
    kept = {}
    dists.pop((x, y), None)
    dists.pop((y, x), None)
    for key, item in dists.items():
        if x == key[0]:
            new[key[1]] = new.get(key[1], 0) + item
        elif x == key[1]:
            new[key[0]] = new.get(key[0], 0) + item
        elif y == key[0]:
            new[key[1]] = new.get(key[1], 0) + item
        elif y == key[1]:
            new[key[0]] = new.get(key[0], 0) + item
        else:
            kept[key] = item
    return kept, {k: i / 2. for k, i in new.items()}

def nw(ss1, ss2, save=False):
    s1 = [x.seq for x in ss1]
    s2 = [y.seq for y in ss2]
    s1l = len(s1[0])
    s2l = len(s2[0])
    path = [[None for j in xrange(s2l + 1)] for i in xrange(s1l + 1)]
    scores = [[None for j in xrange(s2l + 1)] for i in xrange(s1l + 1)]

    UL = [-1,-1]
    L = [0,-1]
    U = [-1,0]

    scores[0][0] = 0
    path[0][0] = 42
    for i in xrange(1, s1l + 1):
        path[i][0] = U
        scores[i][0] = gappen + (gapcont * (i-1))  # posscore([x[i] for x in s1],['-'],dir=1,ls=len(s2))+scores[i-1][0]
    for j in xrange(1, s2l + 1):
        path[0][j] = L
        scores[0][j] = gappen + (gapcont * (j-1))  # posscore(['-'],[y[j] for y in s2],dir=0,ls=len(s1))+scores[0][j-1]
    scores[0][0] = 0
    path[0][0] = 42
    for i in xrange(1, s1l + 1):
        for j in xrange(1, s2l + 1):
            ul = scores[i - 1][j - 1] + posscore([x[i - 1] for x in s1], [y[j - 1] for y in s2])
            u = scores[i-1][j] + (gappen*len([x[i-1] for x in s1 if x[i-1]!="-"]) if path[i-1][j]!=U else gapcont*len([x[i-1] for x in s1 if x[i-1]!="-"]))
            l = scores[i][j-1] + (gappen*len([y[j-1] for y in s2 if y[j-1]!="-"]) if path[i][j-1]!=L else gapcont*len([y[j-1] for y in s2 if y[j-1]!="-"]))

            scores[i][j] = max(ul,u,l)
            if scores[i][j] == ul:
                path[i][j] = UL
            elif scores[i][j] == u:
                path[i][j] = U
            else:
                path[i][j] = L


    res1 = ["" for s in s1]
    res2 = ["" for s in s2]

    si = s1l
    sj = s2l
    ei = 0
    ej = 0


    i = s1l
    j = s2l

    prev = (scores[i][j], i, j)
    trash1, trash2 = ["" for s in s1], ["" for s in s2]
    while scores[i][j] >= prev[0]:
        prev = (scores[i][j], i, j)
        if path[i][j] == UL:
            for ind, x in enumerate(s1):
                trash1[ind] += x[i - 1]
            for ind, y in enumerate(s2):
                trash2[ind] += y[j - 1]
            i -= 1
            j -= 1
        elif path[i][j] == U:
            for ind, x in enumerate(s1):
                trash1[ind] += x[i - 1]
            i -= 1

        else:
            for ind, y in enumerate(s2):
                trash2[ind] += y[j - 1]
            j -= 1

    trash1 = [s[:-1] for s in trash1]
    trash2 = [s[:-1] for s in trash2]


    i, j = prev[1:]
    sg = [i, j, 0]  # starts_growing
    while path[i][j] != 42:
        if path[i][j] == UL:
            for ind, x in enumerate(s1):
                res1[ind] += x[i - 1]
            for ind, y in enumerate(s2):
                res2[ind] += y[j - 1]
            i -= 1
            j -= 1
        elif path[i][j] == U:
            for ind, x in enumerate(s1):
                res1[ind] += x[i - 1]
            for ind, y in enumerate(s2):
                res2[ind] += "-"
            i -= 1

        else:
            for ind, x in enumerate(s1):
                res1[ind] += "-"
            for ind, y in enumerate(s2):
                res2[ind] += y[j - 1]
            j -= 1
        sg[2] += 1
        if scores[i][j] < scores[sg[0]][sg[1]]:
            sg = [i, j, 0]
    b1, b2 = [''], [''] ###TODO
    if sg[2]:
        b1, res1 = res1[:sg[2]], res1[sg[2]:]
        b2, res2 = res2[:sg[2]], res2[sg[2]:]


        b1, b2 = zip(*[i for i in zip(b1[::-1], b2[::-1]) if i[0] != "-" or i[1] != "-"])
        #wtf?
        b1 = "".join(b1)
        b2 = "".join(b2)
    zres1 = zip(*res1)
    zres2 = zip(*res2)
    nres1,nres2=[], []
    for _ in xrange(len(zres1)):
        if set(list(zres1[_])+list(zres2[_])) != set(["-"]):
            nres1.append(zres1[_])
            nres2.append(zres2[_])
    nres1.reverse()
    nres2.reverse()
    res1 = map(list,zip(*nres1))
    res2 = map(list,zip(*nres2))


    trash1 = map(lambda x: list(x[::-1]),trash1  )
    trash2 = map(lambda x: list(x[::-1]),trash2  ) #trashe sa juz obrocone tutaj
    trash1 = filter(lambda x: set(x)!=set(["-"]), trash1)
    trash2 = filter(lambda x: set(x)!=set(["-"]), trash2)

    while trash1 and trash2 and \
        len(set(trash1[0]))+len(set(trash2[0])) != len(set(trash1[0]+trash2[0])):
        for ri,r in enumerate(s1):
            res1[ri].append(trash1[ri].pop(0))
        for ri,r in enumerate(s2):
            res2[ri].append(trash2[ri].pop(0))

    nres1, nres2 = [],[]
    for ri,r in enumerate(s1):
        nres1.append(("-" * sg[2]) + b1[ri] + "".join(res1[ri]) + "".join(trash1[ri]) + ("-" * len(trash2[ri])))
    for ri,r in enumerate(s2):
        nres2.append(("-" * sg[2]) + b2[ri] + "".join(res2[ri]) +  ("-" * len(trash1[ri])) + "".join(trash2[ri]))

    res1 = nres1
    res2 = nres2
    if save:
        res = res1 + res2
        for ind, ss in enumerate(ss1 + ss2):
            ss.seq = res[ind]
        return tuple([x for x in ss1 + ss2]), scores[s1l][s2l]
    return (res1, res2), scores[s1l][s2l]
    ############### END LGA ########################


def pairwise(ss1, ss2, save=False):
    #print "Running pariwise with",ss1,ss2
    s1 = ss1
    s2 = ss2
    s1l = len(s1)
    s2l = len(s2)
    path = [[None for j in xrange(s2l + 1)] for i in xrange(s1l + 1)]
    scores = [[None for j in xrange(s2l + 1)] for i in xrange(s1l + 1)]

    UL = [-1,-1]
    L = [0,-1]
    U = [-1,0]

    scores[0][0] = 0
    path[0][0] = 42
    for i in xrange(1, s1l + 1):
        path[i][0] = U
        scores[i][0] = 0#gappen + (gapcont * (i-1))  # posscore([x[i] for x in s1],['-'],dir=1,ls=len(s2))+scores[i-1][0]
    for j in xrange(1, s2l + 1):
        path[0][j] = L
        scores[0][j] = 0#gappen + (gapcont * (j-1))  # posscore(['-'],[y[j] for y in s2],dir=0,ls=len(s1))+scores[0][j-1]
    scores[0][0] = 0
    path[0][0] = 42
    for i in xrange(1, s1l + 1):
        for j in xrange(1, s2l + 1):
            ##ULadd
            if "-" not in [s1[i - 1], s2[j - 1]]:
                ula = posscore(s1[i - 1], s2[j - 1])

            elif s1[i - 1]=='-' and s2[j - 1]=="-":
                ula=0
            else:
                if i<2 or s1[i-2]!="-":
                    if i<j or s2[j-2]!="-":
                        ula = gappen
                    else:
                        if s2[j-1] == "-":
                            ula = gapcont
                        else:
                            ula = gappen
                else:
                    if i<j or s2[j-2]!="-":
                        if s1[i-1]=='-':
                            ula = gapcont
                        else:
                            ula = gappen
                    else:
                        ula = 0
            #/ULadd
            ul = scores[i - 1][j - 1] + ula
            u = scores[i-1][j] + (gappen if path[i-1][j]!=U else gapcont)
            l = scores[i][j-1] + (gappen if path[i][j-1]!=L else gapcont)

            scores[i][j] = max(ul,u,l)
            if scores[i][j] == ul:
                path[i][j] = UL
            elif scores[i][j] == u:
                path[i][j] = U
            else:
                path[i][j] = L

    #from test_heatmap import plot_matrix
    #plot_matrix(scores)

    res1 = ""
    res2 = ""
    i = s1l
    j = s2l

    si = s1l
    sj = s2l
    ei = 0
    ej = 0
    #for row in scores:
    #    print row
    #################### LGA #######################
    #print "koniec to",i,j

    prev = (scores[i][j],i,j)
    trash1,trash2= "",""
    while scores[i][j]>=prev[0]:
        prev = (scores[i][j],i,j)
        if path[i][j] == UL:
            trash1+=s1[i - 1]
            trash2+= s2[j - 1]
            i -= 1
            j -= 1
        elif path[i][j] == U:
            trash1+= s1[i - 1]
            i -= 1
        else:
            trash2+= s2[j - 1]
            j -= 1

    #print "cofam do",i,j

    trash1 = trash1[:-1]
    trash2 = trash2[:-1]
    #print trash1, trash2
    i,j = prev[1:]
    sg = [i,j,0]#starts_growing
    while path[i][j] != 42:
        if path[i][j] == UL:
            res1+=s1[i - 1]
            res2+= s2[j - 1]
            i -= 1
            j -= 1
        elif path[i][j] == U:
            res1+= s1[i - 1]
            res2+= "-"
            i -= 1

        else:
            res1+= "-"
            res2+= s2[j - 1]
            j -= 1
        sg[2]+=1
        if scores[i][j]<scores[sg[0]][sg[1]]:
            sg = [i,j,0]
    res1 = res1[::-1]
    res2 = res2[::-1]

    #print res1
    #print res2
    #print sg[2],"sg2"
    b1,b2 = '',''
    if sg[2]:
        b1,res1 = res1[:sg[2]],res1[sg[2]:]
        b2,res2 = res2[:sg[2]],res2[sg[2]:]
        b1, b2 = zip(*[i for i in zip(b1, b2) if i[0] != "-" or i[1] != "-"])
        b1="".join(b1).replace("-","")
        b2="".join(b2).replace("-","")
    #print res1
    #print res2
    #print b1
    #print b2
    res1,res2 = map(list,zip(*[i for i in zip(res1,res2) if i[0]!="-" or i[1]!="-"]))
    trash1 = list("".join([x for x in trash1[::-1] if x!="-"]))
    trash2 = list("".join([x for x in trash2[::-1] if x!="-"]))
    while trash1 and trash2 and trash1[0] == trash2[0]:
        res1.append(trash1.pop(0))
        res2.append(trash2.pop(0))

    res1 = ("-"*len(b2)) + b1 + "".join(res1) + "".join(trash1) + ("-"*len(trash2))
    res2 = b2 + ("-"*len(b1)) + "".join(res2) + ("-"*len(trash1))+"".join(trash2)
    return (res1,res2), scores[s1l][s2l]




def consensus(seqs):
    dists = {}
    seqs = [sekwencja(i, s) if type(s) == type("ab") else s for i, s in enumerate(seqs)]
    for i, seq1 in enumerate(seqs):
        for seq2 in seqs[i + 1:]:
            _, d = nw([seq1], [seq2])
            dists[(seq1, seq2)] = d
    while len(dists) > 1:
        x = sorted(dists.keys(), key=lambda x: dists[x], reverse=True)[0]
        new, _ = nw(list(x[0]) if type(x[0]) == type((1, 2)) else [x[0]],
                    list(x[1]) if type(x[1]) == type((1, 2)) else [x[1]], True)
        k, n = napraw(x[0], x[1], dists)
        dists = k
        for cos in n:
            dists[(new, cos)] = n[cos]
    x = dists.keys()[0]
    new, _ = nw(list(x[0]) if type(x[0]) == type((1, 2)) else [x[0]],
                list(x[1]) if type(x[1]) == type((1, 2)) else [x[1]], True)
    new = sorted(new, key=lambda x: x.id)
    return [x.seq for x in new],[x.id for x in new]


###################Testowanie uliniowien######################
def compare(aln1, aln2):  # uliniowienia jako listy sekwencji
    return score(aln1), score(aln2)


def score(aln):
    sum = 0
    la = len(aln)
    for pos in xrange(len(aln[0])):
        for s in xrange(la - 1):
            for t in xrange(1, la):
                sum += posscore(aln[s][pos], aln[t][pos])
    return sum


from subprocess import call


def test(seqlist):
    seqs = [sekwencja(i, s) for i, s in enumerate(seqlist)]
    cons = consensus(seqs)
    with open('/tmp/notAligned.fasta', 'w', 0) as out:
        for i, s in enumerate(seqlist):
            out.write(">%d\n%s\n" % (i, s))
    call(['clustalo', '--force', '--auto', '-i', '/tmp/notAligned.fasta', '-o', '/tmp/aligned.fasta'])
    with open('/tmp/aligned.fasta') as input:
        c = ["".join(x.split("\n")[1:]) for x in input.read().split(">")[1:]]
    print cons
    print c
    print compare(cons, c)

if __name__ == "__main__":
    seqlist = ["SYSLCTAAFTFTKIPAETLHGTVTVEVQYAGTDGPCKVPAQMAVDMQTLTPVGRLITANPVITTENSKMMLELDPPFGDSYIVIGVGEKKITHHWHR", \
"AKFACSKKMTGKSIQPENLEYRIMLSVHGSQHSGMIVNDTGHETDENRAKVEITPNSPRAEATLGGFGSLGLDCEPRTGLDFSDLYYLTMNNKHWLVHKEWFHDIPLPWHAGADTGTPHWNNKEALVEFKDAHAKRQTVVVLGSQEGAVHTALAGALEAEMDGAKGRLSSGHLKCRLKMDKLRLKGVSYSLCTAAFTFTKIPAETLHGTVTVEVQYAGTDGPCKVPAQMAVDMQTLTPVGRLITANPVITESTENSKMMLELDPPFGDSYIVIGVGEKKITHHWHIRCIGVSNRDFVEGMSGGTWVDVVLEHGGCVTVMAQDKPTVDIELVTTTVSNMAEVRSYCYEASISDMASDSRCPTQGEAYLDKQSDTQYVCKRTLVDRSGSTIGKAFEATVRGAKRMAVLGDTAWDFGSVGGRGWGNGCGLFGKGSLVTCALNSLGKGIHQIFGAAFKSLFGGMSWFSQILIGTLLMWLGLNTKNGSISLMCLALGGVLIFLSTA"]
    with open('/tmp/notAligned.fasta', 'w', 0) as out:
        for i, s in enumerate(seqlist):
            out.write(">%d\n%s\n" % (i, s))
    call(['clustalo', '--force', '--auto', '-i', '/tmp/notAligned.fasta', '-o', '/tmp/aligned.fasta'])
    with open('/tmp/aligned.fasta') as input:
        c = ["".join(x.split("\n")[1:]) for x in input.read().split(">")[1:]]
    print c
    print pairwise_prot("SYSLCTAAFTFTKIPAETLHGTVTVEVQYAGTDGPCKVPAQMAVDMQTLTPVGRLITANPVITTENSKMMLELDPPFGDSYIVIGVGEKKITHHWHR", \
"AKFACSKKMTGKSIQPENLEYRIMLSVHGSQHSGMIVNDTGHETDENRAKVEITPNSPRAEATLGGFGSLGLDCEPRTGLDFSDLYYLTMNNKHWLVHKEWFHDIPLPWHAGADTGTPHWNNKEALVEFKDAHAKRQTVVVLGSQEGAVHTALAGALEAEMDGAKGRLSSGHLKCRLKMDKLRLKGVSYSLCTAAFTFTKIPAETLHGTVTVEVQYAGTDGPCKVPAQMAVDMQTLTPVGRLITANPVITESTENSKMMLELDPPFGDSYIVIGVGEKKITHHWHIRCIGVSNRDFVEGMSGGTWVDVVLEHGGCVTVMAQDKPTVDIELVTTTVSNMAEVRSYCYEASISDMASDSRCPTQGEAYLDKQSDTQYVCKRTLVDRSGSTIGKAFEATVRGAKRMAVLGDTAWDFGSVGGRGWGNGCGLFGKGSLVTCALNSLGKGIHQIFGAAFKSLFGGMSWFSQILIGTLLMWLGLNTKNGSISLMCLALGGVLIFLSTA")
    exit()

    print consensus([sekwencja(0,"SYSLCTAAFTFTKIPAETLHGTVTVEVQYAGTDGPCKVPAQMAVDMQTLTPVGRLITANPVITTENSKMMLELDPPFGDSYIVIGVGEKKITHHWHR"),
        sekwencja(1,"AKFACSKKMTGKSIQPENLEYRIMLSVHGSQHSGMIVNDTGHETDENRAKVEITPNSPRAEATLGGFGSLGLDCEPRTGLDFSDLYYLTMNNKHWLVHKEWFHDIPLPWHAGADTGTPHWNNKEALVEFKDAHAKRQTVVVLGSQEGAVHTALAGALEAEMDGAKGRLSSGHLKCRLKMDKLRLKGVSYSLCTAAFTFTKIPAETLHGTVTVEVQYAGTDGPCKVPAQMAVDMQTLTPVGRLITANPVITESTENSKMMLELDPPFGDSYIVIGVGEKKITHHWHIRCIGVSNRDFVEGMSGGTWVDVVLEHGGCVTVMAQDKPTVDIELVTTTVSNMAEVRSYCYEASISDMASDSRCPTQGEAYLDKQSDTQYVCKRTLVDRSGSTIGKAFEATVRGAKRMAVLGDTAWDFGSVGGRGWGNGCGLFGKGSLVTCALNSLGKGIHQIFGAAFKSLFGGMSWFSQILIGTLLMWLGLNTKNGSISLMCLALGGVLIFLSTA")])
    exit()

