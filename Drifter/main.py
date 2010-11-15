import gettext
gettext.install('why-so-spherious')

from simulation.model import Model
from simulation.view import View
from simulation.presenter import Presenter

def main():
    Presenter(Model(), View()).run()

if __name__ == '__main__':
    main()
