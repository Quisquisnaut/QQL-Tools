# Compatibility reporting

QQL-Tools will eventually need to describe compatibility more precisely than a binary supported/unsupported flag.

## Report shape

Future compatibility reports should be able to say:

| External feature | QQL capability | Result | Notes |
| --- | --- | --- | --- |
| Course title | metadata | Exact | Stored directly |
| Lesson hierarchy | Lesson/Round | Mapped | Structural alignment required |
| Multiple choice | Select | Exact | |
| Gap exercise | Select/Input/... | Mapped | Depends on semantics |
| Timed response | unavailable | Unsupported | Timing behavior lost |

## Result categories

Use the following categories:

- **Exact**
- **Mapped**
- **Approximated**
- **Preserved but unused**
- **Unsupported**
- **Rejected**

A compatibility result should be able to record **information loss** explicitly instead of silently dropping unsupported behavior.

## Current project state

This repository does **not** claim compatibility with any specific external platform yet. The implemented Python types merely provide a place to represent compatibility decisions once a real external format has been analyzed.
