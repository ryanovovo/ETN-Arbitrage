#!/bin/bash

# 切換到 conda 環境 twstock
source ~/miniconda3/etc/profile.d/conda.sh
cd /Users/ryan/Desktop/sinotrade
conda activate twstock

# 執行 terminal.py
python terminal.py
