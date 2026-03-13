# Stratified Sampler

A Python tool for drawing reproducible, stratified random samples from news article datasets. Samples equally across political bias categories and presidential administration time periods. Configured via `config.yaml` — no code changes required to adapt to a different dataset.

## How It Works

Given an Excel file of articles, the tool:

1. Classifies each article by source bias (Left, Center, Right) using configurable publication lists
2. Assigns each article to an administration period (Obama, Trump 1, Biden, Trump 2) based on publication date
3. Draws an equal random sample from each stratum (bias × administration)
4. Saves the result to an Excel file

With a fixed random seed, the same input always produces the same output.

## Customization

The code uses Political Bias and Administration as the categorical variables

To customize:

Political Bias - Can be your first categorial variable. For example: organization, platform, source etc.

Administation - Can be the second temporal variable. For example: time period, policy years, academic years, etc.

The code can remain the same, only the config.yaml needs updating.

## Requirements

- Python 3.x
- `pandas`
- `openpyxl`
- `pyyaml`

```bash
pip install pandas openpyxl pyyaml
```

## Input Format

Your Excel file must have at minimum:

| Column   | Description                                    |
| -------- | ---------------------------------------------- |
| `Source` | Publication name                               |
| `Date`   | Publication date (any format pandas can parse) |

## Setup

Edit `config.yaml` before running:

```yaml
initial_settings:
  input_file: 'articles.xlsx' # your data file
  output_file: 'sampled_output.xlsx'
  target_sample_size: 240 # must be divisible by (periods × categories)
  random_seed: 2025 # any integer; set for reproducibility

category_groups:
  categories:
    Left: ['The New York Times', 'CNN', 'MSNBC']
    Center: ['Reuters', 'Associated Press', 'NPR']
    Right: ['Fox News', 'Breitbart']

time_periods:
  periods:
    Obama:
      start: '2012-01-01'
      end: '2017-01-19'
    Trump_1:
      start: '2017-01-20'
      end: '2021-01-19'
```

## Usage

```bash
python stratified_sampler.py
```

The tool prints a per-stratum breakdown as it runs and saves the final sample to the configured output file.

## Sample Data

A sample dataset is included in the `Sample Articles/` folder. Use it to verify the tool runs correctly before substituting your own dataset.

## Behavior Notes

- Articles with sources not in any configured category are excluded and not sampled
- Articles outside all defined time periods are excluded
- If a stratum has fewer articles than the per-stratum target, all available articles in that stratum are used and a warning is printed
- `target_sample_size` should divide evenly by the number of strata (periods × categories) to avoid a silent remainder

## License

MIT License. See [LICENSE](LICENSE) for details.
