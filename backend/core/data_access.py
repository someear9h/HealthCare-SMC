from typing import Protocol, List, Dict, Any
from pathlib import Path
import csv
import threading
from datetime import datetime


class DataAccess(Protocol):
    def append(self, record: Dict[str, Any]) -> None:
        ...

    def read_last(self, n: int) -> List[Dict[str, Any]]:
        ...


class CSVDataAccess:
    def __init__(self, filepath: str, fieldnames: List[str]):
        self.filepath = Path(filepath)
        self.fieldnames = fieldnames
        self.lock = threading.Lock()
        # Ensure file exists with header
        if not self.filepath.exists():
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with self.filepath.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def append(self, record: Dict[str, Any]) -> None:
        # append a row as CSV safely
        with self.lock:
            with self.filepath.open("a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow({k: record.get(k, "") for k in self.fieldnames})

    def read_last(self, n: int) -> List[Dict[str, Any]]:
        # Read last n records efficiently
        if not self.filepath.exists():
            return []
        with self.lock:
            with self.filepath.open("r", newline="") as f:
                reader = list(csv.DictReader(f))
                # Return last n, newest last -> we want newest first
                return list(reversed(reader))[:n]


# Simple factory for CSV storage used in this project
def make_csv_accessor(dataset_name: str, fieldnames: List[str]) -> CSVDataAccess:
    base = Path(__file__).parents[1] / "datasets"
    base.mkdir(parents=True, exist_ok=True)
    filepath = base / f"{dataset_name}.csv"
    return CSVDataAccess(str(filepath), fieldnames)
