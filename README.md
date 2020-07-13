# snapshots

snapshots includes a single deployed AWS Lambda function that grabs a random photo from specified Google Drive folder and sends it to a specified Facebook chat at a scheduled time (E.g. my function runs every day at 9:30 AM) . Here's how you can replicate my process. 

## Installation

Install [pipenv](https://pipenv.pypa.io/en/latest/). 
```bash
brew install pipenv
```
Spawn a shell with virtualenv activated. 
```bash
pipenv shell
```
Install dependencies located in Pipfile. `--dev` installs development packages in addition to project dependencies (black, flake8)

```bash
pipenv install --dev
```
## Deployment
