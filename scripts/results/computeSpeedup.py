import optparse

def nbIter(filename, timeLimit):
    if(timeLimit == 0.0):
        return len(open(filename, "r").readlines())
    else:
        lines = open(filename, "r").readlines()
        times = [float(v.replace(",\n", "")) for v in lines]
        cum, nb = 0, 0
        while(cum < timeLimit):
            cum += times[nb]
            nb += 1
        return nb
if __name__=="__main__":
    parser = optparse.OptionParser()
    parser.add_option('-i','--input', help="input directory", default="")
    parser.add_option('-f','--time', help="time limits", default="0.0")

    (opts, args) = parser.parse_args()
    timeLimit = float(opts.time)

    comp = [("GVPM_L2_a2m_bre_areaMIS_null", "GVPM_L2_a2m_bre_areaMIS"),
            ("GVPM_L2_a2m_distance_areaMIS_null", "GVPM_L2_a2m_distance_areaMIS")]

    comp += [("GVPM_L2_a2m_bre_areaMIS_null", "SPPM_a2m_bre"),
            ("GVPM_L2_a2m_distance_areaMIS_null", "SPPM_a2m_distance")]

    for c1,c2 in comp:
        c1F = nbIter(opts.input+"/"+c1+"_time.csv", timeLimit)
        c2F = nbIter(opts.input+"/"+c2+"_time.csv", timeLimit)

        print(c1, "vs", c2)
        print("Speedup: ", float(c1F) / float(c2F))