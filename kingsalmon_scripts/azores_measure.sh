#!/bin/bash
echo "please connect card 6"
python2 azores_check.py --cal --ddir 10MHZ --beams 24 --paths 1 --memoffset 320
python2 azores_check.py --cal --ddir 12MHZ --beams 24 --paths 1 --memoffset 576

echo "please connect card 16"
python2 azores_check.py --cal --ddir 12MHZ --beams 24 --paths 1 --memoffset 576
python2 azores_check.py --cal --ddir 12MHZ --beams 24 --paths 1 --memoffset 576

