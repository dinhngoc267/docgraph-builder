import os
import glob
import random

from pydantic_ai import RunContext

from src.models import  Dependency

def select_sample_data(data_dir:str, limit_length:int=10000):

    files = glob.glob(f"/home/ju/PycharmProjects/automated-docgraph-construction/data/cord-19/articles/*.txt")
    if files:
        chosen_file = random.choice(files)

        with open(chosen_file, "r") as f:
            data = f.read()

        return data[:limit_length]

    return None

async def retrieve_data(ctx: RunContext[Dependency]) -> str:

    return select_sample_data(data_dir=ctx.deps.data_dir, limit_length=ctx.deps.sample_data_length)