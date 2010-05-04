#!/usr/bin/env python
# main.py

from vp.app import App

if __name__ == "__main__":
    try:
        a = App()
        a.setup_window(70, 60, 1)
        a.setup_ship()
        a.setup_missiles()
        a.update()
        a.loop()
    finally:
        a.quit()
