# PIKE-O

PIKE-O is an OpenEvolve-based PyTorch optimization system that fits into the [PIKE](https://github.com/pike-project/pike) framework.

Modifications have been made to the OpenEvolve parallel processing system to enable an error-fixing agent, and to conform to the desired PIKE output directory structure.

## About

This is a public fork of [OpenEvolve](https://github.com/algorithmicsuperintelligence/openevolve), licensed under the Apache License 2.0.
Some modifications have been made by Kirill Nagaitsev in 2025.

## Running with PIKE

See [PIKE](https://github.com/pike-project/pike) for details on how to run the system.

## Important Notes

The KernelBench example can be found in `examples/kernelbench`

The mutation-only prompt template is located in `examples/kernelbench/templates_mutation`, and no inspiration/elite solutions are included in this prompt, regardless of other parameter choices in `config.yaml`. To use crossover-based prompts, switch the `template_dir` parameter to `examples/kernelbench/templates_crossover`

Error fixing can be enabled by setting `max_fix_attempts > 0` in `config.yaml`
