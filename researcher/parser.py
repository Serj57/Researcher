import os
import csv
import sqlite3
import subprocess
from .config import TABLE
from .config import DATABASE


class TsharkParser:
    def __init__(self):
        self._output = 'markup.csv'
        self._db = DATABASE
        self._table = TABLE
        
    def _run_tshark(self, proto:str, pcap:str):
        args = f' -r {pcap} -E separator=, -T fields -e {proto}.stream -e frame.number -e {proto}.payload > {self._output}'
        subprocess.run("tshark" + args, stdout=subprocess.PIPE, shell=True)
    
    def _import_to_sql(self):

        conn = sqlite3.connect(self._db)
        conn.execute(f"DELETE FROM {self._table};")
        conn.commit()

        with open(self._output, 'r', encoding='utf-8') as dump:
            csv_reader = csv.reader(dump, delimiter=',')
            rows = [(int(row[0]), int(row[1]), row[2]) for row in csv_reader]
        
        conn.executemany(f'INSERT INTO {self._table} VALUES(?, ?, ?);', rows)
        conn.execute(f"DELETE FROM {self._table} WHERE data = '';")
        conn.commit()

        os.remove(self._output)

    def parse(self, proto:str, pcap:str):
        self._run_tshark(proto, pcap)
        self._import_to_sql()