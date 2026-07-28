import csv
import io
from typing import List, Any


class ExportService:
    @staticmethod
    def generate_csv(headers: List[str], rows: List[List[Any]]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
        return output.getvalue()
