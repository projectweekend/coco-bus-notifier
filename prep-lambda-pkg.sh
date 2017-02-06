#!/usr/bin/env bash
mkdir deploy
cp requirements.txt ./deploy
cp ./lambda/main.py ./deploy
cd deploy
pip install -r requirements.txt -t .
zip -r lambda.zip .
cd ..
mv deploy/lambda.zip lambda.zip
rm -r deploy
