# team-project-robustness

Repository of all code for the Team Project about LLM Roleplaying Robustness

## Steps to run the pipeline

### Setup Python Environment and Install Dependencies

```shell
pip install -r requirements.txt
```

### Ensure Environment Variables

Create a `code/.env` file that corresponds with `code/.env.example`

### Run files in order

```shell
# Step 1: Pull Ollama Models
python pipeline/pull_ollama_models.py

# Step 2: Setup Pipeline
python pipeline/start_pipeline_afresh.py

# Step 3: Generate Characters
python code/character_generation.py

# Step 4: Generate Persona Prompt Bundles (currently only JSON Prompts are saved)
python code/persona_prompt_bundle_generation.py

# Step 5: Generate Attack Prompt Bundles, in batches
python code/attack_prompt_bundle_generation.py # Multiple times if needed

# Step 6: Generate Transcripts, in batches
python code/transcript_generation.py # Multiple times if needed
# To generate the transcripts that didn't get generated the first time around, run this (can be repeated as often as wanted)
python code/backup_transcript_generation.py # Multiple times if needed

# Step 7: Evaluate Transcripts
# Running a complete evaluation: rerunning the file below until we get output: Merged partial evaluation results into one file and Reset checkpoint
# Need to run 5 complete evaluations to average out test results
python code/evaluation.py

# Step 8: Build Evaluation Dashboard
python code/combine_results.py
python code/build_dashboard.py
python code/imbalance_sensitivity_dashboard.py # Optional
```

### Analysing Results

The pipeline generates two dashboards for easy analysis of the experiment results. To explore them, open the following files in any browser.

`outputs/testscore_dashboard.html` provides detailed graphs and diagrams allowing for analysing the experiment results, along with instructions on interpreting them. 
`outputs/imbalance_sensitivity_dashboard.html` provides additional insights on the differences between unweighted and macro-averaged results, taking into consideration the uneven distribution of trait values when randomly generating characters.

## Working with submodules

To add a local repository of yours to the project, first clone this repository locally. Then, run the command:

```bash
git add submodule GITHUB_HTTP_PATH_TO_YOUR_REPO
```

Commit and Push your changes to upload the submodule to the parent repository.

When pulling or cloning the parent repository, the external submodule will be empty locally. Run the following command:

```bash
git submodule init
```

to register the submodule for your local path, and:

```bash
git submodule update
```

to download the files from the submodule.

When committing within the submodule, you need to **commit twice**. Once within the sub-repository, and once in the parent-repository to make sure your changes are properly documented.

For additional queries, you can check out the documentation on submodules [here](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

## Working with Ruff for Linting and Formatting

First, download the Ruff python package:

```bash
pip install ruff
```

The configuration is stored in `pyproject.toml`. Note the configuration assumed Python 3.13.

To format and lint all files in the `/code` folder, run the following code before committing:

```bash
ruff format
ruff check --fix
```

If you're working with VS-Code, you can add the official Ruff extension as well as the following code to your `.vscode/settings.json` file, to make sure the project-wide configurations are followed.

```json
{
  "ruff.configurationPreference": "filesystemFirst",
}
```

## Additional results

The `/report` folder contains high-resolution copies of all diagrams and graphs included in our final report, including the main experiment results and secondary study results.
