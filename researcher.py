import argparse

from researcher import *


def pcap_handler(args):
    parser = TsharkParser()
    parser.parse(args.proto, args.file)


def analyze_handler(args):
    analyser = Analyzer()

    if args.method == 'pos':
        method = PositionalMethod(args.range, args.length)
    
    if args.method == 'pkt':
        method = PacketPositionalMethod(args.range, args.length, args.count)

    analyser.set_method(method)
    result = analyser.start()
    print(result)


if __name__ == '__main__':

    ### base parser ###
    base_parser = argparse.ArgumentParser(prog='Researcher')

    ### subparser ###
    subparser = base_parser.add_subparsers()

    ### analyze subparser ###
    analyze_parser = subparser.add_parser('analyze', help='Параметры анализа pcap(ng) файлов.')

    analyze_parser.add_argument('-m', '--method', required=True, choices=['pos', 'pkt'],  metavar='',
                            help='Метод анализа. Допустимые выражения: pos, pkt.')

    analyze_parser.add_argument('-r', '--range', type=int, default=32, metavar='',
                            help='Число исследуемых позиций. (default: 32)')

    analyze_parser.add_argument('-l', '--length', type=int, default=10, metavar='',
                            help='Число отображаемых байт на позицию. (default: 10)')
    
    analyze_parser.add_argument('-c', '--count', type=int, default=5, metavar='',
                            help='Число пакетов. (default: 5)')

    analyze_parser.set_defaults(handler=analyze_handler)

    ### pcap subparcer ###
    file_parser = subparser.add_parser('pcap', help='Параметры обработки pcap(ng) файлов.')
    
    file_parser.add_argument('-p', '--proto', required=True, choices=['udp', 'tcp'], metavar='',
                            help='Протокол транспортного уровня. Допустимые выражения: udp, tcp.')

    file_parser.add_argument('-f', '--file', required=True, type=str, metavar='',
                            help='Файл дампа pcap(ng).')

    file_parser.set_defaults(handler=pcap_handler)
    
    
    arg = base_parser.parse_known_args()
    arg[0].handler(arg[0])

