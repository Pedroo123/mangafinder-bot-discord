# Agent Instructions for MangaFinder Bot Discord

## Core Principles

### Filesystem, file modification, data loss
* Read Before Writing: Always load and analyze the current contents of a file before modifying it, unless you are certain it's a new or empty file. Never assume a file is empty.
* Use Targeted Operations: Prefer methods that modify specific parts of a file (e.g., append, insert lines, search and replace specific patterns) over whole-file overwrites.
* Scope Replacements Carefully: When using search and replace, ensure the pattern is not overly broad. Preview the changes if possible (e.g., using diff or a dry-run mode).
* Preserve Existing Content: When adding new code or sections, make sure to merge with existing content, not replace it entirely.
* Use git operations to inspect the state of certain files.

### Breaking Debugging Loops
1.  **Recognize the Loop:** Acknowledge that the current approach is not working.
2.  **Halt and Re-evaluate:** Stop trying to make small tweaks to the last failed attempt.
3.  **Failure Counter:** If you've tried to fix the same function/test 3 times with similar logic and failed, you MUST pivot.
4.  **Pivot Strategies:**
    *   **Re-read Documentation:** Go back to the project's documentation, or any relevant library documentation, to ensure you haven't misunderstood something fundamental.
    *   **Deeper Error Analysis:** Don't just look at the error message. Explain *why* your change caused that specific test failure. Write down the hypothesis.
    *   **Revisit Root Cause:** Go back to the original bug report and your initial analysis.
    *   **Simplify:** Can you create a smaller, minimal test case to isolate the issue?
    *   **Google Search:** Use the web search tool to search for common errors or issues.
    *   **Reset:** Consider reverting the changes to a clean state and starting the fix approach from scratch.
    *   **Seek Help:** Use `knowledgebase_lookup` with specific error messages or concepts.

### General Framework: Working with Python Projects
* **`python -m pytest` over `pytest`** - The `-m` flag adds the current directory to `sys.path`, fixing most import errors.
* **Install from manifest, not error messages** - When you see `ModuleNotFoundError`, don't `pip install <that-package>`. Install the *entire* project deps from the manifest file.
* **Patch where it's looked up, not where it's defined** - If `api.py` does `from utils import helper`, patch `api.helper`, not `utils.helper`.
* **AsyncMock for async functions** - `MagicMock` is not awaitable. Use `AsyncMock` for any `async def` function.

## Project-Specific Instructions

### Backend Implementation
* The bot is being ported from TypeScript to Python.
* Use `asyncpraw` for Reddit API interaction and `discord.py` for the Discord bot.
* Port logic from `src/service/reddit.service.ts` to `src/reddit_service.py`.

### Security
* Security is a top concern.
* Never hardcode credentials. Use environment variables (via `python-dotenv`).
* Ensure the Docker container runs as a non-root user.

### UI/UX
* Responses should be formatted as Discord Embeds.
* Embeds must include: Title, Date, Front Page (thumbnail/image), and a Link for redirect.

### Deployment
* Target platform: Azure (Container Apps).
* Use a minimal and secure base image (e.g., `python:3.8-slim`).
* Include a `Dockerfile` and `.dockerignore`.
