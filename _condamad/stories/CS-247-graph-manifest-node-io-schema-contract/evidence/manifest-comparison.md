# Manifest comparison evidence

Self-comparison classification: compatible.

Deltas: 0.

## Review-fix optional dependency comparison

The implementation review found that `optional_depends_on` was persisted in the manifest but was not part of
`compare_graph_manifests`.

Resolution:

- added `node_optional_input_added` as a compatible comparison delta;
- added `node_optional_input_removed` as a breaking comparison delta;
- added unit coverage proving both optional dependency delta classes.

Validation:

- `pytest -q tests\unit\domain\astrology\test_calculation_graph_manifest.py
  tests\unit\domain\astrology\test_natal_calculation_graph_manifest.py
  tests\architecture\test_api_contract_neutrality.py`: PASS, 21 passed.
- `pytest -q tests`: PASS, 896 passed, 201 deselected.

## Review-fix requiredness descriptor comparison

The final brief-alignment pass found that `GraphTypeDescriptor.required` was persisted in manifest evidence but was not
part of `compare_graph_manifests`.

Resolution:

- added `required_input_requiredness_changed` as a breaking comparison delta;
- added `node_input_requiredness_changed` as a breaking comparison delta;
- added `node_output_requiredness_changed` as a breaking comparison delta;
- added unit coverage proving descriptor requiredness delta classes.

Validation:

- `pytest -q tests\unit\domain\astrology\test_calculation_graph_manifest.py
  tests\unit\domain\astrology\test_natal_calculation_graph_manifest.py
  tests\architecture\test_api_contract_neutrality.py`: PASS, 22 passed.
- `pytest -q tests`: PASS, 897 passed, 201 deselected.
