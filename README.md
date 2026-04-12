# team-project-robustness

Repository of All code for the Team Project about LLM Roleplaying Robustness

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
ruff lint
```

If you're working with VS-Code, you can add the official Ruff extension as well as the following code to your `.vscode/settings.json` file, to make sure the project-wide configurations are followed.

```json
{
  "ruff.configurationPreference": "filesystemFirst",
}
```
