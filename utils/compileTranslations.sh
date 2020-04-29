#!env sh
cd ..
for f in translations/*_*.ts;
    do lrelease "translations/$f";
done
cd utils
