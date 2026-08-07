**What this changes**

**Why**

**Checks**
- [ ] `bash -n setup.sh run.sh scripts/*.sh` passes
- [ ] `python3 -m json.tool` passes on both `config/*.example.json`
- [ ] `git ls-files | grep -Ev '\.example\.' | grep -E 'profile|answers|queue|applications/|logs/|screenshots/|state/'` prints nothing
- [ ] No new runtime dependencies
- [ ] Does not help the agent fabricate, bypass a CAPTCHA, or fake human behavior
