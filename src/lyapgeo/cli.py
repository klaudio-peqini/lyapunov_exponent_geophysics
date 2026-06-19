from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from .benchmarks import logistic_series, logistic_true_lyapunov
from .io import read_series
from .workflows import run_methods, save_analysis_outputs


def _method_list(value: str) -> list[str]:
    if value == 'all':
        return ['local', 'rosenstein', 'kantz']
    return [v.strip() for v in value.split(',') if v.strip()]


def _sheet_value(value: str):
    return int(value) if str(value).isdigit() else value


def add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument('--method', default='all', help='all or comma-list: local,rosenstein,kantz')
    p.add_argument('--emb-dim', type=int, default=3)
    p.add_argument('--tau', type=int, default=1)
    p.add_argument('--horizon', type=int, default=5)
    p.add_argument('--fit-start', type=int, default=0)
    p.add_argument('--fit-end', type=int, default=5)
    p.add_argument('--theiler', type=int, default=20)
    p.add_argument('--k-neighbors', type=int, default=8)
    p.add_argument('--max-pairs', type=int, default=5000)
    p.add_argument('--normalize', choices=['none', 'demean', 'zscore', 'minmax'], default='zscore')
    p.add_argument('--hist-rule', choices=['fd', 'scott', 'sturges', 'auto'], default='fd')
    p.add_argument('--n-bootstrap', type=int, default=2000)
    p.add_argument('--ci', type=float, default=0.95)
    p.add_argument('--center', choices=['median', 'mean'], default='median')
    p.add_argument('--seed', type=int, default=0)
    p.add_argument('--outdir', required=True)


def cmd_series(args: argparse.Namespace) -> int:
    t0 = time.perf_counter()
    if args.input_format in {'csv', 'excel'} and args.column is None and args.column_name is None:
        raise SystemExit('For CSV/Excel input, provide --column or --column-name.')
    column = args.field if args.input_format == 'radon-eye' else (args.column_name if args.column_name is not None else args.column)
    x = read_series(args.input, column=column, delimiter=args.delimiter, header_none=args.header_none, input_format=args.input_format, sheet=_sheet_value(args.sheet))
    results = run_methods(
        x,
        methods=_method_list(args.method),
        emb_dim=args.emb_dim,
        tau=args.tau,
        horizon=args.horizon,
        fit_start=args.fit_start,
        fit_end=args.fit_end,
        theiler=args.theiler,
        k_neighbors=args.k_neighbors,
        max_pairs=args.max_pairs,
        seed=args.seed,
        n_bootstrap=args.n_bootstrap,
        ci=args.ci,
        center=args.center,
        normalize=args.normalize,
    )
    save_analysis_outputs(results, args.outdir, hist_rule=args.hist_rule)
    dt = time.perf_counter() - t0
    print(f'Wrote outputs to: {args.outdir}')
    for r in results:
        print(f'{r.method:12s} LE={r.estimate:.6g}  CI{args.ci:.2f}=[{r.ci_low:.6g}, {r.ci_high:.6g}]  n={r.n_local}')
    print(f'Elapsed time: {dt:.3f} s')
    return 0


def cmd_benchmark_logistic(args: argparse.Namespace) -> int:
    t0 = time.perf_counter()
    x = logistic_series(args.r, args.x0, args.n, discard=args.discard)
    true_le = logistic_true_lyapunov(args.r, x)
    results = run_methods(
        x,
        methods=_method_list(args.method),
        emb_dim=args.emb_dim,
        tau=args.tau,
        horizon=args.horizon,
        fit_start=args.fit_start,
        fit_end=args.fit_end,
        theiler=args.theiler,
        k_neighbors=args.k_neighbors,
        max_pairs=args.max_pairs,
        seed=args.seed,
        n_bootstrap=args.n_bootstrap,
        ci=args.ci,
        center=args.center,
        normalize=args.normalize,
    )
    save_analysis_outputs(results, args.outdir, hist_rule=args.hist_rule)
    outdir = Path(args.outdir)
    pd.DataFrame({'x': x}).to_csv(outdir / 'logistic_series.csv', index=False)
    (outdir / 'true_lyapunov.txt').write_text(f'{true_le:.12g}\n', encoding='utf-8')
    dt = time.perf_counter() - t0
    print(f'True derivative-formula LE: {true_le:.6g}')
    for r in results:
        print(f'{r.method:12s} LE={r.estimate:.6g}  CI{args.ci:.2f}=[{r.ci_low:.6g}, {r.ci_high:.6g}]  n={r.n_local}')
    print(f'Wrote outputs to: {args.outdir}')
    print(f'Elapsed time: {dt:.3f} s')
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='lyapgeo', description='Lyapunov exponent workflows for geophysical time series.')
    sub = p.add_subparsers(dest='cmd', required=True)
    ps = sub.add_parser('series', help='Analyze CSV, Excel, or Radon Eye TXT time series.')
    ps.add_argument('--input', required=True, help='Input file.')
    g = ps.add_mutually_exclusive_group(required=False)
    g.add_argument('--column', type=int, help='0-based column index for CSV/Excel.')
    g.add_argument('--column-name', type=str, help='Column name for CSV/Excel.')
    ps.add_argument('--delimiter', default=',', help='CSV delimiter.')
    ps.add_argument('--header-none', action='store_true')
    ps.add_argument('--input-format', choices=['csv', 'excel', 'radon-eye'], default='csv')
    ps.add_argument('--sheet', default=0, help='Excel sheet name or 0-based sheet index.')
    ps.add_argument('--field', choices=['radon', 'temperature', 'humidity'], default='radon', help='Radon Eye field.')
    add_common_args(ps)
    ps.set_defaults(func=cmd_series)
    pb = sub.add_parser('benchmark-logistic', help='Validate estimators on a logistic-map benchmark.')
    pb.add_argument('--r', type=float, default=3.9)
    pb.add_argument('--x0', type=float, default=0.2)
    pb.add_argument('--n', type=int, default=6000)
    pb.add_argument('--discard', type=int, default=1000)
    add_common_args(pb)
    pb.set_defaults(func=cmd_benchmark_logistic)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == '__main__':
    raise SystemExit(main())
