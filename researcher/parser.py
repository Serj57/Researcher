import subprocess
import sqlite3
from .config import DATABASE
from .config import TABLE

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

        to_sql = f'sqlite3 {self._db} ".import {self._output} {self._table} --csv"'
        subprocess.run(to_sql, stdout=subprocess.PIPE, shell=True)
        
        conn.execute(f"DELETE FROM {self._table} WHERE data = '';")
        conn.commit()

    def parse(self, proto:str, pcap:str):
        self._run_tshark(proto, pcap)
        self._import_to_sql()