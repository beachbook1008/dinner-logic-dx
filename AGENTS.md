# AGENTS

## Project overview
- This is a small Streamlit app in `dinner_planner.py` that reads `dinner_list.csv` and uses Gemini via Google Generative AI.
- The app loads `GEMINI_API_KEY` from a local `.env` file using `dotenv.load_dotenv()`.
- `.env` is intentionally excluded in `.gitignore`; do not add secrets or API keys to version control.

## Key guidance for AI coding agents
- Preserve or use environment-based configuration for sensitive values.
- If modifying API access or keys, keep the pattern: `load_dotenv()` + `os.getenv("GEMINI_API_KEY")`.
- When troubleshooting `.env` behavior, check that `.gitignore` excludes `.env` and that the code is reading `GEMINI_API_KEY` correctly.
- Avoid hardcoding credentials or writing `.env` contents into the repository.

## Relevant files
- `dinner_planner.py` - main app logic
- `dinner_list.csv` - menu / calorie source data
- `.env` - local secret configuration file
- `.gitignore` - ensures `.env` is ignored

## Notes
- There is no existing package manifest, so dependency changes should be minimal and based on the current imports.
- Keep changes simple and aligned with the current Streamlit app structure.
