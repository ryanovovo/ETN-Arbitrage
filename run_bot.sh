#!/bin/bash

# 切換到 conda 環境 twstock
source ~/miniconda3/etc/profile.d/conda.sh
cd ~/sinotrade
conda activate twstock

python ~/sinotrade/main.py

