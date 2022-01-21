# V2DL3 - VERITAS (VEGAS and Eventdisplay) to DL3 Converter.

Provide a tool to convert VERITAS data products to DL3 FITS format, allowing to use e.g. the [gammapy science tools](https://gammapy.org/) for analysis. 

The converter can be used to convert point-like and full-enclosure IRFs. 
The FITS output follows format as defined in [open gamma-ray astro data formats repository](https://github.com/open-gamma-ray-astro/gamma-astro-data-formats).

The projects tries to share as many tools as possible between VEGAS and Eventdisplay, especially those used for writing the FITS files.

Contact:
	Ralph Bird (ralph.bird.1@gmail.com)
	Tarek Hassan (tarek.hassan@desy.de)
	Tony Lin (xyxlin@gmail.com)
	Tobias Kleiner (tobias.kleiner@desy.de)
    Sonal Patel (sonal.patel@desy.de)
    Gernot Maier (gernot.maier@desy.de)
        


---
# The DL3 converter v2dl3

v2dl3 is the main tool to be used for converting IRFs.

## Using V2DL3 with VEGAS

* vegas version >= 2.5.7
* requirements are listed in the ```environment.yml``` file.

### Installation

Use the [conda package manage](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) to install the dependenies:
```
conda env create -f environment.yml
```
The environment ```v2dl3``` will be created and can be activated with:

```
conda activate v2dl3
```

Install now pyV2DL3:
```
pip install . --use-feature=in-tree-build
```

### Usage of commandline tool v2dl3 with VEGAS

Run `v2dl3 --help` to see all options.

Make sure you have ROOT with pyROOT enabled and VEGAS(>=v2.5.7) installed to proceed.
Now, lets create the DL3 fits files from the stage 5 files in the ```./VEGAS/``` folder. 

##### One file at a time

To convert a single stage 5 file to DL3 fits you need to provide the path to the stage 5 file as well as the corresponding effective area file using the flag ```-f```. The last argument is the name of the ouput DL3 file.

```
v2dl3 -f ./VEGAS/54809.med.ED.050.St5_Stereo.root ./VEGAS/EA_na21stan_medPoint_050_ED_GRISU.root ./test.fits
```

##### Generate from a VEGAS stage6 runlist

You can also provide a stage6 runlist to the command line tool. In this case the last argument is the folder where all the output DL3 files will be saved. Beware that the file names for the outputs are inferred from the root file name (xxx.root -> xxx.fits)

```
v2dl3 -l ./runlist.txt  ./test
```

---

## EventDisplay

- use Eventdisplay version >= 486

### Installation

Use the [conda package manage](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) to install the dependenies:
```
conda env create -f environment-eventdisplay.yml
```
The environment ```v2dl3ED``` will be created and can be activated with:

```
conda activate v2dl3ED
```

Note that no pip is required for using the v2dl3 tool with Eventdisplay.

### Usage of commandline tool v2dl3

Run `python pyV2DL3/script/v2dl3_for_Eventdisplay.py --help` to see all options.

Convert an anasum output file to DL3.
The following input is required:
- anasum file for a given run
- effective area file for the corresponding cut applied during the preparation of the anasum file (DL3 version)

Example for point-like analysis:
```
python pyV2DL3/script/v2dl3_for_Eventdisplay.py -f 54809.anasum.root [Effective Area File] ./outputdir/54809.anasum.fits
```
Example for full-enclosure analysis:
```
python pyV2DL3/script/v2dl3_for_Eventdisplay.py --full-enclosure -f 64080.anasum.root [Effective Area File] ./outputdir/64080.anasum.fits
```

---
**TEXT BELOW REQUIRES REVIEW**

##### Multi file processing

To convert many runs at once with different Effective Area files there is a modified anasum script here ( ``` VERITAS-Observatory/Eventdisplay_AnalysisScripts_VTS/scripts/ANALYSIS.anasum_parallel_from_runlist_v2dl3.sh ``` ), that can be used to create a ``` v2dl3_for_runlist_from_ED485-anasum.sh ``` script. This script then contains one line for each processed file in the formatting as shown above in the full-enclosure case. 
Then in your bash run 
```
./v2dl3_for_runlist_from_ED485-anasum.sh
```
to create the fits files one after another. 

Alternatively, you can submit one job for each entry of this script using
```bash
v2dl3_qsub --v2dl3_script <script>
```
where `<script>` is the script that was written out by `ANALYSIS.anasum_parallel_from_runlist_v2dl3.sh`.
`v2dl3_qsub` has the following options:
 - `--conda_env` name of the conda environment. Default is `v2dl3` 
 - `--conda_exe` path to the conda executable. Only needed if `$CONDA_EXE` is not set.
 - `--rootsys` path to rootsys. Only needed if `$ROOTSYS` is not set
 - `--add_option` allows to add further options to v2dl3. (e.g. `--add_option '--evt_filter /path/to/file.yaml'`)

#### Filter events
Using --evt_filter option, you can filter which events are written to the fits file. The argument takes the path of a 
yaml file that stores conditions. E.g. to select only events between 0.5 and 1.0 TeV:
```yaml
Energy: [0.5, 1.0]
```

---
### Git pushing
If two people have used the same notebook at the same time it gets a bit nasty with a merge due to differences in outputs and cell run counts.  To overcome this I have followed the instructions in http://timstaley.co.uk/posts/making-git-and-jupyter-notebooks-play-nice/

Specifically, this requires that you have jq (https://stedolan.github.io/jq/) which should be easy enough to install, I get it through brew on my mac (I'm not sure what happens if you don't have jq installed - maybe you will find out!).

The following files have been edited to allow for this (in this repository directory, if you want you can set some of this up globally).

.git/config
```
[core]
attributesfile = .gitattributes

[filter "nbstrip_full"]
clean = "jq --indent 1 \
        '(.cells[] | select(has(\"outputs\")) | .outputs) = []  \
        | (.cells[] | select(has(\"execution_count\")) | .execution_count) = null  \
        | .metadata = {\"language_info\": {\"name\": \"python\", \"pygments_lexer\": \"ipython3\"}} \
        | .cells[].metadata = {} \
        '"
smudge = cat
required = true
```

.gitattributes
```
*.ipynb filter=nbstrip_full
```
