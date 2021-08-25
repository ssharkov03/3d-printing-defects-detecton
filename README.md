# 3d-printing-defects-detecton

#### Model training notebook
https://www.kaggle.com/sergeisharkov/3d-printing-defects-detection-notebook

#### Defects dataset
https://www.kaggle.com/sergeisharkov/3d-printer-defects-dataset


## Getting started
In command line open directory to clone in and type  
```bash
$ git clone https://github.com/ssharkov03/3d-printing-defects-detecton.git
```


### Getting bot API TOKEN
1. Go to https://telegram.me/BotFather
2. To create a new bot type **/newbot** to the message box and press enter
3. Enter the name of the user name of your new bot
4. Copy API TOKEN you got


### Config .env
1. Open example.env file
2. Insert your token to TOKEN
3. Rename file to .env


### Local runs
If you want to run bot locally, install packages from requerements.txt
Also, install database (next step)


### Database install & config
     
##### For local runs (optional)

1. Download archive via [https://sqlitestudio.pl/](https://sqlitestudio.pl/) 
2. Unzip the archive
3. 
##### Configuring database

1. Open bot project and then open ***app.py*** file

```python
# Hyper-parameters
T = 30  # Check image from camera for defects every T seconds
database_name = "YOUR_NAME.db"  # Input your database filename
```

2. Replace database ***YOUR_NAME.db*** with the filename ****.db*** you want


### Hint #1
If you want to check images from camera every ***N*** seconds, make the following changes in ***app.py*** 


```python
# Hyper-parameters
T = N  # Check image from camera for defects every N seconds
```
_Note: the smaller the T, the worse the correct notifications timing works (especially when many people use the bot)_

### Hint #2
If you want to get ALERT notifications only if defects_probability > P,
open model.py file and commit following modifications in get_prediction():

```python


if probability_of_yes_defects.item() <= 0.5:
    option = "Minimal defects probability - "
elif 0.5 < probability_of_yes_defects.item() < P:
    option = "Low defects probability - "
elif P <= probability_of_yes_defects.item() <= 0.8:
    option = "ALERT!\nMedium defects probability - "
else:
    option = "ALERT!\nHigh defects probability - "

return [option, probability_of_yes_defects.item()]

```
_Note: 0.5 < P <= 0.8_

Afterwards open app.py file and make following modifications to hyper-parameters: 

```python
# Hyper-parameters
Q = P  # Threshold for defects
```

### Deploying bot on Heroku

#### Install GIT
1. Go to [https://git-scm.com/downloads](https://git-scm.com/downloads) and download git
2. Install git

#### Install Heroku CLI
1. Go to [https://devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
2. Install Heroku CLI

#### Deploy part
1. Sign up to [heroku.com](http://heroku.com/)
2. Create new app using *YOUR-APP-NAME*

![1](https://user-images.githubusercontent.com/37328273/129976133-5dcfdea6-7808-4387-9b0c-f5cb3498719a.jpg)

3. Go to Settings/Buildpacks, click Add buildpack and type in 
``` bash
https://buildpack-registry.s3.amazonaws.com/buildpacks/heroku-community/apt.tgz
```

![2](https://user-images.githubusercontent.com/37328273/129976265-5e5db151-2e41-40cd-ae94-0ecf6de10431.jpg)

4. Do the same with this buildpack
``` bash
heroku/python
```
5. Login heroku through command line

```bash
$ heroku login
```
6. Enter the directory of project to deploy

```bash
$ cd current_project/
```
7. Initialize a git repository

```bash
$ git init
$ heroku git:remote -a YOUR-APP-NAME
```
8. Deploy your application

```bash
$ git add .
$ git commit -am "Version 1"
$ git push heroku master
```


9. Go to Heroku website and click on Overview tab
10. After - click Configure Dynos

![4](https://user-images.githubusercontent.com/37328273/129976528-9a952195-6d91-423c-a9e0-cb2dbccf07ea.jpg)

11. And turn on worker

![5](https://user-images.githubusercontent.com/37328273/129976540-a8fb2893-f26e-4e18-997d-6537d4f851da.jpg)


## Congratulations! You've set up your first defects detection bot!


















