## github actions + pages demo

- setup:

- get creds [here](https://gspread.readthedocs.io/en/latest/oauth2.html)
  - pop private key
  - add to secrets as `GSPREAD_PRIVATE_KEY`
- make a spreadsheet
  - share it with email from creds
- get github token [here](https://github.com/settings/tokens)
  - add to secrets as `GH_TOKEN`
- modify repo name in workflow
- setup github pages in settings to track master/docs
- to make it all work locally, setup the env vars with the dotenv package
