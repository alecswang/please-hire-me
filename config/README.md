# config/

Everything the agent reads before it touches a form. No logs, no data here.

| File | What | Tracked? |
|---|---|---|
| `settings.json` | Run knobs and target criteria. The launcher turns it into the run's instructions. | no (yours) |
| `profile.json` | Every field value an ATS asks for. Used verbatim, never guessed. | no (yours) |
| `answers.md` | Free-text templates, fact sheet, preset legal/EEO answers. The only source for prose. | no (yours) |
| `spec.md` | The run contract: hard rules, per-application procedure, log format. | yes |
| `*.example.*` | Templates `setup.sh` copies from. Edit these when you add a new field. | yes |

Add a fact once here and the agent stops asking you about it forever.
