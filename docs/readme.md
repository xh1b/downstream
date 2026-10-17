# Software documentation

<!-- @ref:docs-index; @tag:documentation -->
<!-- @link:repository-overview; @link:documentation-workflow; @link:reference-token-contract. -->

The [code](../src/downstream) and [admitted data](../params) define what
Downstream computes. The [methods paper](../paper/downstream.tex) explains the
mathematics, scientific choices and limitations. These guides explain how to
run, change and integrate the software. If prose and implementation disagree,
check the code and its tests, then correct the explanation.

| Guide | Use it to |
| --- | --- |
| [Model card](model_card.md) | Decide which outputs and populations the implementation supports. |
| [Integration](integration.md) | Supply scenarios, interpret results, scale or mix outputs, and preserve provenance. |
| [Evidence and data](evidence.md) | Maintain source records, import baselines and check evidence admission. |
| [Calculator](calculator.md) | Run the browser app, understand its code boundaries and verify a change. |
| [Development](development.md) | Use the task system, run tools/tests, inspect CI, build the paper and qualify a release. |

Start with the [root README](../README.md) for installation and CLI examples.
For an equation or the reason behind a modeling choice, follow the paper refs
in source comments or use the [paper-to-code map](development.md#paper-and-implementation).
The rendered paper is available as [PDF](../paper/downstream.pdf) and
[HTML](methods.html). Edit generated output through its source and builder.

## Supporting material

[Audits](audits/readme.md) contain reviews, diagnostics and qualification
receipts. They record what was checked at a particular time; their historical
numbers and conclusions are not the current API documentation.
[Research and design material](research/readme.md) contains plans, literature
background and the extraction register. A proposed design is not implemented
behavior. Work status, decisions and new verification receipts belong on the
[task board](../tasks/README.md).

## Maintaining this structure

Use lowercase filenames for Markdown throughout `docs/`, including audit,
research and index files. Extend one of the five guides before adding another
top-level document. Keep
software instructions here, explanations of the mathematics in the paper,
reviews in `audits/`, and supporting research/design material in `research/`.
An audit needs a clear scope, date and evidence; it does not need the same
editorial treatment as a maintained guide. Record actionable follow-up in tasks.

Use ordinary relative Markdown links for browsing and stable repository tokens
for relationships. Define a ref once at the passage or implementation it names;
preserve it when moving that content. Code can cite the paper for rationale and
a software guide for its calling contract. Tests link to the implementation
and contract they verify. See the [token contract](../tasks/README.md#reference-tokens)
and [development checks](development.md#documentation-and-reference-checks).
Run `make check-docs` before review to check live navigation, executable examples
and generated references; this target runs in CI.
