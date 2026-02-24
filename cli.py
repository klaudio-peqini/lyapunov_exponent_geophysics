"""
CLI entrypoint: lyapgeo
"""
from __future__ import annotations

import argparse
import time

from .bifurcation import BifurcationConfig, gaussian_bifurcation, logistic_bifurcation, logexp_bifurcation, plot_bifurcation
from .io import CSVLoadConfig, load_series_from_csv
from .lorenz import LorenzLyapConfig, lyapunov_spectrum
from .lyapunov import SeriesLyapunovConfig, lyapunov_exponent_series


def _add_le_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--eps", type=float, default=0.01, help="Neighborhood threshold (epsilon).")
    p.add_argument("--l", type=int, default=5, help="Prediction horizon length.")
    p.add_argument("--max-pairs", type=int, default=1000, help="Maximum number of neighbor pairs.")
    p.add_argument("--min-separation", type=int, default=10, help="Ignore pairs with |i-j| <= this.")
    p.add_argument("--seed", type=int, default=0, help="Random seed for subsampling pairs.")
    p.add_argument("--tiny", type=float, default=1e-12, help="Small value to avoid log(0).")


def cmd_series(args: argparse.Namespace) -> int:
    t0 = time.perf_counter()

    x = load_series_from_csv(
        CSVLoadConfig(
            path=args.csv,
            column=args.column if args.column is not None else args.column_name,
            delimiter=args.delimiter,
            skiprows=args.skiprows,
            header_none=args.header_none,
        )
    )
    le = lyapunov_exponent_series(
        x,
        SeriesLyapunovConfig(
            eps=args.eps, l=args.l, max_pairs=args.max_pairs, min_separation=args.min_separation, seed=args.seed, tiny=args.tiny
        ),
    )

    dt = time.perf_counter() - t0
    print(f"Lyapunov exponent (series estimator): {le:.6g}")
    print(f"Elapsed time: {dt:.3f} s  |  N={x.size}  pairs<= {args.max_pairs}  l={args.l} eps={args.eps}")
    return 0


def cmd_bifurcation(args: argparse.Namespace) -> int:
    t0 = time.perf_counter()
    le_cfg = SeriesLyapunovConfig(
        eps=args.eps, l=args.l, max_pairs=args.max_pairs, min_separation=args.min_separation, seed=args.seed, tiny=args.tiny
    )
    cfg = BifurcationConfig(steps=args.steps, last=args.last, rounding=args.rounding, le=le_cfg)

    if args.map == "logistic":
        param, steady, le_f, le_s = logistic_bifurcation(args.r_min, args.r_max, args.dr, args.x0, cfg)
        xlabel, title = "r", "Logistic map"
    elif args.map == "gaussian":
        param, steady, le_f, le_s = gaussian_bifurcation(args.beta_min, args.beta_max, args.db, args.alpha, args.x0, cfg)
        xlabel, title = "β", "Gaussian map"
    else:
        param, steady, le_f, le_s = logexp_bifurcation(args.r_min, args.r_max, args.dr, args.x0, cfg)
        xlabel, title = "r", "Logistic exponential map"

    plot_bifurcation(param, steady, le_f, le_s, xlabel=xlabel, outpath=args.out, title=title)
    dt = time.perf_counter() - t0
    print(f"Wrote: {args.out}")
    print(f"Elapsed time: {dt:.3f} s  |  points={param.size}  steps={cfg.steps}  last={cfg.last}")
    return 0


def cmd_lorenz(args: argparse.Namespace) -> int:
    t0 = time.perf_counter()
    cfg = LorenzLyapConfig(sigma=args.sigma, r=args.r, b=args.b, dt=args.dt, iters=args.iters, transient=args.transient, seed=args.seed)
    le = lyapunov_spectrum(cfg)
    dt = time.perf_counter() - t0
    print("Lorenz Lyapunov spectrum (QR):", " ".join(f"{x:.6g}" for x in le))
    print(f"Elapsed time: {dt:.3f} s  |  iters={cfg.iters} dt={cfg.dt} transient={cfg.transient}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="lyapgeo", description="Lyapunov exponent tools for geophysical time series.")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("series", help="Compute Lyapunov exponent from a CSV column.")
    ps.add_argument("--csv", required=True, help="Path to CSV file.")
    g = ps.add_mutually_exclusive_group(required=True)
    g.add_argument("--column", type=int, default=None, help="0-based column index.")
    g.add_argument("--column-name", dest="column_name", type=str, help="Column name.")
    ps.add_argument("--delimiter", default=",", help="CSV delimiter.")
    ps.add_argument("--skiprows", type=int, default=0, help="Rows to skip.")
    ps.add_argument("--header-none", action="store_true", help="Treat CSV as headerless.")
    _add_le_args(ps)
    ps.set_defaults(func=cmd_series)

    pb = sub.add_parser("bifurcation", help="Generate bifurcation diagram + LE curves for discrete maps.")
    pb.add_argument("map", choices=["logistic", "gaussian", "logexp"])
    pb.add_argument("--out", required=True, help="Output file (PDF/PNG).")
    pb.add_argument("--steps", type=int, default=2000)
    pb.add_argument("--last", type=int, default=300)
    pb.add_argument("--rounding", type=int, default=4)
    pb.add_argument("--x0", type=float, default=0.2)

    pb.add_argument("--r-min", type=float, default=2.8)
    pb.add_argument("--r-max", type=float, default=4.0)
    pb.add_argument("--dr", type=float, default=0.01)

    pb.add_argument("--alpha", type=float, default=1.0)
    pb.add_argument("--beta-min", type=float, default=-1.0)
    pb.add_argument("--beta-max", type=float, default=1.0)
    pb.add_argument("--db", type=float, default=0.01)

    _add_le_args(pb)
    pb.set_defaults(func=cmd_bifurcation)

    pl = sub.add_parser("lorenz-lyap", help="Compute Lorenz Lyapunov spectrum (QR method).")
    pl.add_argument("--sigma", type=float, default=10.0)
    pl.add_argument("--r", type=float, default=28.0)
    pl.add_argument("--b", type=float, default=8.0 / 3.0)
    pl.add_argument("--dt", type=float, default=1.0)
    pl.add_argument("--iters", type=int, default=1000)
    pl.add_argument("--transient", type=int, default=100)
    pl.add_argument("--seed", type=int, default=0)
    pl.set_defaults(func=cmd_lorenz)

    return p


def main(argv: list[str] | None = None) -> int:
    p = build_parser()
    args = p.parse_args(argv)
    return int(args.func(args))
