from dataclasses import dataclass


@dataclass
class MyDeps:
    data_dir: str
    sample_data_length: int = 10000