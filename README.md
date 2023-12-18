## Steps to setup a virtual environment (VS Code)
1. Open Terminal by pressing Ctrl+`
2. (Optional) Upgrade pip by typing ```python.exe -m pip install --upgrade pip```
2. Create virtual environment by typing ```python -m venv venv``` (You can name your virtual environment wtv you want by replacing the 2nd 'venv')
3. Click on 'Yes' on the bottom right if it says that a new environment has been created ...
4. Whenever you want to run the project in the virtual environment,
- Type ```venv/Scripts/activate``` if you have 'Scripts folder in your virtual environment folder
- Type ```venv/bin/activate``` if you have 'bin' folder in your virtual environment folder
- If you renamed your virtual environment, replace the 'venv' part with whatever you renamed it as
5. Whenever you want to stop running in the virtual environment, type ```deactivate```

Since there will be a 'requirements.txt' file, holding all the packages required to install, always do:
- ```pip list``` to check whether you have the packages installed and the correct versions
- ```pip install -r requirements.txt``` to install all the packages with the specified version from the file itself
  - If you ever want to update the packages required, type ```pip freeze > requirements.txt```
