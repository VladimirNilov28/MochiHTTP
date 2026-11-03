import argparse

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='mochi',
        description='MochiHTTP is a command-line HTTP client',
        version='0.1.0'
    )
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--host', type=str, default='localhost')
    
    args = parser.parse_args()
