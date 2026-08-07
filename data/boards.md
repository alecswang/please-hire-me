# Live ATS boards

Every org slug this project has ever touched, re-probed against the ATS APIs on **2026-08-06**.
A board appears here only if it returned at least one posting that day. This exists to save
you the slug-guessing game described in `data/ats-field-notes.md`, and to give a new install
somewhere concrete to start sourcing.

Regenerate with `./scripts/probe_boards.sh`. Boards die and come back, so re-probe rather than
trusting this file forever. Requests are paced on purpose: live orgs return unparseable bodies
under rate limiting and read as dead.

```bash
curl -s "https://api.ashbyhq.com/posting-api/job-board/<slug>?includeCompensation=true"
curl -s "https://boards-api.greenhouse.io/v1/boards/<slug>/jobs"
curl -s "https://api.lever.co/v0/postings/<slug>?mode=json"
```

`jobs` is every posting on the board. `US` counts postings whose location string looks United
States based. `band` means at least one posting publishes a compensation range in the API,
which tells you whether a comp filter will work without reading body text.

## Ashby (135 live boards)

| slug | jobs | US | band |
|---|---:|---:|:--:|
| `openai` | 745 | 594 | yes |
| `harvey` | 364 | 262 | yes |
| `crusoe` | 358 | 349 | yes |
| `legora` | 279 | 123 | yes |
| `sierra` | 192 | 115 | yes |
| `clickhouse` | 167 | 56 |  |
| `cohere` | 142 | 41 | yes |
| `decagon` | 123 | 91 | yes |
| `ramp` | 122 | 110 | yes |
| `notion` | 119 | 73 |  |
| `skydio` | 115 | 100 |  |
| `etched` | 109 | 99 | yes |
| `plaid` | 107 | 99 | yes |
| `langchain` | 101 | 71 |  |
| `replit` | 88 | 78 | yes |
| `profound` | 85 | 82 | yes |
| `cognition` | 83 | 39 | yes |
| `mercor` | 78 | 70 | yes |
| `synthesia` | 72 | 23 |  |
| `commure` | 69 | 56 | yes |
| `polymarket` | 65 | 65 | yes |
| `baseten` | 65 | 65 | yes |
| `suno` | 64 | 34 | yes |
| `reflectionai` | 62 | 53 |  |
| `supabase` | 57 | 46 |  |
| `voleon` | 56 | 47 | yes |
| `temporal` | 54 | 44 |  |
| `coderabbit` | 53 | 33 | yes |
| `lumaai` | 49 | 39 | yes |
| `matx` | 44 | 0 |  |
| `speak` | 43 | 28 | yes |
| `attio` | 42 | 18 | yes |
| `exa` | 41 | 35 | yes |
| `n8n` | 41 | 9 | yes |
| `factory` | 41 | 40 |  |
| `basis-ai` | 37 | 37 | yes |
| `kalshi` | 36 | 36 | yes |
| `sardine` | 36 | 11 | yes |
| `thinkingmachines` | 35 | 35 |  |
| `cartesia` | 34 | 29 | yes |
| `render` | 33 | 33 | yes |
| `gamma` | 33 | 33 |  |
| `encord` | 33 | 16 | yes |
| `modal` | 31 | 27 | yes |
| `fal-ai` | 31 | 31 | yes |
| `livekit` | 31 | 26 | yes |
| `vapi` | 31 | 30 | yes |
| `surge-ai` | 30 | 30 |  |
| `hex` | 29 | 29 |  |
| `physicalintelligence` | 29 | 27 |  |
| `reducto` | 29 | 29 | yes |
| `listenlabs` | 28 | 28 | yes |
| `sesame` | 27 | 24 | yes |
| `linear` | 26 | 0 |  |
| `distyl` | 24 | 22 |  |
| `omni` | 23 | 16 | yes |
| `periodic-labs` | 23 | 23 |  |
| `dust` | 23 | 9 | yes |
| `parallel` | 22 | 22 | yes |
| `openrouter` | 21 | 21 | yes |
| `runpod` | 21 | 21 |  |
| `numeric` | 21 | 20 | yes |
| `ambiencehealthcare` | 20 | 20 |  |
| `middesk` | 20 | 20 | yes |
| `midjourney` | 20 | 20 |  |
| `normalcomputing` | 20 | 16 | yes |
| `persona` | 19 | 19 | yes |
| `latent` | 19 | 19 | yes |
| `tavily` | 18 | 7 | yes |
| `semgrep` | 17 | 16 |  |
| `firecrawl` | 17 | 17 | yes |
| `tavus` | 16 | 16 |  |
| `chalk` | 15 | 3 | yes |
| `warp` | 15 | 15 | yes |
| `bland` | 14 | 14 | yes |
| `chaidiscovery` | 14 | 14 |  |
| `hyperbolic` | 14 | 14 |  |
| `character` | 13 | 13 | yes |
| `cobot` | 12 | 4 |  |
| `pylon` | 12 | 12 | yes |
| `resend` | 12 | 12 |  |
| `gumloop` | 12 | 12 | yes |
| `sieve` | 11 | 10 | yes |
| `latentlabs` | 11 | 5 |  |
| `terminal` | 11 | 0 | yes |
| `nabla` | 11 | 4 | yes |
| `mirage` | 10 | 10 | yes |
| `elicit` | 10 | 10 |  |
| `pika` | 10 | 10 | yes |
| `openart` | 9 | 9 | yes |
| `thebotcompany` | 9 | 9 | yes |
| `irregular` | 9 | 0 |  |
| `tempo` | 9 | 8 | yes |
| `extropic` | 8 | 8 | yes |
| `pinecone` | 8 | 8 | yes |
| `sphinx` | 8 | 8 | yes |
| `harmonic` | 8 | 7 | yes |
| `opusclip` | 8 | 8 | yes |
| `railway` | 8 | 2 |  |
| `browserbase` | 7 | 7 | yes |
| `ideogram` | 7 | 2 |  |
| `ollama` | 7 | 7 |  |
| `graphite` | 7 | 7 |  |
| `parasail` | 7 | 1 | yes |
| `openevidence` | 7 | 4 |  |
| `reka` | 7 | 7 |  |
| `unify` | 7 | 7 | yes |
| `motherduck` | 7 | 6 | yes |
| `substrate` | 7 | 7 |  |
| `sfcompute` | 7 | 7 | yes |
| `arcade` | 6 | 6 |  |
| `neon` | 6 | 4 | yes |
| `unstructured` | 6 | 6 | yes |
| `paradigm` | 6 | 6 | yes |
| `phonic` | 6 | 6 |  |
| `stytch` | 5 | 5 | yes |
| `turbopuffer` | 5 | 5 |  |
| `rime` | 4 | 4 |  |
| `anterior` | 4 | 4 | yes |
| `credal` | 4 | 4 | yes |
| `runway` | 4 | 0 |  |
| `greptile` | 4 | 4 | yes |
| `julius` | 4 | 4 | yes |
| `context` | 4 | 4 |  |
| `cluely` | 4 | 4 | yes |
| `letta` | 4 | 4 |  |
| `anon` | 3 | 3 |  |
| `kernel` | 3 | 0 | yes |
| `axiom` | 3 | 3 | yes |
| `weaviate` | 3 | 0 |  |
| `mem0` | 3 | 3 | yes |
| `clarify` | 2 | 2 |  |
| `axiommath` | 1 | 0 |  |
| `vellum` | 1 | 1 |  |
| `inngest` | 1 | 1 |  |

## Greenhouse (100 live boards)

| slug | jobs | US |
|---|---:|---:|
| `speechify` | 1302 | 618 |
| `databricks` | 815 | 395 |
| `stripe` | 551 | 259 |
| `datadog` | 440 | 224 |
| `anthropic` | 390 | 316 |
| `nebius` | 357 | 201 |
| `brex` | 304 | 243 |
| `cloudflare` | 297 | 9 |
| `samsara` | 289 | 260 |
| `coreweave` | 287 | 252 |
| `point72` | 230 | 102 |
| `roblox` | 222 | 194 |
| `scaleai` | 215 | 137 |
| `xai` | 201 | 118 |
| `airbnb` | 191 | 108 |
| `gitlab` | 190 | 170 |
| `optiverus` | 176 | 69 |
| `coinbase` | 170 | 155 |
| `clickhouse` | 167 | 148 |
| `vast` | 166 | 166 |
| `drweng` | 161 | 76 |
| `robinhood` | 134 | 107 |
| `ripple` | 128 | 94 |
| `figureai` | 127 | 107 |
| `intercom` | 121 | 38 |
| `jumptrading` | 105 | 43 |
| `gleanwork` | 104 | 75 |
| `worldquant` | 101 | 10 |
| `cresta` | 99 | 85 |
| `apptronik` | 83 | 82 |
| `vercel` | 80 | 68 |
| `neuralink` | 79 | 79 |
| `chainguard` | 74 | 74 |
| `towerresearchcapital` | 72 | 21 |
| `sigmacomputing` | 70 | 65 |
| `psiquantum` | 69 | 61 |
| `togetherai` | 59 | 48 |
| `parloa` | 59 | 25 |
| `agilityrobotics` | 57 | 45 |
| `mercury` | 56 | 56 |
| `dvtrading` | 56 | 26 |
| `schonfeld` | 53 | 26 |
| `discord` | 48 | 48 |
| `virtu` | 46 | 22 |
| `matx` | 44 | 44 |
| `snorkelai` | 43 | 42 |
| `flowtraders` | 42 | 11 |
| `airtable` | 40 | 37 |
| `oldmissioncapital` | 34 | 29 |
| `akunacapital` | 33 | 30 |
| `eve` | 31 | 31 |
| `goodfire` | 30 | 29 |
| `kalshi` | 27 | 27 |
| `applovin` | 24 | 18 |
| `turing` | 24 | 14 |
| `heygen` | 21 | 21 |
| `axiom` | 20 | 15 |
| `alloy` | 19 | 18 |
| `figure` | 19 | 14 |
| `transmarketgroup` | 17 | 17 |
| `find` | 16 | 1 |
| `tavily` | 15 | 12 |
| `eclipsetrading` | 15 | 2 |
| `polyai` | 15 | 11 |
| `parallel` | 13 | 13 |
| `genevatrading` | 13 | 10 |
| `blackforestlabs` | 13 | 3 |
| `speechmatics` | 12 | 1 |
| `brave` | 12 | 7 |
| `foundry` | 12 | 6 |
| `stackblitz` | 11 | 11 |
| `maventrading` | 11 | 3 |
| `vaticlabs` | 11 | 5 |
| `galileo` | 10 | 10 |
| `descript` | 10 | 10 |
| `pdtpartners` | 10 | 9 |
| `gsacapital` | 10 | 2 |
| `planetscale` | 9 | 9 |
| `assemblyai` | 9 | 8 |
| `inceptive` | 9 | 8 |
| `engineersgate` | 8 | 3 |
| `labelbox` | 8 | 8 |
| `worldlabs` | 7 | 7 |
| `ctccampusboard` | 6 | 4 |
| `instabase` | 5 | 4 |
| `udio` | 5 | 5 |
| `invisible` | 5 | 1 |
| `humeai` | 5 | 5 |
| `stabilityai` | 5 | 5 |
| `harmonic` | 5 | 5 |
| `warp` | 4 | 4 |
| `quadraturecapital` | 4 | 1 |
| `profound` | 2 | 2 |
| `cline` | 2 | 2 |
| `imbue` | 2 | 2 |
| `exoduspoint` | 2 | 0 |
| `coactive` | 1 | 1 |
| `marshallwace` | 1 | 0 |
| `paradigm` | 1 | 1 |
| `tempo` | 1 | 1 |

## Not listed

A slug missing from this file was dead, renamed, or never on that ATS on the probe date.
Before writing one off, try the variants in `data/ats-field-notes.md`: `fal` against
`fal-ai`, `sierra` against `sierraai`, Greenhouse against Ashby for the same company.
