#!/usr/bin/env python

"""FlaiMapper: computational annotation of small ncRNA derived fragments using RNA-seq high throughput data

 Here we present Fragment Location Annotation Identification mapper
 (FlaiMapper), a method that extracts and annotates the locations of
 sncRNA-derived RNAs (sncdRNAs). These sncdRNAs are often detected in
 sequencing data and observed as fragments of their  precursor sncRNA.
 Using small RNA-seq read alignments, FlaiMapper is able to annotate
 fragments primarily by peak-detection on the start and  end position
 densities followed by filtering and a reconstruction processes.
 Copyright (C) 2011-2014:
 - Youri Hoogstrate
 - Elena S. Martens-Uzunova
 - Guido Jenster


 [License: GPL3]

 This file is part of flaimapper.

 flaimapper is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 flaimapper is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.

 Documentation as defined by:
 <http://epydoc.sourceforge.net/manual-fields.html#fields-synonyms>
"""


import sys
import re
import csv
import subprocess
import operator
import math


def fasta_entry_names(fasta_file):
    names = set()
    with open(fasta_file) as fh:
        for line in fh:
            line = line.strip()
            if(line != '' and line[0] == '>'):
                names.add(line[1:])

    return list(sorted(names))


def parse_gff_annotation_name(string, gid="gene_id"):
    matches = re.findall(re.escape(gid) + '=[\'" ]?([^\'";]+)', string)
    return matches[0] if len(matches) > 0 else None


def parse_gff(gff_file):
    """2015-mar-20: Removed the Tabix library because of incompatibility
    issues.
    """

    regions = []

    with open(gff_file, 'r') as fh:
        for line in fh:
            line = line.strip()
            if(len(line) > 0 and line[0] != '#'):
                region = line.split('\t')

                start_pos = int(region[3]) - 1

                if(start_pos < 0):
                    sys.stderr.write('Masked regions (GTF/GFF) file "' + gff_file + '" is currupt:\n\n' + line + '\n\nThis format must have 1-based coordinates.\n')
                    sys.exit()

                #  @todo -> additional info column should just be the name column (1st column)
                name = None
                if(len(region) >= 9):
                    name = parse_gff_annotation_name(region[8])

                # GTF uses 1-based coordinates - convert them to 0-based
                regions.append((
                    region[0],			 # chr
                    start_pos,			 # start (0-based)
                    int(region[4]) - 1,	 # end   (0-based)
                    0,					 # score
                    name,				 # name of precursor
                    len(regions)		 # id in regions (0, 1, ...)
                ))

    return regions


def parse_table(filename, column_reference=2, column_start=3, column_end=4, column_sequence=8):
    idx = {}
    k = 0
    with open(filename, 'r') as fh:
        csv_fh = csv.reader(fh, delimiter="\t")
        for row in csv_fh:
            if k != 0:
                data = (
                    row[column_reference],
                    int(row[column_start]),
                    int(row[column_end]),
                    row[column_sequence])

                key1 = data[0].lstrip('>')

                if key1 not in idx:
                    idx[key1] = {}

                if data[1] not in idx[key1]:
                    idx[key1][data[1]] = []

                idx[key1][data[1]].append(data)

            k += 1

    return idx


def get_file_diff(f1, f2):
    out = ''
    with subprocess.Popen(['diff', f1, f2], stdout=subprocess.PIPE) as pipe:
        out = pipe.stdout.read().decode("utf-8")
    return out


def sort_frequency_dict(some_dict):
    # from pseudo random dict:
    # {34: 6, 32: 6, 36: 6, 33: 6, 35: 12, 39: 6, 38: 6}
    #
    # sort on key (this case alignment position):
    # [(32, 6), (33, 6), (34, 6), (35, 12), (36, 6), (38, 6), (39, 6)]
    sorted_list = sorted(some_dict.items(), key=operator.itemgetter(0), reverse=False)

    # sort on value (this case frequency) which preserves ordering on key/position if values are identical (called 'stable sorting;):
    # [(35, 12), (32, 6), (33, 6), (34, 6), (36, 6), (38, 6), (39, 6)]
    sorted_list.sort(key=operator.itemgetter(1), reverse=True)
    return sorted_list


def py2_round(x, d=0):
    p = 10 ** d
    return float(math.floor((x * p) + math.copysign(0.5, x))) / p
