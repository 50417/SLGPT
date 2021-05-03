# SLGPT
Uses transfer learning to generate Simulink models from scratch 

### Installation

Tested  on Ubuntu 18.04

### Running Validity Checker and Extracting Graph Properties (via utils)
##### Requirements 
* MATLAB with Simulink R2018b/R2019b/2020b 
* Simulink Test
* Simulink Check 
* Simulink Report Generator

##### To run validity checker
```sh
> validityChecker.validityChecker(<Folder_PATH_OF_SIMULINK_MODELS>)
```

##### To extract adjacency representation of Simulink model (output JSON file is used to plot graphs )
```sh
> utils.run(<Folder_PATH_OF_SIMULINK_MODELS>,'OUTPUT_FILENAME.json')
```

NOTE : Multiple runs will append to the json file yielding bad json files. Either delete the file or use new file name. 

##### To filter Simulink models without toolbox dependency (aside from MATLAB and Simulink), StateFlow Blocks
```sh
> utils.filter_simulink(<Folder_PATH_OF_SIMULINK_MODELS>)
```


### Preparing Data
First, create virtual environment using  [Anaconda] so that the installation does not conflict with system wide installs.
```sh
$ conda create -n <envname> python=3.7
$ conda activate <envname>
```


```sh
$ python restructure_mdl.py --dataset_dir=<Folder_PATH_OF_SIMULINK_MODELS> --code_rewrite
```
 A new training file is created as 'training.txt' Experiments/Restructure folder. 
Remove the --code_rewrite flag when restructuring generated models.

### Running GPT-2 Training and Sampling 
##### Installing dependencies
```sh
$ cd GPT

$ pip install -r requirements.txt
```

### Usage
To train and sample from the model 
```sh
$  python download_model.py  124M
$ cd src
$ python train.py --dataset <PATH_TO_TRAIN_DATA> --run_name <RUN_NAME> 
$ python interactive_conditional_samples.py --temperature 0.8 --top_p 0.9 -model_name <RUN_NAME>
```

### Reproduce Plots
Go to code-process directory.
Update path to json files and database in calculatemetrics.py downloaded from TrainingDataandEvaluationData.
``` 
$ python calculatemetrics.py
``` 

NOTE: All experimental results are stored in Experiments/ directory

