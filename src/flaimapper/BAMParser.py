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


import pysam


class BAMParser:
    """parseNcRNA is a class that parses the BAM alignment files using pysam.
    """
    def __init__(self, region, alignment):
        self.region = region
        self.alignment = pysam.AlignmentFile(alignment, 'rb')

    def parse_reads(self):
        if(self.region[0] in self.alignment.references):
            for read in self.alignment.fetch(self.region[0], self.region[1], self.region[2]):

                if len(read.blocks) > 0:  # ensure the read is acutally aligned
                    # First coordinate is given at 0 base, the second as 1
                    # Therefore the second is converted with "-1"
                    yield (read.blocks[0][0], read.blocks[-1][1] - 1)
        else:
            raise Exception("Call to non-existing region")

    def __iter__(self):
        for read in self.parse_reads():
            yield read
