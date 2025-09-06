PYINSTALLER = pyinstaller
PYINSTALLERFLAGS = --onefile

all: main

main: main.py
	$(PYINSTALLER) $(PYINSTALLERFLAGS) main.py

clean:
	rmdir /s/q dist
	rmdir /s/q build