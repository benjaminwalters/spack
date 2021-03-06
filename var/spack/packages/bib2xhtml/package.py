from spack import *
from glob import glob

class Bib2xhtml(Package):
    """bib2xhtml is a program that converts BibTeX files into HTML."""
    homepage = "http://www.spinellis.gr/sw/textproc/bib2xhtml/"
    url='http://www.spinellis.gr/sw/textproc/bib2xhtml/bib2xhtml-v3.0-15-gf506.tar.gz'

    version('3.0-15-gf506', 'a26ba02fe0053bbbf2277bdf0acf8645')

    def url_for_version(self, v):
        return ('http://www.spinellis.gr/sw/textproc/bib2xhtml/bib2xhtml-v%s.tar.gz' % v)

    def install(self, spec, prefix):
        # Add the bst include files to the install directory
        bst_include = join_path(prefix.share, 'bib2xhtml')
        mkdirp(bst_include)
        for bstfile in glob('html-*bst'):
            install(bstfile, bst_include)

        # Install the script and point it at the user's favorite perl
        # and the bst include directory.
        mkdirp(prefix.bin)
        install('bib2xhtml', prefix.bin)
        filter_file(r'#!/usr/bin/perl',
                    '#!/usr/bin/env BSTINPUTS=%s perl' % bst_include,
                    join_path(prefix.bin, 'bib2xhtml'))
