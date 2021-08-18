# 3d-printing-defects-detecton

#### Model training notebook
https://www.kaggle.com/sergeisharkov/3d-printing-defects-detection-notebook

#### Defects dataset
https://www.kaggle.com/sergeisharkov/3d-printer-defects-dataset


## Getting started
In command line open directory to clone in and type  
```cmd
git clone https://github.com/ssharkov03/3d-printing-defects-detecton.git
```


### Getting bot API TOKEN
1. Go to https://telegram.me/BotFather
2. To create a new bot type **/newbot** to the message box and press enter.
3. Enter the name of the user name of your new bot.
4. Copy API TOKEN you got.


### Config .env
1. Open example.env file
2. Insert your token to TOKEN
3. Rename file to .env


### Local runs
If you want to run bot locally, install packages from requerements.txt


### Database install & config
1. Download archive via [https://sqlitestudio.pl/](https://sqlitestudio.pl/)
2. Unzip the archive and send SQLiteStudio.exe file to desktop
3. Open telegram bot directory and create file ***your_name.db***
4. Open it 

![1](https://user-images.githubusercontent.com/37328273/129971749-174b4c78-fae1-44f0-9eb0-70c6c62d82b8.jpg)

5. Create table and select your database name

![2](https://user-images.githubusercontent.com/37328273/129972451-83b6cb77-5788-4fa6-839b-6ed8d8022b3b.jpg)

6. Set Table name to "subs" (not subscribtions!)

![3](https://user-images.githubusercontent.com/37328273/129972475-c56ebd66-0661-4871-89dd-f9a925fa38be.jpg)

7. Set first column - *id*

![4](https://user-images.githubusercontent.com/37328273/129972484-34e9ca02-df77-4414-a4fa-e01ce6f7e2bc.jpg)

8. Set second column - *user_id*

![5](https://user-images.githubusercontent.com/37328273/129972521-a83026d5-96ce-4b39-bbaf-98cd73361921.jpg)

9. Set third column - *status*

![6](https://user-images.githubusercontent.com/37328273/129972551-4c25fbbe-6ff7-4ce9-b16c-5b214e7c1e23.jpg)

10. Set fourth column - *stream*

![7](https://user-images.githubusercontent.com/37328273/129972560-91e42b51-2dca-404c-a326-180d2bc70b70.jpg)

11. Click commit button and close application

![8](https://user-images.githubusercontent.com/37328273/129972572-1f231b82-eca2-46d1-ac01-013053de640a.jpg)

12. Open bot project and then open ***app.py*** file

![9](https://user-images.githubusercontent.com/37328273/129972590-6ffe1883-cd42-4fa3-b5dd-be731123f3a6.jpg)

13. Replace database ***database_example.db*** with ***your_name.db*** file


### Hint
If you want to get notifications every ***N*** seconds and check detail every ***K*** seconds for possible defects, \
open app.py file and make following changes: 

```python
# Hyper-parameters
YOUR_TIME_YES = K   # check image for defects every YOUR_TIME_YES, if defects prob. > 0.65, you will be notified
YOUR_TIME_ALL = N  # you will be notified every YOUR_TIME_ALL seconds about current state
```


### Hint 2
If you want to get ALERT notifications only if defects_probability > T,
open model.py file and commit following modifications in get_prediction():

```python


if probability_of_yes_defects.item() <= 0.5:
    option = "Minimal defects probability - "
elif 0.5 < probability_of_yes_defects.item() < T:
    option = "Low defects probability - "
elif T <= probability_of_yes_defects.item() <= 0.8:
    option = "ALERT!\nMedium defects probability - "
else:
    option = "ALERT!\nHigh defects probability - "

return [option, probability_of_yes_defects.item()]

```

Afterwards open app.py file and make following modifications to get_yes_defects(): 

```python
if ret and frame is not None:
    # if video stream active, then continue detection

    verdict, prob_yes_defects = get_prediction(frame)
   
    # loud notification - defects detected
    if prob_yes_defects >= T:  # T - based on verdicts in get_prediction

        # load photo to memory and push it to bot
        bio = BytesIO()
        bio.name = 'image.jpeg'
        frame = np.flip(frame, axis=-1)
        image = imget(frame)
        image.save(bio, 'JPEG')
        bio.seek(0)
```









