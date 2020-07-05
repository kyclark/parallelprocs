"""
Purpose: Run commands with (GNU) parallel
Author:  Ken Youens-Clark <kyclark@gmail.com>
"""

import os
import sys
import tempfile
import subprocess
from shutil import which
from typing import List, Optional


# --------------------------------------------------
def run(commands: List[str],
        msg: str = 'Running job',
        parallel: Optional[str] = which('parallel'),
        num_procs: int = 2,
        verbose: bool = False,
        halt: int = 0):
    """
Run commands in parallel

Required:

- commands (List[str]): commands

Keyword options:

- msg (str): message to print if verbose
- parallel (str): path to "parallel", default "which('parallel')"
- num_procs (int): num of concurrent processes, default "0" to use all CPUs
- verbose (bool): print messages to sys.stderr, default "False"
- halt (int): number of failed jobs to trigger halt, default "0" for no halt

Returns:

- True or False depending on success

May raise exceptions, so run with try/except.
    """

    if isinstance(commands, str):
        commands = [commands]

    if not commands:
        return False

    def tell(s):
        if verbose:
            print(s, file=sys.stderr)

    tell(f'{msg} (# jobs = {len(commands)}, # parallel = {num_procs})')

    if parallel and os.path.isfile(parallel):
        # Run in parallel if possible
        job_file = tempfile.NamedTemporaryFile(delete=False, mode='wt')
        job_file.write('\n'.join(commands))
        job_file.close()

        cmd = 'parallel {} {} < {}'.format(
            '-j {}'.format(num_procs) if num_procs else '',
            '--halt soon,fail={}'.format(halt) if halt else '', job_file.name)

        try:
            out = subprocess.run(cmd,
                                 shell=True,
                                 check=True,
                                 capture_output=True,
                                 text=True)
            if out.stdout:
                tell(out.stdout)
            if out.stderr:
                tell(out.stderr)

        except subprocess.CalledProcessError as err:
            stderr = err.stderr + '\n' if err.stderr else ''
            stdout = err.stdout + '\n' if err.stdout else ''
            raise Exception('Error: {}{}'.format(stdout, stderr))

        finally:
            os.remove(job_file.name)
    else:
        # Maybe parallel isn't installed, so run serially
        for cmd in commands:
            rv, output = subprocess.getstatusoutput(cmd)
            if rv != 0:
                raise Exception(f'Failed to run: {cmd}\nError: {output}')

    return True
