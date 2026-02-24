"""
Lorenz Lyapunov spectrum via tangent linear model + QR.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
from scipy.integrate import solve_ivp


def rhs(t: float, v: np.ndarray, sigma: float, r: float, b: float) -> np.ndarray:
    x, y, z = v
    return np.array([sigma * (y - x), r * x - y - x * z, x * y - b * z], dtype=float)


def jacobian(t: float, v: np.ndarray, sigma: float, r: float, b: float) -> np.ndarray:
    x, y, z = v
    return np.array([[-sigma, sigma, 0.0], [r - z, -1.0, -x], [y, x, -b]], dtype=float)


@dataclass(frozen=True)
class LorenzLyapConfig:
    sigma: float = 10.0
    r: float = 28.0
    b: float = 8.0 / 3.0
    dt: float = 1.0
    iters: int = 1000
    transient: int = 100
    seed: int = 0


def lyapunov_spectrum(cfg: LorenzLyapConfig) -> np.ndarray:
    n = 3
    n_lyap = 3
    rng = np.random.default_rng(cfg.seed)

    v = rng.random(n)
    U = rng.random((n, n_lyap))

    def assemble(vv: np.ndarray, UU: np.ndarray) -> np.ndarray:
        return np.hstack((vv, UU.flatten()))

    def disassemble(state: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        return state[:n], state[n:].reshape(n, n_lyap)

    def rhs_aug(t: float, state: np.ndarray) -> np.ndarray:
        vv, UU = disassemble(state)
        dv = rhs(t, vv, cfg.sigma, cfg.r, cfg.b)
        dU = jacobian(t, vv, cfg.sigma, cfg.r, cfg.b) @ UU
        return assemble(dv, dU)

    local = []
    for _ in range(cfg.iters):
        sol = solve_ivp(
            rhs_aug,
            (0.0, cfg.dt),
            assemble(v, U),
            t_eval=(cfg.dt,),
            max_step=cfg.dt,
            rtol=1e-7,
            atol=1e-9,
        )
        v, U = disassemble(sol.y[:, -1])
        Q, R = np.linalg.qr(U)
        U = Q
        local.append(np.log(np.abs(np.diag(R))) / cfg.dt)

    local = np.asarray(local, dtype=float)
    if cfg.transient >= local.shape[0]:
        return np.mean(local, axis=0)
    return np.mean(local[cfg.transient :], axis=0)
