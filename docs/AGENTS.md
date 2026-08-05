# AGENTS.md — docs/

This directory holds the agent-facing documentation for the `thunderball` BOND
film package (mission codename DISCO VOLANTE).

Every document here is a hard constraint, not a suggestion. Read them in this
order:

1. `agent_instructions.md` — the read-first protocol, the eight hard rules, the
   pitfalls that have actually bitten in this package, and the verification
   checklist you must run before claiming a change is done.
2. `architecture.md` — the layer contract and a module-by-module inventory of
   what each file in `src/thunderball/` computes, including which four names in
   `mission.py` are frozen because the fleet consumes them.
3. `testing_philosophy.md` — read this *before* writing a test, not after. It
   documents a real shipped defect that a full green suite failed to catch, and
   the six rules that follow from it.

## Rules for this directory itself

- **Never hand-author a metric here.** Test counts and coverage percentages
  live in `_generated/COUNTS.md` and are regenerated from a measured run. Prose
  elsewhere should describe the *gate* ("line+branch coverage of `src/` at or
  above 90%"), not quote a figure that will go stale.
- **Name modules individually.** A doc that says "the domain modules" without
  naming them cannot be checked against the tree and rots invisibly.
- **Keep these files true after a code change.** A wrong docstring or a stale
  module list is a defect in this package's terms, and doc drift is one of the
  things a review pass is specifically looking for.
- **No exemplar boilerplate.** Everything here describes *this* package. If a
  sentence would read identically in a sibling film package, it is not earning
  its place.
