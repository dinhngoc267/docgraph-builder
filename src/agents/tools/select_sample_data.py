import os
import glob
import random

from typing import Union

from pydantic_ai import RunContext

from src.models import  MyDeps

def select_sample_data(data_dir:str, limit_length:int=10000):
    file_patterns = ['*.txt']

    for pattern in file_patterns:
        files = glob.glob(os.path.join(data_dir, pattern))
        if files:
            chosen_file = random.choice(files)

            with open(chosen_file, "r") as f:
                data = f.read()

            return data[:limit_length]

    return None

async def retrieve_data(ctx: RunContext[MyDeps]) -> str:

    return select_sample_data(data_dir=ctx.deps.data_dir, limit_length=ctx.deps.sample_data_length)