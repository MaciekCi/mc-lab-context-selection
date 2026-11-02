#!/usr/bin/env python3
"""Offline synthetic evidence-packet builder. No API calls or credentials."""
import argparse,json
from pathlib import Path
import context_data as data
import context_engine as engine

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--case',default='R-867')
p.add_argument('--strategy',choices=['whole','search','linked'],default='linked')
p.add_argument('--output',type=Path)
a=p.parse_args()
corpora,tasks=data.build();task=next((t for t in tasks if t['id']==a.case),None)
if task is None:p.error('Unknown case; examples: R-867, B-867, I-867')
context,ids=engine.select(corpora[task['family']],task['question'],a.strategy)
print(json.dumps({'classification':'synthetic demonstration','api_calls':0,'question':task['question'],'strategy':a.strategy,'source_ids':ids,'context_bytes':len(context.encode())},indent=2))
if a.output:a.output.write_text(engine.prompt(task['question'],context)+'\n')
