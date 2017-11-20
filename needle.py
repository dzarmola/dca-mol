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
    matrix_prot[k[1], k[0]] = i
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
        return pairwise(ss1,ss2)
    except KeyError:
        raise RuntimeError("""There was a problem with similarity matrix during alignment. 
        Are you sure selected sequence and structure are o the same polymer (protein/nucleic acid) type?""")



# matrix["-","."]=0
#    matrix[".","-"]=0


class sekwencja:
    def __init__(self, id, seq):
        self.id = id
        self.seq = seq

    def __repr__(self):
        return str(self.id) + ":" + self.seq


def posscore(ss1, ss2, dir=2, ls=1):
    score = 0
    #    print ss1,ss2,dir,ls,
    if dir == 1 and ss1 == ["-"]:
        score += gapcont * len(ss2) * ls
        #        print score
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
                #    print score
    return score

def posscore_pair(ss1, ss2, dir=2, ls=1):
    score = 0
    #    print ss1,ss2,dir,ls,
    if dir == 1 and ss1 == ["-"]:
        score += gapcont * len(ss2) * ls
        #        print score
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
                #    print score
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
            # u = scores[i ][j-1] + ( gappen*len([y[j-1] for y in s2 if y[j-1]!="-"]) if path[i-1][j]!=L else gapcont*len([y[j-1] for y in s2 if y[j-1]!="-"])) #posscore([x[i - 1] for x in s1], ['-'], dir=1, ls=len(s2))
            # l = scores[i-1][j]  + ( gappen*len([x[i-1] for x in s1 if x[i-1]!="-"]) if path[i][j-1]!=U else gapcont*len([x[i-1] for x in s1 if x[i-1]!="-"]))#posscore(['-'], [y[j - 1] for y in s2], dir=0, ls=len(s1))
            u = scores[i-1][j] + (gappen*len([x[i-1] for x in s1 if x[i-1]!="-"]) if path[i-1][j]!=U else gapcont*len([x[i-1] for x in s1 if x[i-1]!="-"]))
            l = scores[i][j-1] + (gappen*len([y[j-1] for y in s2 if y[j-1]!="-"]) if path[i][j-1]!=L else gapcont*len([y[j-1] for y in s2 if y[j-1]!="-"]))

            scores[i][j] = max(ul,u,l)
            if scores[i][j] == ul:
                path[i][j] = UL
            elif scores[i][j] == u:
                path[i][j] = U
            else:
                path[i][j] = L
    """print "\t \t"+"\t".join(s2[0])
    ts1 = " "+s1[0]
    for i in xrange(s1l+1):
        print ts1[i],
        print "\t" + "\t".join(map(str,scores[i]))
    print "###########################################"
    print "     "+" ".join(s2[0])
    for i in xrange(s1l+1):
        print (ts1[i] if i>=0 else " "),
        print " " + " ".join(map(lambda x: "U" if x==U else "X" if x ==UL else "L" if x==L else "E",path[i]))
    print "###########################################"
    """


    res1 = ["" for s in s1]
    res2 = ["" for s in s2]
    i = s1l
    j = s2l
    while path[i][j] != 42:
        #print i,j,path[i][j]
        if path[i][j] == UL:
            for ind, x in enumerate(s1):
            #    print x
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
    if save:
        res = res1 + res2
        for ind, ss in enumerate(ss1 + ss2):
            ss.seq = res[ind][::-1]
        return tuple([x for x in ss1 + ss2]), scores[s1l][s2l]
    #print tuple([x[::-1] for x in res1 + res2]), scores[s1l][s2l]
    return tuple([x[::-1] for x in res1 + res2]), scores[s1l][s2l]

def pairwise(ss1, ss2, save=False):
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
        scores[i][0] = gappen + (gapcont * (i-1))  # posscore([x[i] for x in s1],['-'],dir=1,ls=len(s2))+scores[i-1][0]
    for j in xrange(1, s2l + 1):
        path[0][j] = L
        scores[0][j] = gappen + (gapcont * (j-1))  # posscore(['-'],[y[j] for y in s2],dir=0,ls=len(s1))+scores[0][j-1]
    scores[0][0] = 0
    path[0][0] = 42
    for i in xrange(1, s1l + 1):
        for j in xrange(1, s2l + 1):
            ##ULadd
            if "-" not in [s1[i - 1], s2[j - 1]]:
                ula = posscore(s1[i - 1], s2[j - 1])
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
    """print "\t \t"+"\t".join(s2)
    ts1 = " "+s1
    for i in xrange(s1l+1):
        print ts1[i],
        print "\t" + "\t".join(map(str,scores[i]))
    print "###########################################"
    print "     "+" ".join(s2)
    for i in xrange(s1l+1):
        print (ts1[i] if i>=0 else " "),
        print " " + " ".join(map(lambda x: "U" if x==U else "X" if x ==UL else "L" if x==L else "E",path[i]))
    print "###########################################"
    """



    res1 = ""
    res2 = ""
    i = s1l
    j = s2l
    while path[i][j] != 42:
        #print i,j,path[i][j]
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

    #print res1[::-1],res2[::-1], scores[s1l][s2l]
    res1,res2 = zip(*[i for i in zip(res1[::-1],res2[::-1]) if i[0]!="-" or i[1]!="-"])
    return ("".join(res1),"".join(res2)), scores[s1l][s2l]


def consensus(seqs):
    dists = {}
    seqs = [sekwencja(i, s) if type(s) == type("ab") else s for i, s in enumerate(seqs)]
    for i, seq1 in enumerate(seqs):
        for seq2 in seqs[i + 1:]:
            _, d = nw([seq1], [seq2])
            dists[(seq1, seq2)] = d
            #    print dists
    while len(dists) > 1:
        #        print dists
        x = sorted(dists.keys(), key=lambda x: dists[x], reverse=True)[0]
        #        print "x",x
        new, _ = nw(list(x[0]) if type(x[0]) == type((1, 2)) else [x[0]],
                    list(x[1]) if type(x[1]) == type((1, 2)) else [x[1]], True)
        #        print "new",new
        k, n = napraw(x[0], x[1], dists)
        dists = k
        for cos in n:
            dists[(new, cos)] = n[cos]
    x = dists.keys()[0]
    new, _ = nw(list(x[0]) if type(x[0]) == type((1, 2)) else [x[0]],
                list(x[1]) if type(x[1]) == type((1, 2)) else [x[1]], True)
    new = sorted(new, key=lambda x: x.id)
    #    print "\n".join([x.seq for x in new])
    #    print dists
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
    print pairwise("G-L-VGKED-S","G-LVGKQASAEED")
    exit()
    test(["GLVGGKEDS", "GLVGKQASAEEDS", "GKQAEEDS"])
    test(["GL-VGKED-S", "--GLVGKQASAEED-S", "GKQAEE-DS"])
    # test(["MPLCLKINKKHGEQTRRILIENNLLNKDYKITSEGNYLYLPIKDVDEDILKSILNIEFELVDKELEEKKIIKKPSFREIISKKYRKEIDEGLISLSYDVVGDLVILQISDEVDEKIRKEIGELAYKLIPCKGVFRRKSEVKGEFRVRELEHLAGENRTLTIHKENGYRLWVDIAKVYFSPRLGGERARIMKKVSLNDVVVDMFAGVGPFSIACKNAKKIYAIDINPHAIELLKKNIKLNKLEHKIIPILSDVREVDVKGNRVIMNLPKFAHKFIDKALDIVEEGGVIHYYTIGKDFDKAIKLFEKKCDCEVLEKRIVKSYAPREYILALDFKINKK","MVLWILWRPFGFSGRFLKLESHSITESKSLIPVAWTSLTQMLLEAPGIFLLGQRKRFSTMPETETHERETELFSPPSDVRGMTKLDRTAFKKTVNIPVLKVRKEIVSKLMRSLKRAALQRPGIRRVIEDPEDKESRLIMLDPYKIFTHDSFEKAELSVLEQLNVSPQISKYNLELTYEHFKSEEILRAVLPEGQDVTSGFSRIGHIAHLNLRDHQLSFKHLIGQVMIDKNPGITSAVNKINNIDNMYRNFQMEVLSGEQNMMTKVRENNYTYEFDFSKVYWNPRLSTEHSRITELLKPGDVLFDVFAGVGPFAIPVAKKNCTVFANDLNPESHKWLLYNCKLNKVDQKVKVFNLDGKDFLQGPVKEELMQLLGLSKERKPSVHVVMNLPAKAIEFLSAFKWLLDGQPCSSEFLPIVHCYSFSKDANPAEDVRQRAGAVLGISLEACSSVHLVRNVAPNKEMLCITFQIPASVLYKNQTRNPENHEDPPLKRQRTAEAFSDEKTQIVSNT"])
    exit()

    newhomos = [
        ['CSPGIWQLDCTHLEGKVILVAVHVASGYIEAEVIPAETGQETAYFLLKLAGRWPVKTVHTDNGSNFTSTTVKAACWWAGIKQE', ('FGIPY', '-----'),
         'NPQSQGVIESMNKELKKIIGQVRDQAEHLKTAVQMAVFIHNHKR', ('KGG', '---'),
         'IGGYSAGERIVDIIATDIQTKELQKQITKIQNFRVYYRDSRDPVWKGPAKLLWKGEGAVVIQDNSDIKVVPRRKAKIIRDYGKQMA'],
        ['SSPGIWQLDCTHLEGKVILVAVHVASGYIEAEVIPAETGQETAYFLLKLAGRWPVKTVHTDNGSNFTSTTVKAACWWAGIKQED', ('FGIPY', '-GIPY'),
         'NPQSQGVIESMNKELKKIIGQVRDQAEHLKTAVQMAVFIHNHKR', ('KGG', 'KGG'), 'GYSAGERIVDIIATDIQTK']]
    i = 0
    while i < 5:
        pairs = [x[i] for x in newhomos]
        aln = consensus(list(pairs[0]) + [x[1] for x in pairs])
        i += 1
        print pairs
        print aln

    exit()
    s1 = "GATTAA"
    s2 = "TAGAC"
    s3 = "GATAAT"
    s4 = "CAAT"
    """seqs=[sekwencja(i,s) for i ,s in enumerate([s1,s2,s3,s4])]
    print seqs
#    order([s1,s2,s3,s4])    
    consensus(seqs)"""
    test([s1, s2, s3, s4])
    test(["GKQSAAED", "GKED", "AQSAVD"])
