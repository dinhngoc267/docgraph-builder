from dataclasses import dataclass

@dataclass
class Dependency:
    data_dir: str = None
    sample_data_length: int = 10000