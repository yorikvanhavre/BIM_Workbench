#!env sh
cd ..
lupdate *.ui -ts translations/uifiles.ts
pylupdate5 *.py -ts translations/pyfiles.ts
lconvert -i translations/uifiles.ts translations/pyfiles.ts -o translations/BIM.ts
rm translations/pyfiles.ts
rm translations/uifiles.ts
cd utils
./updateCrowdin.py update
