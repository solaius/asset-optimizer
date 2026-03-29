---
name: run-experiment
description: Start an optimization experiment from the CLI
---

Guide the user through running an optimization:
1. Which asset file to optimize
2. Which evaluation to use (list available, or create new)
3. Which provider to use
4. Max iterations and convergence strategy

Then construct and run the CLI command:
```bash
asset-optimizer optimize <file> --evaluation <eval> --provider <provider> --iterations <N>
```
