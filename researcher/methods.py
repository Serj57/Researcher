from abc import ABC, abstractmethod

from prettytable import PrettyTable


from multiprocessing import Pool

from collections import Counter

from .config import DATABASE
from .config import TABLE

from math import ceil

import sqlite3


class IMethod(ABC):

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def _format(self):
        pass


class PositionalMethod(IMethod):
    def __init__(self, range:int, length:int) -> None:
        self._db = DATABASE
        self._table = TABLE
        self._positions = range
        self._per_position = length
        self._result = Counter()
    
    @staticmethod
    def _do_job(chunk:list[tuple]):
        chunk = [[row[0][index:index+2] for index in range(0, len(row[0]), 2)] for row in chunk]
        byte_counter = Counter([(index+1, byte) for payload in chunk for index, byte in enumerate(payload)])
        return byte_counter

    def run(self):
        conn = sqlite3.connect(self._db)
        cursor = conn.cursor()
        data = cursor.execute(f"SELECT data FROM {self._table}")
        payloads = data.fetchall()
        conn.close()
        pool = Pool(4)
        count = len(payloads)
        chunks = [payloads[i: i + ceil(count/4)] for i in range(0, count, ceil(count/4))]
        del payloads
        chunks = pool.map(self._do_job, chunks)
        for chunk in chunks:
            self._result.update(chunk)
        return self._format()

    def _format(self):
        pt = PrettyTable()
        pt.field_names = ['pos', 'open %', 'items']
        pt.border = False
        pt.align = 'l'
        data = list(filter(lambda item: item[0][0] < self._positions + 1, self._result.items()))
        for position in range(1, self._positions + 1):
            group = list(filter(lambda item: item[0][0]==position, data))
            if not group:
                break
            group.sort(key=lambda item: (item[0][0], -item[1]))
            items = [(item[0][1], item[1]) for item in group[:self._per_position]]
            str_items = ' '.join([f"('{item[0]}', {item[1]})" for item in items])
            pt.add_row([position, round(len(items)/len(group)*100, 1), str_items])
        del data
        return pt


class PacketPositionalMethod(IMethod):
    def __init__(self, range:int, length:int, count:int):
        self._db = DATABASE
        self._table = TABLE
        self._positions = range
        self._per_position = length
        self._count = count
        self._result = Counter()

    def _slice_streams(self):
        conn = sqlite3.connect(self._db)
        cursor = conn.cursor()
        for num in range(1, self._count + 1):
            req = f"""
                SELECT pkt_num, data
                FROM ( SELECT ROW_NUMBER() OVER (PARTITION BY stream ORDER BY packet) pkt_num,
                                data
                        FROM {self._table}) AS rank
                WHERE pkt_num = {num};
            """
            data = cursor.execute(req)
            payloads = data.fetchall()
            yield payloads

    @staticmethod
    def _do_job(item:tuple):
        payload = [item[1][index:index+2] for index in range(0, len(item[1]), 2)]
        payload_counter = Counter([(item[0], index+1, byte) for index, byte in enumerate(payload)])
        return payload_counter

    def run(self):
        pool = Pool(4)
        for chunk in self._slice_streams():
            bucket = pool.map(self._do_job, chunk)
            for slice in bucket:
                self._result.update(slice)
        return self._format()
    
    def _format(self):
        pt = PrettyTable()
        pt.field_names = ['pkt', 'pos', 'open %', 'items']
        pt.border = False
        pt.align = 'l'
        data = list(filter(lambda item: item[0][1] < self._positions + 1, self._result.items()))
        for pkt in range(1, self._count + 1):
            for position in range(1, self._positions + 1):
                group = list(filter(lambda item: item[0][0] == pkt and item[0][1] == position, data))
                if not group:
                    break
                group.sort(key=lambda item: (item[0][0], item[0][1], -item[1]))
                items = [(item[0][2], item[1]) for item in group[:self._per_position]]
                str_items = ' '.join([f"('{item[0]}', {item[1]})" for item in items])
                pt.add_row([pkt, position, round(len(items)/len(group)*100, 1), str_items])
        del data
        return pt


