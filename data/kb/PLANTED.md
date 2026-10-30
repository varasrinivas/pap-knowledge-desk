# Planted defects in the knowledge base (for the profiler and the knowledge-fix loop to find)

These are deliberate. Do not "fix" them in the source documents: the course measures that the system finds them.

| ID | Kind | Where | What | How the system should find it |
|---|---|---|---|---|
| GAP-1 | Missing topic | none (UI-04 and POL-15 stop short) | Adding a second servicing provider to an existing request: there is no screen. The real fix, known only from past incidents, is to **Withdraw** and resubmit with the servicing provider as the primary, or to ask Service Desk to add it (subcategory `how_to`) | About 4% of the history: incidents resolved by explaining a workaround, with no document above the coverage gate. They form the gap cluster |
| GAP-2 | Missing topic | none | The "Peer-to-peer requested" banner on the Decision tab means the *reviewer* asked for a peer-to-peer with the ordering provider; the office must call the scheduling line within 2 business days or the case is decided on the record | About 3% of the history: gap cluster |
| GAP-3 | Missing topic | none (WF-12 mentions fax only in passing) | Fax-to-portal intake matching: faxed requests appear as **Draft** under the office's worklist within 4 hours, tagged `FAX`. The office must open the draft and press **Submit**, otherwise nothing is reviewed | About 3% of the history: gap cluster (also the live P1 outage, so a fax question has both a live and a gap answer) |
| STALE-1 | Stale fact | UI-05 (Adding attachments) | Says the size limit is **20 MB**. The current limit is **25 MB** (CANON, POL-09) | Past incidents closed with "limit is 25 MB" contradict the document. The knowledge-fix loop flags the contradiction and proposes the correction |

Topics the documents *do* cover, where incidents are **user education** (the answer existed and was not found or followed): the attachment limit, the MFA-reset sign-in, lapsed delegation (Submit button gone), pend-code meanings, the appeal deadline, how routing picks the region, the Documents-tab delay, and the report export format.
