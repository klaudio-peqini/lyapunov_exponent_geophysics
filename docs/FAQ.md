# FAQ

## My series returns NaN for the Lyapunov exponent
That usually means the estimator found no valid neighbor pairs. Try:
- increase `--eps`
- reduce `--min-separation`
- reduce `--l`
- ensure the series is numeric (no NaNs)

## How do I speed it up?
- reduce `--max-pairs`
- reduce `--l`
- use a shorter time window for exploratory runs
