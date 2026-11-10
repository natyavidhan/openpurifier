# Contributing to OpenPurifier

Thanks for wanting to help. This is a small hardware project, so the most valuable contributions
are often not code at all.

## Ways to help

- **Build one and report back.** Open an issue titled `Build report: <your filter> + <your fan>` with
  your printer, material, what fit, what didn't, and a photo if you can. Real-world fit data is what
  the project needs most.
- **Measure the unverified dimensions.** The table under *Measure before you print* in the README
  lists values that came from listing photos rather than datasheets. Calipers and a photo are
  enough.
- **Fit other parts.** Different fans and filters mostly mean different values in
  `cad/src/lib/params.py`. If you get one working, a PR with a new parameter set is great.
- **Firmware.** Particle-sensor auto mode, better filter-life logic, other boards.
- **Docs and translations.**

## Changing the CAD

1. Change dimensions in `cad/src/lib/params.py`, not in the part files, unless you're changing a
   part's shape.
2. Rebuild and run the checks from `cad/`:

   ```bash
   cad run src/assembly.py
   PYTHONPATH=src cad run checks/check_fit.py
   PYTHONPATH=src cad run checks/check_fit.py basic
   PYTHONPATH=src cad run checks/check_tray.py
   ```

   `check_fit` should report no interferences.
3. Re-export the STLs you changed into `print/smart/` and/or `print/basic/` with
   `src/print_parts.py`. Keep the file names and numbering.
4. If the outside of the purifier changed, regenerate the renders (see *Changing the design* in the
   README).

## Pull requests

- One change per PR, with a short description of what and why.
- Say whether you've printed it. "Untested, CAD only" is fine; just say so.
- Anything touching the mains wiring needs a clear explanation and will get a careful review.

## Safety

Don't submit changes that remove the fuse, the cable gland, the box lids or the separation between
the mains and low-voltage sides.
