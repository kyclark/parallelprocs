"""Run commands with (GNU) parallel"""

import os
import sys
import tempfile
import subprocess
from shutil import which


# --------------------------------------------------
def run(commands,
        msg='Running job',
        parallel=which('parallel'),
        num_procs=0,
        verbose=False,
        halt=0):
    """
Run commands in parallel

Required:

- commands (list(str)): commands

Keyword options:

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

    tell('{} (# jobs = {}, # parallel = {})'.format(msg, len(commands), num_procs))

    if parallel and os.path.isfile(parallel):
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
        for cmd in commands:
            rv, out = subprocess.getstatusoutput(cmd)
            if rv != 0:
                raise Exception('Failed to run: {}\nError: {}'.format(
                    cmd, out))

    return True
