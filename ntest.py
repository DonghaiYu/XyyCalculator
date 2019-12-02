import argparse
import logging
from os.path import basename, splitext, join, isfile
import time
import tkinter as tk
import
class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text
    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

class GUI(tk.Frame):
    """ This class defines the graphical user interface """
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.generate_button = tk.Button(self.root, text="Generate", command=main)
        self.quit_button = tk.Button(self.root, text="Quit", command=self.root.quit)
        self.text_handler = None
        self.build_gui()
    def build_gui(self):
        self.root.title('Logging test')
        self.generate_button.grid(row=0, column=0)
        self.quit_button.grid(row=0, column=1)
        # Add ScrolledText widget to display logging
        st = ScrolledText.ScrolledText()
        st.configure(font='TkFixedFont')
        st.grid(row=1, sticky='ew', columnspan=2)
        # Create textlogger
        self.text_handler = TextHandler(st)

################################################################################
# Main Program Flow
#
def main():
    # log something
    logger.info('something to log')
    time.sleep(1)
    logger.info('and something one second later')
    time.sleep(1)
    logger.info('and yet another second...')

################################################################################
# Read commandline arguments
#
def get_arguments():
    parser = argparse.ArgumentParser(
        description="Test GUI logging")
    parser.add_argument('--logdir', required=False, default=None)
    parser.add_argument('--debug', action="store_const", const=logging.DEBUG, default=logging.INFO)
    a = parser.parse_args()
    return a

################################################################################
# Configure logger
#
def get_logger(log_level=logging.INFO, log_dir=None, text_handler=None):
    script = splitext(basename(__file__))[0]
    logg = logging.getLogger(script)
    logg.setLevel(log_level)
    # set up file or stdout handlers
    if log_dir:
        info_file = join(log_dir, script + '.log')
        info_handler = logging.FileHandler(info_file)
    else:
        info_handler = logging.StreamHandler()
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    info_handler.setFormatter(formatter)
    info_handler.setLevel(log_level)
    if text_handler:
        text_handler.setFormatter(formatter)
        text_handler.setLevel(log_level)
    # add the handlers to logg
    logg.addHandler(info_handler)
    if text_handler:
        logg.addHandler(text_handler)
    return logg

################################################################################
# get args, configure logger and launch GUI
#
if __name__ == '__main__':
    args = get_arguments()
    root = tk.Tk()
    gui = GUI(root)
    logger = get_logger(log_level=args.debug, log_dir=args.logdir, text_handler=gui.text_handler)
    root.mainloop()