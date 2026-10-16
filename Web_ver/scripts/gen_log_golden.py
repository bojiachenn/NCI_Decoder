"""Generate golden outputs for log-file mode (Decoder.py mode_1).

Runs the *real* Decoder.mode_1() (input() / clear_terminal monkeypatched) inside a
temporary working directory, so NCI_output/<file>_d.txt is written there and never
into the Python repo. The log is copied into that temp dir under its own name and
typed as a relative path, so the "File Path:" header is just the file name.

Before each run the decoder modules' scalar globals (HDLL_CMD, PWR_MODE_00, ...)
are reset to their import-time values (same as gen_golden.py), matching the JS port
where every log file gets a fresh decoder context.

Output: tests/log_golden/golden.json = [{name, log, decodeKey, filter, input, output}]

Usage:  python scripts/gen_log_golden.py
"""
import builtins
import contextlib
import json
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True  # keep the Python repo untouched

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.normpath(os.path.join(HERE, "..", "tests", "log_golden"))

sys.path.insert(0, HERE)
import gen_golden  # noqa: E402  (sets up sys.path for the Python repo, imports ctrl modules)

sys.path.insert(0, gen_golden.REPO)
import Decoder  # noqa: E402

RAW_LOG = os.path.join(LOG_DIR, "raw_log.txt")  # copy of the NXP sample log (was ../NCI_ref/raw_log.txt)
NXP_LOG = os.path.join(LOG_DIR, "nxp_sample.log")
ST_LOG = os.path.join(LOG_DIR, "st_sample.log")

# name, log file, config vendor (= decode key + decoder vendor), config filter
CASES = [
    ("raw_log_nxp_filtered", RAW_LOG, "Nxp", "nxpncir nxpncix"),
    ("raw_log_nxp_all", RAW_LOG, "Nxp", "remain_all"),
    ("raw_log_st_all", RAW_LOG, "st", "remain_all"),
    ("nxp_sample_all", NXP_LOG, "Nxp", "remain_all"),
    ("nxp_sample_filtered", NXP_LOG, "Nxp", "NFC ERROR enabling"),
    ("st_sample_all", ST_LOG, "st", "remain_all"),
    ("st_sample_filtered", ST_LOG, "ST", "stnfchal watchdog"),
]


def run_mode_1(log_path, vendor, filt):
    name = os.path.basename(log_path)
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copyfile(log_path, os.path.join(tmp, name))
        answers = iter([name, "-1"])
        old_cwd, old_input, old_clear = os.getcwd(), builtins.input, Decoder.clear_terminal
        os.chdir(tmp)
        builtins.input = lambda *a: next(answers)
        Decoder.clear_terminal = lambda: None
        Decoder.config = {"vendor": vendor, "chip_model": "None", "filter": filt}
        try:
            with open(os.devnull, "w") as devnull, contextlib.redirect_stdout(devnull):
                Decoder.mode_1()
        finally:
            os.chdir(old_cwd)
            builtins.input = old_input
            Decoder.clear_terminal = old_clear
        # mode_1 writes the output as UTF-8 ('\r\n' on Windows; read() normalises it)
        with open(os.path.join(tmp, "NCI_output", name + "_d.txt"), encoding="utf-8") as f:
            return f.read()


def main():
    snap = gen_golden._snapshot()
    golden = []
    for case_name, log_path, vendor, filt in CASES:
        gen_golden._restore(snap)
        with open(log_path, encoding="utf8", errors="ignore", newline="") as f:
            text = f.read()
        output = run_mode_1(log_path, vendor, filt)
        golden.append({"name": case_name, "log": os.path.basename(log_path), "decodeKey": vendor,
                       "filter": filt, "input": text, "output": output})
    path = os.path.join(LOG_DIR, "golden.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(golden, f, ensure_ascii=False, indent=1)
    print(f"{path}: {len(golden)} cases")


if __name__ == "__main__":
    main()
