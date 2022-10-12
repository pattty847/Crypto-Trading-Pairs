import argparse
import sys

# TODO: FINISH LATER

class Parser():
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            prog='Crypto Thing',
            description='It does stuff idk yet.',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog = ""  
        )
        parser.add_argument('-c', '--cointegration', action='store_true', help='Display cointegration heatmap for a list of tickers.')
        parser.add_argument('-s', '--spread', action='store_true', help='Plot the spread between two tickers.')
        parser.add_argument('-z', '--zscore', action='store_true', help='listen')
        args = parser.parse_args()
        if args.listen:
            buffer = ''
        else:
            buffer = sys.stdin.read()
        self.execute_command(args)


    def execute_command(self, args):
        if args.cointegration:
            pass