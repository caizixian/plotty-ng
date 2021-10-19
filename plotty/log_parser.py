from pathlib import Path
from typing import Any, List, Optional
import pandas as pd
import enum
import gzip
import uuid
import re

# The four regular expressions below are borrowed from https://github.com/jamesbornholt/plotty
# MIT License Copyright (c) 2021 James Bornholt
TIMEDRUN = re.compile(r"mkdir.*timedrun")
DaCapo_ERROR = re.compile(r'NullPointerException|JikesRVM: WARNING: Virtual processor has ignored timer interrupt|hardware trap|-- Stack --|code: -1|OutOfMemory|ArrayIndexOutOfBoundsException|FileNotFoundException|FAILED warmup|Validation FAILED|caught alarm')
DaCapo_STARTING = re.compile(r"=====(==|) .* (S|s)tarting")
DaCapo_PASSED = re.compile(r"PASSED in (\d+) msec")
DaCapo_WARMUP = re.compile(r"completed warmup \d* *in (\d+) msec")
DaCapo_LATENCY = re.compile(r"DaCapo (\w*) *tail latency: 50% (\d+) usec, 90% (\d+) usec, 99% (\d+) usec, 99.9% (\d+) usec, 99.99% (\d+) usec, max (\d+) usec")
MMTk_HEADER = "============================ MMTk Statistics Totals ============================"
TABULATE_HEADER = "============================ Tabulate Statistics ============================"


class ParsingMode(enum.Enum):
    NON_STATS = 1
    MMTk_STATS_COLUMN_NAMES = 2
    TABULATE_STATS_COLUMN_NAMES = 3
    MMTk_STATS_VALUES = 4
    TABULATE_STATS_VALUES = 5
    ERROR = 6


def check_invocation_start(line: str) -> bool:
    return TIMEDRUN.match(line) is not None


def check_iteration_start(line: str) -> bool:
    return DaCapo_STARTING.match(line) is not None


def check_mmtk_start(line: str) -> bool:
    return line.strip() == MMTk_HEADER


def check_tabulate_start(line: str) -> bool:
    return line.strip() == TABULATE_HEADER


def check_error(line: str) -> bool:
    return DaCapo_ERROR.search(line) is not None


def parse_dacapo_iteration(line: str) -> Optional[int]:
    m = DaCapo_PASSED.search(line)
    if m:
        return float(m.group(1))
    m = DaCapo_WARMUP.search(line)
    if m:
        return float(m.group(1))
    return None


def parse_dacapo_latency(line: str) -> Optional[List[int]]:
    m = DaCapo_LATENCY.search(line)
    if m:
        latencies = dict(
            p50=float(m.group(2)),
            p90=float(m.group(3)),
            p99=float(m.group(4)),
            p999=float(m.group(5)),
            p9999=float(m.group(6)),
            pmax=float(m.group(7))
        )
        latency_suffix = m.group(1)
        if latency_suffix:
            latencies = {k+".{}".format(latency_suffix): v for k, v in latencies.items()}
        return latencies
    else:
        return None


def parse_lines(lines: List[str]):
    # Parse one file
    # Each file contains multiple invocations
    # And each invocation contains multiple iterations (warmup and timing iteration)
    invocation = -1
    iteration = 0
    state = ParsingMode.NON_STATS
    current_iteration = None
    rows = []
    column_names = None
    for line in lines:
        if check_invocation_start(line):
            invocation += 1
            iteration = 0
            state = ParsingMode.NON_STATS
            continue
        if line.startswith("="):
            # possibly special line
            if check_iteration_start(line):
                # append the data for the previous iteration
                if current_iteration is not None:
                    rows.append(current_iteration)
                iteration += 1
                current_iteration = {
                    "invocation": invocation,
                    "iteration": iteration,
                }
                state = ParsingMode.NON_STATS
            if state is ParsingMode.ERROR:
                continue
            if check_mmtk_start(line):
                state = ParsingMode.MMTk_STATS_COLUMN_NAMES
            elif check_tabulate_start(line):
                state = ParsingMode.TABULATE_STATS_COLUMN_NAMES
            else:
                bmtime = parse_dacapo_iteration(line)
                if bmtime is not None:
                    current_iteration["bmtime"] = bmtime
                    continue
                latency = parse_dacapo_latency(line)
                if latency is not None and current_iteration is not None:
                    current_iteration.update(latency)
                    continue
                if check_error(line):
                    state = ParsingMode.ERROR
        else:
            if state is ParsingMode.ERROR:
                continue
            if state is ParsingMode.MMTk_STATS_COLUMN_NAMES:
                column_names = line.strip().split("\t")
                state = ParsingMode.MMTk_STATS_VALUES
            elif state is ParsingMode.TABULATE_STATS_COLUMN_NAMES:
                column_names = line.strip().split("\t")
                state = ParsingMode.TABULATE_STATS_VALUES
            elif state is ParsingMode.MMTk_STATS_VALUES:
                values = map(float, line.strip().split("\t"))
                if current_iteration is not None:
                    current_iteration.update(dict(zip(column_names, values)))
                column_names = None
                state = ParsingMode.NON_STATS
            elif state is ParsingMode.TABULATE_STATS_VALUES:
                values = map(float, line.strip().split("\t"))
                if current_iteration is not None:
                    current_iteration.update(dict(zip(column_names, values)))
                column_names = None
                state = ParsingMode.NON_STATS
     # append the data for the last iteration
    if current_iteration is not None:
        rows.append(current_iteration)
    return rows


def process_one_file(path: Path):
    with gzip.open(path, "rt") as fd:
        return parse_lines(fd.readlines())


def parse_folder(path: Path):
    scenarios = []
    results = []
    for p in path.glob("*.log.gz"):
        suffixes = p.name.split(".")
        scenario = {}
        uid = str(uuid.uuid4())
        scenario["_id"] = uid
        scenario["benchmark"] = suffixes[0]
        scenario["hfac"] = int(suffixes[1])
        scenario["heap"] = int(suffixes[2])
        buildstring = ".".join(suffixes[3:-2])
        scenario["buildstring"] = buildstring
        scenario["build"] = suffixes[3]
        for modifier in suffixes[4:-2]:
            parts = modifier.split("-")
            if len(parts) == 1:
                scenario[parts[0]] = True
            else:
                scenario[parts[0]] = "-".join(parts[1:])
        lst_stats = process_one_file(p)
        for stat in lst_stats:
            stat["scenario"] = uid
        results.extend(lst_stats)
        scenarios.append(scenario)
    return pd.DataFrame(scenarios), pd.DataFrame(results)
