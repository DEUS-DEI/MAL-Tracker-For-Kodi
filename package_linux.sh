#!/bin/bash
set -e
DIR="plugin.video.maltracker"
ZIP="plugin.video.maltracker.zip"
rm -f $ZIP
cd ..
zip -r $ZIP $DIR
cd $DIR
