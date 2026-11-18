# CanBERT+

## Environment Setup
Please follow the command to prepare dependency.
```
conda create -n canbert python=3.12
conda activate canbert
pip install -r requirements.txt
```
It is not necessary to use conda environment.

## Data Preprocessing
It needs to prepare the data.

Go to model and execute the following command.
```
python gen_vocab.py -i /path/to/data/
```

## Model Pre-training
The next step is to pretrain the model. It will take few hours.
```
python can_ids.py -i /path/to/data/orig.csv
```

## Model Fine-tuning
With the pretrained model, it can fine-tune it based on new datasets.
```
python can_finetune.py -i /path/to/data/mcan/g80_mcan_fuzzing_data.csv
python can_finetune.py -i /path/to/data/mcan/g80_mcan_ddos_data.csv
```
When the size of data set is too small, it may be necessary to increase patience to obtain reliable result.

## Dataset
The evaluated datasets are not collected by authors. Hence, please cite each dataset when you are planning to use it.
