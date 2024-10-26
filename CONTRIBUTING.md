
# Contributing to Kiota Java

Kiota Python is a mono-repo containing source code for the following packages:

- 'microsoft-kiota-abstractions'
- 'microsoft-kiota-authentication-azure'
- 'microsoft-kiota-http'
- 'microsoft-kiota-serialization-form'
- 'microsoft-kiota-serialization-json'
- 'microsoft-kiota-serialization-text'
- 'microsoft-kiota-serialization-multipart'

Kiota Python is open to contributions. There are a couple of different recommended paths to get contributions into the released version of this library.

__NOTE__ A signed a contribution license agreement is required for all contributions, and is checked automatically on new pull requests. Please read and sign [the agreement](https://cla.microsoft.com/) before starting any work for this repository.

## File issues

The best way to get started with a contribution is to start a dialog with the owners of this repository. Sometimes features will be under development or out of scope for this SDK and it's best to check before starting work on contribution. Discussions on bugs and potential fixes could point you to the write change to make.

## Submit pull requests for bug fixes and features

Feel free to submit a pull request with a linked issue against the __main__ branch.  The main branch will be updated frequently.

## Commit message format

To support our automated release process, pull requests are required to follow the [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/)
format.
Each commit message consists of a __header__, an optional __body__ and an optional __footer__. The header is the first line of the commit and
MUST have a __type__ (see below for a list of types) and a __description__. An optional __scope__ can be added to the header to give extra context.

```
<type>[optional scope]: <short description>
<BLANK LINE>
<optional body>
<BLANK LINE>
<optional footer(s)>
```

The recommended commit types used are:

- __feat__ for feature updates (increments the _minor_ version)
- __fix__ for bug fixes (increments the _patch_ version)
- __perf__ for performance related changes e.g. optimizing an algorithm
- __refactor__ for code refactoring changes
- __test__ for test suite updates e.g. adding a test or fixing a test
- __style__ for changes that don't affect the meaning of code. e.g. formatting changes
- __docs__ for documentation updates e.g. ReadMe update or code documentation updates
- __build__ for build system changes (gradle updates, external dependency updates)
- __ci__ for CI configuration file changes e.g. updating a pipeline
- __chore__ for miscallaneous non-sdk changesin the repo e.g. removing an unused file

Adding a an exclamation mark after the commit type (`feat!`) or footer with the prefix __BREAKING CHANGE:__ will cause an increment of the _major_ version.

## Working with source locally

To support the mono-repo structure and release processes, the individual projects leverage [poetry](https://python-poetry.org/) for package management.

Therefore, to validate,lint and manage packages, you would need to install poetry for easier management of the source.

```shell
python -m pip install --upgrade poetry
```

### Running validations in individual projects

To install dependencies, run the command below in the directory of the project you are working on.

```shell
poetry install
```

To fix the code format to align to linting rules setup using `yapf`, run the command below in the directory of the project you are working on.

```shell
poetry run yapf -ir {projectName}
```

To check the code format to align to linting rules setup using `yapf`, run the command below in the directory of the project you are working on.

```shell
poetry run yapf -dr {projectName}
```

To lint the code using `pylint`, run the command below in the directory of the project you are working on.

```shell
poetry run pylint {projectName} --disable=W --rcfile=.pylintrc
```

To run the tests using `pytest`, run the command below in the directory of the project you are working on.

```shell
poetry run pylint pytest
```

To run type checking using `mypy` , run the command below in the directory of the project you are working on.

```shell
poetry run mypy {projectName}
```

### Running validations across all projects

To help with validation of validations across all projects, you can leverage the [powershell script](./kiota-python.ps1) at the root of repository. The script will handle the above scenarios by changing directories and running the relevant command across all the projects in the mono repo.

To install dependencies across all projects, run the following in a powershell shell from the repository root.

```shell
.\kiota-python.ps1 install-deps
```

To fix the code format to align to linting rules setup using `yapf` across all projects, run the following in a powershell shell from the repository root.

```shell
.\kiota-python.ps1 format
```

To check the code format to align to linting rules setup using `yapf` across all projects, run the following in a powershell shell from the repository root.

```shell
.\kiota-python.ps1 check-format
```

To lint the code using `pylint` across all projects, run the following in a powershell shell from the repository root.

```shell
.\kiota-python.ps1 lint
```

To run the tests using `pytest` across all projects, run the following in a powershell shell from the repository root.

```shell
.\kiota-python.ps1 test
```

To run type checking using `mypy` across all projects, run the following in a powershell shell from the repository root.

```shell
.\kiota-python.ps1 check-types
```

__TIP__ Running `.\kiota-python.ps1 test` should give a hint of all available commands you can pass to the script to run across projects which can be configured this in [this file](./projects-config.json).
