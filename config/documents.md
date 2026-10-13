# Cover Letters and Tailored Resumes

Two per-application documents, each behind a toggle in `config/settings.json` → `documents`. Both
default to on. A missing key counts as on.

| Key | Default | Effect |
|---|---|---|
| `documents.cover_letter` | `true` | Draft a cover letter when the form has a field for one. |
| `documents.tailor_resume` | `true` | Upload a LaTeX resume rewritten for this posting from true facts only. |
| `documents.resume_max_pages` | `1` | Page limit the tailored PDF must fit. |
| `documents.cover_letter_min_words` / `_max_words` | `150` / `250` | Length window the linter enforces. |

Both build with tectonic (LaTeX) and read PDFs back with poppler: `brew install tectonic poppler`.
Setup installs them. Without them the agent uploads the default resume and pastes letters as text.

Every file lands in `applications/files/<company>-<role>/` under the user's real name, because the
recruiter sees the filename: `Firstname-Lastname-Resume.pdf`, `Firstname-Lastname-Cover-Letter.pdf`,
plus the sources `cover-letter.md`, `resume.tex`, and `posting.txt`. The folder is gitignored with the rest of
`applications/`.

Both documents follow the same law as every other answer: **only facts from `config/answers.md`,
`config/profile.json`, and the base resume.** The posting tells you what to emphasize. It never
supplies a fact about the user.

## Cover letter

### Why these rules
- **Tailoring works, but echoing the posting no longer does.**
  - In a 2019 field test of 7,287 applications, a tailored letter got 53% more callbacks than
    no letter, while a generic one added little
    ([ResumeGo](https://www.resumego.net/research/cover-letters/)). That was before AI.
  - Once Freelancer.com shipped a one-click AI letter tool, how closely a letter matched the
    posting's words lost about half its link to callbacks and nearly 80% of its link to offers.
    Employers moved to signals they could verify, like work history
    ([Cui et al. 2025](https://arxiv.org/abs/2509.25054)).
  - A second study found the hiring premium for customized applications vanished after LLMs
    ([Galdin & Silbert 2025](https://arxiv.org/abs/2511.08785)).
  - So keyword overlap with the posting is now table stakes. What still separates a letter is
    what an LLM can't produce from the posting alone: a detail about the company that took real
    reading to find, a story only this person has, and work a reader can check.
- **Recruiters spot generated letters** by missing personalization (61%), flat tone (60%), and
  generic phrasing (57%). 54% are less likely to move forward on unedited AI text
  ([Jobseeker](https://www.jobseeker.com/en/resume/articles/2025-hr-trends-hiring-statistics)).
  A letter that doesn't sound like the person who shows up to the interview is a red flag.
- **Don't repeat the resume.** The letter's job is the case for why this person would excel, told
  with something the resume doesn't contain
  ([Ask a Manager](https://askamanager.org/2010/10/2-reasons-your-cover-letter-sucks.html)).
- **Short.** 82% of HR readers want one page or less, and 40% want under half a page (ResumeLab
  survey). Half a page is about 250 words.

### Shape: 150-250 words, three paragraphs
- **Greeting:** "Dear [Company] hiring team," or the hiring manager's name when the posting gives
  it. Never "To whom it may concern".
- **Opening (2-3 sentences): who is writing, which role, and the real reason.** Plain is right:
  "I study [major] at [school] and I'm applying for the [role] role." Then one
  specific thing about this company that you found by reading beyond the posting, on its
  engineering blog, a launch post, docs, or a changelog. Say it the way a person would ("I read
  your post on X, and it's close to what I worked on at Y"). Don't stage it as a clever framed
  observation. A paraphrase of the job description doesn't count. If you find nothing specific,
  skip it rather than fake it.
- **Story (3-5 sentences): one piece of work, told through the part the resume can't show.** Take
  it from the "Stories" section of `config/answers.md`: why the user took it on, the hard part,
  or a decision they made. Use at most two numbers, and only ones that carry the point.
  Restating resume bullets wastes the paragraph.
- **Close (1-2 sentences):** availability from `eligibility.earliest_start`, said plainly. Add what
  the user would want to work on only if their own words in `answers.md` say it. Don't circle back
  to the opening line.
- **Proof link (optional):** one link to work a reader can check, such as a repo, paper, or demo
  from the profile, placed where the story mentions that work.
- **Sign-off:** the user's name alone. No "Sincerely".

### Voice
Follow the user's tone rules and the "Writing style" section of `config/answers.md`. When
`answers.md` has a "Voice sample", match its sentence length, word choice and formality.
- First person and conversational, in plain declarative sentences. Contractions are fine.
- No em dashes, and no dash used as punctuation.
- Never string nouns together as a list; write sentences with real verbs.
- Vary sentence length. At most one three-part list. Fewer than half the sentences start with "I".
- Banned outright (the linter holds the full list): passionate, leverage, delve, cutting-edge,
  excited to, I believe, thrilled, deeply, world-class, synergy, I am writing to, eager,
  I am confident, perfect fit, ideal candidate, align with, resonate, thrive, dynamic,
  fast-paced, honed, spearheaded, testament, navigate, landscape, realm, foster, robust,
  seamless, innovative, proven track record, results-driven, detail-oriented, furthermore,
  moreover, additionally, journey, elevate, empower, showcase, pivotal, at the intersection of,
  skill set.

### Sounding like a person, not a model
A letter can pass every rule above and still read as generated. These are the structural signs
readers recognize, taken from Wikipedia's catalog of AI writing
([Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)) and from
reviewing this repo's own drafts:
- **No wrap-up lines.** Let a paragraph end on a fact, not on a short sentence that sums it up
  ("That taught me what breaks...", "That's the work I do best").
- **No callback ending.** The last paragraph doesn't loop back to the opening image.
- **No mirrored phrasing:** "both halves of X", "agents that write fixes and harnesses that
  measure them", "not just X but Y", "X rather than Y", "it's not X, it's Y".
- **No significance padding:** "highlighting...", "reflecting...", "ensuring...", "serves as",
  "stands as", "underscores".
- **Uneven is fine.** Paragraphs can differ in length, and so can sentences. A plain sentence
  like "Three pilot customers pay for it now." is better than a clever one.
- **Use the user's own words.** When `answers.md` has a passage the user wrote (Stories, Voice
  sample, or any answer in their words), reuse its phrases nearly verbatim. That is the only
  reliable source of a human voice. Polished text the agent wrote itself is the giveaway.
- **Say less.** If a sentence exists only to connect two other sentences, cut it.

### Facts: every claim has a source
- **Every sentence that says something about the user must trace to a line in the fact sheet, the
  Stories section, a template, or the resume.** That covers opinions, motives and lessons as
  well as numbers. "Most of my time went into the review loop" is a fabrication unless the user
  said it. The linter only catches numbers, so this check is yours. Write the claim-to-source
  list into the per-application doc.
- Every number must already be in the sources. The linter fails on any that isn't.
- Client and contract work stays "a contract project for X", never "at X".
- The company detail is quoted in the per-application doc with its URL. Never invent a product, a
  post, a value, or a mission line. Never claim the user used the product or met the team unless
  the fact sheet says so.
- Dates and availability come from `eligibility` and `profile.json`, never from memory.

### The three tests
1. **Read-aloud test:** read it as the user would say it to a recruiter on the phone. Any sentence
   they would never say out loud gets rewritten in their words or cut.
2. **Swap test:** replace the company name with a competitor's. If the letter still reads as true,
   the hook is generic. Rewrite it.
3. **Resume test:** cover the resume. Does the letter tell the reader something new about this
   person? If every sentence is a resume bullet in prose, rewrite the story paragraph.

### When to draft
Draft only when the form has a place for a letter:
- a field labeled cover letter, as a text box or file upload, required or optional;
- or a posting that asks for one and gives no dedicated field, but has an "Additional
  information" box.

No field means no letter, and you don't draft one to keep on file. Check this once the form is
open. Fill the form's other fields first, then draft the letter.

### Procedure
1. Read the posting and note its top two or three requirements. Then spend a few minutes on the
   company's own site for the hook detail. Record the URL and the sentence you used.
2. Pick the story from `answers.md` that best answers the requirements. Draft to
   `applications/files/<slug>/cover-letter.md`.
3. `python3 scripts/app_docs.py lint-letter <that file> --company "<Company>" --jd <posting.txt>`.
   It fails on:
   - length;
   - dashes;
   - banned phrases;
   - placeholders;
   - unsourced numbers;
   - a missing company name;
   - a "To whom it may concern" opener.

   It warns on:
   - sentences that restate resume bullets;
   - sentences that paraphrase the posting;
   - uniform sentence and paragraph length;
   - wrap-up lines that end a paragraph, and mirrored "not X but Y" phrasing;
   - too many sentences starting with "I".

   Fix every FAIL and treat every WARN as an edit. Rerun until OK.
4. Run all three tests. Check every claim against its source.
5. Put it in the field it was drafted for:
   - Text box: paste the text, with a blank line between paragraphs.
   - File input: `python3 scripts/app_docs.py render-letter <md> <dir>/Firstname-Lastname-Cover-Letter.pdf`,
     then `file_upload` it.
   - "Additional information" box: only when the posting asks for a letter and has no field.
6. A question labeled "cover letter" that asks something specific ("Why Acme? 100 words") is a
   free-text question. Answer it under the normal 40-80 word rule.
7. **A form or posting that says not to use AI** gets no drafted letter. Leave the field for the
   user and log NEEDS HUMAN.
8. Put the final text, the hook's URL, and the claim-to-source list in the per-application doc.

## Tailored resume

### Why these rules
Recruiters search the ATS with the posting's own words, and a human reader skims, often only the
first one or two bullets under each role. So the resume that gets read puts the user's most
relevant true work first, says it in the posting's vocabulary, and proves it with numbers. Every
career guide that covers tailoring draws the same line: reword and reorder real experience, never
add to it. A requirement the user does not meet stays unmet on the page.

### Format (one template, one toolchain)
- **LaTeX, built with tectonic.** The base is `profile.json` → `resume_tailor_base`, default
  `data/resume.tex`, made at setup from `data/resume.example.tex`: Jake's Resume, the most used
  software resume template on Overleaf, adapted so its text layer parses cleanly. A user who
  already keeps their own `.tex` points `resume_tailor_base` at it and their build command at
  `resume_build_cmd` (placeholders `{src}` `{dir}` `{out}`).
- **ATS-safe by construction:** one column, standard section names (Education, Experience,
  Projects, Skills), real text with no icons or images, dates as `Mon YYYY -- Mon YYYY`, no ligature
  glyphs in the text layer.
- **One page** (`documents.resume_max_pages`). The layout in the preamble is fixed after setup.
  When a tailored copy overflows, cut a bullet. Never shrink fonts, margins or spacing.

### What makes a bullet good
- **Result first, XYZ shape:** what changed, measured how, by doing what. "Cut [metric] from
  [before] to [after] by building [thing] on [tool]."
- **Start with a strong past-tense verb** (present tense only for a current role). Never "Responsible
  for", "Helped", "Worked on", "Utilized". No "I", "my", "we".
- **A number in every bullet the facts allow.** The number must already be in the base resume or the
  fact sheet. Pulling a true number from the fact sheet into a bullet that lacked one is the best
  edit there is ("after [N] customer interviews", with N copied from the fact sheet). Inventing, rounding up, or estimating one is
  fabrication.
- **One to two lines.** A bullet whose last line holds one or two words wastes a line: trim it.
- **The posting's spelling for the same thing:** if the posting says "PostgreSQL" and the resume
  says "Postgres", use "PostgreSQL". Only for something the user actually has.
- Order inside a role: the bullet that best answers the posting's top requirement first.

### Allowed edits
- Reorder bullets, entries within a section, and the skills inside each skills line.
- Rewrite a bullet into the shape above, using only facts from the base resume and the fact sheet.
  Two bullets from the same role may merge when the fact sheet ties the facts together.
- Add a true number or detail from the fact sheet to an existing bullet.
- Cut bullets, entries, activities, or skills that do nothing for this posting, to fit the page.
- Move Projects above Experience when the projects answer the posting better.

### Never
- Add a skill, tool, language, title, employer, date, metric, or claim that is in neither the
  base resume nor the fact sheet, even when the posting asks for it.
- Change a heading line: name, contact line, employer, title, location, dates, section names.
  "Co-founder" is not "CTO", "Intern" is not "Engineer".
- Touch the preamble.
- Keyword-stuff: list a posting term the user cannot discuss in an interview.

### Procedure
1. Save the posting text to `applications/files/<slug>/posting.txt`.
2. `python3 scripts/app_docs.py keywords <posting.txt>`. It sorts the posting's terms into three
   groups: on the resume (move them up, match the spelling), in the fact sheet only (may be
   added), gaps (never claim; a gap in a hard requirement can make the role a skip).
3. Copy the base to `applications/files/<slug>/resume.tex` and edit the copy. The base is never
   edited during a run. If the base is missing, skip tailoring, upload `profile.json` → `resume`,
   and say once in the run summary that no tailoring base exists.
4. `python3 scripts/app_docs.py check-resume <copy> --jd <posting.txt>`. It fails on:
   - any number not in the sources;
   - any capitalized, technical, or posting-derived term not in the sources;
   - a changed heading line or preamble;
   - unescaped `% & # _ $`;
   - first person or banned words.

   It warns on bullets with no number, weak openers, and bullets over two lines. Fix every FAIL.
   Treat each WARN as an edit to make when the facts allow it. Rerun until OK.
5. `python3 scripts/app_docs.py render-resume <copy> <dir>/Firstname-Lastname-Resume.pdf`. It
   fails on:
   - a build error;
   - text running past the margin;
   - more pages than allowed;
   - a bullet missing or garbled in the PDF text (the usual sign of a bad escape);
   - ligature glyphs.

   It warns on widow lines and a page under 80% full. Fix and rebuild until OK.
6. Look at the PDF once (the Read tool renders it) before uploading. A script cannot see a
   cramped section or an orphaned heading at the bottom of the page.
7. Upload it with `file_upload` in place of the default resume. If the form autofills from the
   resume, read every field back as usual.
8. In the per-application doc, under "Resume used", give the PDF path and one line per change.

### Setup: turning a PDF resume into the base
Most users have only a PDF. At setup:
1. Copy `data/resume.example.tex` to `data/resume.tex` and transcribe the PDF into it **word for
   word**. Keep the user's wording, numbers, section names and order. Escape `% & # _ $`. Write
   ranges as `--`.
2. `python3 scripts/app_docs.py verify-conversion <original.pdf> data/resume.tex`. It builds the
   LaTeX, compares every word against the original, and fails on any word missing or added, and on
   page overflow. Fix and rerun until OK.
3. If it overflows one page, first match the original's structure (one-line activity bullets
   instead of full entries), then drop the document class from `11pt` to `10pt`. Never cut the
   user's content to make the base fit; that is a choice for tailoring, per job.
4. Run `render-resume` on the base and show the PDF to the user beside their original.
5. Bullets in the base with no number go into the setup question list: "These bullets have no
   number. If you know a real one, tell me; skipping leaves them as they are." Their answers go
   into the fact sheet, never straight into the base.

## When a toggle is off
- `cover_letter: false`: draft nothing. Leave an optional cover-letter field blank. A required one
  is NEEDS HUMAN.
- `tailor_resume: false`: upload `profile.json` → `resume` unchanged.
