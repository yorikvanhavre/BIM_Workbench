#!env sh
for f in translations/*_*.ts;
    do lrelease "translations/$f";
done
