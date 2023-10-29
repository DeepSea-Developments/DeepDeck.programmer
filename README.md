# DeepDeck.programmer

## Getting started
This is the code for the installer to upload new release of DeepDeck. It works on Linux, Windows, and Mac.

## Compile on Linux, Windows
```
pyinstaller app.spec
```

Build the executable in the **dist** folder

## Compile on Mac
first install create-dmg if it is not installed on your OS
```
brew install create-dmg
```

To validate that it was installed correctly, execute the following command:
```
create-dmg --help
```

Then generate the compilation with the following command:
```
pyinstaller app.spec
```
Build the executable in the **dist** folder

\
Now we generate the dmg starting from the compilation generated in the previous step, executing the following bash found in the root of the project:
```
./builddmg.sh
```
Build the executable in the **dist** folder


## Note
The builddmg.sh file must have permission
```
chmod +x builddmg.sh
```

\
For more information on how to create a dmg read the following  [post](https://www.pythonguis.com/tutorials/packaging-pyqt5-applications-pyinstaller-macos-dmg/) 