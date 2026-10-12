"""Motor EL didáctico con interfaces POO; no es una medición IFRS 9 completa."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import fsum, isfinite


@dataclass(frozen=True)
class Exposure:
    pd: float
    lgd: float
    ead: float

    def __post_init__(self):
        if not all(isfinite(float(x)) for x in (self.pd, self.lgd, self.ead)):
            raise ValueError("Los parámetros deben ser finitos")
        if not (0 <= self.pd <= 1 and 0 <= self.lgd <= 1 and self.ead >= 0):
            raise ValueError("PD y LGD en [0,1]; EAD >= 0")


class ExpectedLossModel(ABC):
    @abstractmethod
    def calculate(self, exposures: list[Exposure]) -> float:
        """Calcula pérdida esperada agregada."""


class DeterministicEL(ExpectedLossModel):
    def calculate(self, exposures: list[Exposure]) -> float:
        return fsum(e.pd * e.lgd * e.ead for e in exposures)


def example() -> list[Exposure]:
    return [Exposure(0.02, 0.4, 1000),
            Exposure(0.05, 0.6, 2000),
            Exposure(0.10, 0.3, 500)]


if __name__ == "__main__":
    result = DeterministicEL().calculate(example())
    assert abs(result - 83.0) < 1e-10
    print(f"EL={result:.10f}")
