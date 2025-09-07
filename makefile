PYINSTALLER = pyinstaller
PYINSTALLERFLAGS = --onefile
DISTPATH = ./

all: main

main: gui_main.py console_main.py
	$(PYINSTALLER) $(PYINSTALLERFLAGS) gui_main.py --distpath $(DISTPATH)
	$(PYINSTALLER) $(PYINSTALLERFLAGS) console_main.py --distpath $(DISTPATH)

clean:
	rmdir /s/q dist
	rmdir /s/q build