from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class NormalModel:
    mu: float
    sigma: float

    def cdf(self, x: float) -> float:
        if self.sigma <= 0:
            return 1.0 if x >= self.mu else 0.0
        z = (x - self.mu) / (self.sigma * math.sqrt(2.0))
        return 0.5 * (1.0 + math.erf(z))

    def over_prob(self, line: float) -> float:
        return 1.0 - self.cdf(line)
