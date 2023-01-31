# Installation and usage instructions

## Installation

### Requirements
- Docker Desktop
- Anaconda3
- conda-forge

if you want to use GPU you also need the following:
-  cudatoolkit 11.2
-  cudnn 8.1.0



```bash
conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0
# Anything above 2.10 is not supported on the GPU on Windows Native
python3 -m pip install "tensorflow<2.11"
# Verify install:
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```


```bash
# Create a new environment
conda create -n <name of the environment> python=3.8

# Activate the environment
conda activate <name of the environment>
```


```bash
pip install -r requirements.txt
```

## Usage

### Data collection

```bash
# create a folder for the data
mkdir Data/
mkdir Data/dataset/
mkdir Data/raw/

# create a folder for the results
mkdir Results/
```
    
```bash
# start the data collection script
cd DataCollection
python3 data_collection.py
```

### Data preprocessing

```bash
# start the data preprocessing script
cd Preprocessing
docker compose up --build -d
```

### Training

Copy the `.env.example` file to `.env` and fill in the desired values.

```bash
cd Training/
python train.py
```
