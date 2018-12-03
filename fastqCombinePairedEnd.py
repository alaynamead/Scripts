#!/usr/bin/env python3.6
"""Resynchronize 2 fastq or fastq.gz files (R1 and R2) after they have been
trimmed and cleaned

WARNING! This program assumes that the fastq file uses EXACTLY four lines per
    sequence

Three output files are generated. The first two files contain the reads of the
    pairs that match and the third contains the solitary reads.

Usage:
    python fastqCombinePairedEnd.py input1 input2

input1 = LEFT  fastq or fastq.gz file (R1)
input2 = RIGHT fastq or fastq.gz file (R2)
"""

# modified from: https://github.com/enormandeau/Scripts/blob/master/fastqCombinePairedEnd.py
# by Alayna Mead (28 November 2018)
# pulls read name as the first 7 fields of name line, assuming they're separated by ":"

# Importing modules
import gzip
import sys

# Parsing user input
try:
    in1 = sys.argv[1]
    in2 = sys.argv[2]
except:
    print(__doc__)
    sys.exit(1)

#try:
#    separator = sys.argv[3]
#    if separator == "None":
#        separator = None
#except:
#    separator = " "

# Defining classes
class Fastq(object):
    """Fastq object with name and sequence
    """

    def __init__(self, name, seq, name2, qual):
        self.name = name
        self.seq = seq
        self.name2 = name2
        self.qual = qual

    def getShortname(self):
        temp = self.name.split(':')[0:6]
        return(':'.join(temp))

    def write_to_file(self, handle):
        handle.write(self.name + "\n")
        handle.write(self.seq + "\n")
        handle.write(self.name2 + "\n")
        handle.write(self.qual + "\n")

# Defining functions
def myopen(infile, mode="r"):
    if infile.endswith(".gz"):
        return gzip.open(infile, mode='rt')
    else:
        return open(infile, mode=mode)

def fastq_parser(infile):
    with myopen(infile) as f:
        while True:
            name = f.readline().strip()
            if not name:
                break

            seq = f.readline().strip()
            name2 = f.readline().strip()
            qual = f.readline().strip()
            yield Fastq(name, seq, name2, qual)

# Main
if __name__ == "__main__":
    seq1_dict = {}
    seq2_dict = {}
    seq1 = fastq_parser(in1)
    seq2 = fastq_parser(in2)
    s1_finished = False
    s2_finished = False

    if in1.endswith('fastq.gz'): 
    	stripChar = 9
    else:
    	stripChar = 6

    with myopen(in1[:-stripChar] + "_pairs_R1" + '.fastq', "w") as out1:
        with myopen(in2[:-stripChar] + "_pairs_R2" + '.fastq', "w") as out2:
            with myopen(in1[:-stripChar] + "_singles" + '.fastq', "w") as out3:
                while not (s1_finished and s2_finished):
                    try:
                        s1 = next(seq1)
                    except Exception as e:
                        s1_finished = True
                    try:
                        s2 = next(seq2)
                    except:
                        s2_finished = True

                    # Add new sequences to hashes
                    if not s1_finished:
                        seq1_dict[s1.getShortname()] = s1
                    if not s2_finished:
                        seq2_dict[s2.getShortname()] = s2

                    if not s1_finished and s1.getShortname() in seq2_dict:
                        seq1_dict[s1.getShortname()].write_to_file(out1)
                        seq1_dict.pop(s1.getShortname())
                        seq2_dict[s1.getShortname()].write_to_file(out2)
                        seq2_dict.pop(s1.getShortname())

                    if not s2_finished and s2.getShortname() in seq1_dict:
                        seq2_dict[s2.getShortname()].write_to_file(out2)
                        seq2_dict.pop(s2.getShortname())
                        seq1_dict[s2.getShortname()].write_to_file(out1)
                        seq1_dict.pop(s2.getShortname())
                        
                # Treat all unpaired reads
                for r in seq1_dict.values():
                    r.write_to_file(out3)

                for r in seq2_dict.values():
                    r.write_to_file(out3)

