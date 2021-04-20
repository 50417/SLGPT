# Mining_Tool
Mining_Tool is a tool to collect Simulink models from open source repositories such as GitHub and MATLAB Central

### Installation

Tested on Ubuntu 18.04 

First, create virtual environment using  [Anaconda] so that the installation does not conflict with system wide installs.
```sh
$ conda create -n <envname> python=3.7
```

```sh
$ cd MiningTool
```

Activate environment and Install the dependencies.
```sh
$ conda activate <envname>
$ pip install -r requirements.txt
```

Test your installation 
```sh
$ python downloadRepoFromGithub.py -h
```
This should display help information.

### Usage
downloadRepoFromGithub.py is used to automatically download projects from GitHub and update the metadata in a database.
downloadFromMathWorks.py is used to download projects from MATLAB Central.
 
 To download projects from GitHub, 
 1. Create a personal access token refering [here] 
 2. Replace <YOUR_PERSONAL_ACCESS_TOKEN> with your created token in  downloadRepoFromGithub.py
 3. Run the code as follows:
 ```sh
$ python downloadRepoFromGithub.py -q=Simulink -d=Test_dir -db=abc -flag=X
```
Dont include -flag if you dont want to restrict projects with no license file.
Full details on the flag can be viewed by running : 
```sh
$ python downloadRepoFromGithub.py -h
```

 To download projects from MATLAB Central, 
 1. Update directory, dbname and rss_url in downloadFromMathWorks.py . Ideally use the same dbname used for GitHub  
 2. Run the code as follows:
 ```sh
 python downloadFromMathWorks.py 
```

The table name where metadata is stored can be changed MathWorksRepoInfo.py and SimulinkRepoInfo.py file respectively.
### Development

Want to contribute? Great!
Mining_Tool uses python +  sqlAlchemy for fast developing.

#### Todos

 - Write Test case
 - Exception Handling


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
   [Anaconda]: <https://www.anaconda.com/distribution/>
[here]: <https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line#creating-a-token>
