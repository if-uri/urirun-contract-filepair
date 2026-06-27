# urirun-contract-filepair

**Format `urirun-contract-*`: README opisuje intencję, lokalny LLM proponuje kontrakt,
generator deterministycznie robi kod, bramy egzekwują — CI tylko weryfikuje.**

## Co ten projekt robi (źródło intencji dla LLM)

Odwracalna **para plikowa między procesami** (analogiczna do `windowpair`, ale dla plików):

- `file/command/snapshot-delete` — **command, odwracalne**. Robi snapshot pliku (ścieżka,
  zawartość base64, sha256), zwraca go jako `snapshot`, potem usuwa plik. Zwraca też `inverse`
  wskazujący `file/command/restore` z tym snapshotem jako argumentem.
- `file/command/restore` — **command, odwracalne**, inverse dla `snapshot-delete`. Przyjmuje
  `snapshot`, odtwarza plik z jego bajtów.

Snapshot z `snapshot-delete` jest **kompletnym** wejściem `restore` (pełny handoff). Proces A może
usunąć plik, a proces B — czytając tylko JSON snapshotu — go odtworzyć. Łączy ich wyłącznie kontrakt.

Błędy: `file-missing`, `snapshot-path-missing`.

## Pipeline

```
README.md ──(lokalny LLM)──▶ contracts.json ──(generator det.)──▶ src/handlers_generated.py
   intencja      proponuje, recenzja+commit     kształt prawdy        sygnatura + koperta (nie edytuj)
                                                                              ▼ człowiek/LLM pisze CIAŁO
                                                                       src/handlers.py → enforce + conform
```

```bash
make gen        # contracts.json → src/handlers_generated.py
make check      # conform (efekt, wzajemny inverse, przykłady, inverse-args) + anty-dryf — bez LLM
```

## Wariant wielopakietowy (dwa procesy, transport)

```bash
PORT=8801 python packages/producer/service.py &     # file/command/snapshot-delete
PORT=8802 python packages/consumer/service.py &      # file/command/restore
python orchestrator/drive.py                          # producer ─HTTP→ consumer, full handoff, exit 0/1
```

Konsument odrzuca każdy payload niezgodny z `restore.inp` (snapshot=string → 422; brak `path` →
422 + `remediation: snapshot-path-missing`). Oba procesy ładują TEN SAM `contracts.json` niezależnie.

## Licencja

Apache-2.0 · Tom Sapletta · https://tom.sapletta.com
