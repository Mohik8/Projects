"""
GA Penalty Optimizer
--------------------
Given a user's proposed activity and the bylaws it violates,
the GA evolves a set of activity parameter modifications that
minimise total penalties/violations with minimal disruption to
the user's original plan.

Chromosome: list of float "adjustment" values, one per adjustable dimension.
  e.g. [start_time_offset_hours, end_time_offset_hours, distance_m, ...]

Fitness: higher = better (fewer violations, smaller adjustments from original).
"""

import random
import math
import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, AsyncGenerator


@dataclass
class GAConfig:
    population_size: int = 80
    generations: int = 60
    mutation_rate: float = 0.15
    crossover_rate: float = 0.8
    elitism: int = 4
    tournament_k: int = 4


@dataclass
class Dimension:
    """One adjustable parameter of the user's plan."""
    name: str
    original: float      # user's original value
    min_val: float
    max_val: float
    unit: str = ""
    weight: float = 1.0  # how much the user cares about this dimension


def _random_chromosome(dims: list[Dimension]) -> list[float]:
    return [random.uniform(d.min_val, d.max_val) for d in dims]


def _fitness(
    chromosome: list[float],
    dims: list[Dimension],
    violation_fn: Callable[[list[float]], float],
) -> float:
    """
    fitness = -violations - disruption_cost
    More negative = worse. We maximise (least negative = best).
    violations: penalty from violation_fn (0 = fully legal)
    disruption: weighted sum of absolute deviations from user's originals
    """
    violations = violation_fn(chromosome)
    disruption = sum(
        d.weight * abs(chromosome[i] - d.original) / max(d.max_val - d.min_val, 1e-9)
        for i, d in enumerate(dims)
    )
    return -(violations * 10.0 + disruption)


def _tournament_select(population: list, fitnesses: list[float], k: int) -> list[float]:
    candidates = random.sample(list(zip(population, fitnesses)), k)
    return max(candidates, key=lambda x: x[1])[0]


def _crossover(p1: list[float], p2: list[float]) -> tuple[list[float], list[float]]:
    if len(p1) < 2:
        return p1[:], p2[:]
    point = random.randint(1, len(p1) - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]


def _mutate(chromosome: list[float], dims: list[Dimension], rate: float) -> list[float]:
    result = chromosome[:]
    for i, d in enumerate(dims):
        if random.random() < rate:
            # Gaussian perturbation clamped to bounds
            sigma = (d.max_val - d.min_val) * 0.1
            result[i] = max(d.min_val, min(d.max_val, result[i] + random.gauss(0, sigma)))
    return result


async def run_ga(
    dims: list[Dimension],
    violation_fn: Callable[[list[float]], float],
    config: GAConfig = GAConfig(),
    on_generation: AsyncGenerator | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Async generator — yields one dict per generation:
    {
      "generation": int,
      "best_fitness": float,
      "avg_fitness": float,
      "best_chromosome": list[float],
      "population_sample": list[list[float]],   # 10 random individuals
      "violations": float,
    }
    """
    population = [_random_chromosome(dims) for _ in range(config.population_size)]

    for gen in range(config.generations):
        fitnesses = [_fitness(c, dims, violation_fn) for c in population]

        # ── stats ──
        best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        best = population[best_idx]
        best_fit = fitnesses[best_idx]
        avg_fit = sum(fitnesses) / len(fitnesses)
        violations = violation_fn(best)

        yield {
            "generation": gen + 1,
            "best_fitness": round(best_fit, 4),
            "avg_fitness": round(avg_fit, 4),
            "best_chromosome": best[:],
            "population_sample": random.sample(population, min(10, len(population))),
            "violations": round(violations, 4),
        }

        await asyncio.sleep(0)   # yield control to event loop

        # ── next generation ──
        # Elitism — carry best individuals forward
        sorted_pop = sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)
        new_population = [ind for ind, _ in sorted_pop[: config.elitism]]

        while len(new_population) < config.population_size:
            p1 = _tournament_select(population, fitnesses, config.tournament_k)
            p2 = _tournament_select(population, fitnesses, config.tournament_k)
            if random.random() < config.crossover_rate:
                c1, c2 = _crossover(p1, p2)
            else:
                c1, c2 = p1[:], p2[:]
            new_population.append(_mutate(c1, dims, config.mutation_rate))
            if len(new_population) < config.population_size:
                new_population.append(_mutate(c2, dims, config.mutation_rate))

        population = new_population


def build_violation_fn(bylaws_matched: list[dict], dims: list[Dimension]) -> Callable:
    """
    Construct a violation function from the matched bylaws.
    Returns a float: 0.0 = no violations, higher = more/worse violations.
    This is intentionally simple so it can be extended per bylaw constraint type.
    """
    def violation_fn(chromosome: list[float]) -> float:
        dim_map = {d.name: chromosome[i] for i, d in enumerate(dims)}
        total = 0.0

        for bylaw in bylaws_matched:
            c = bylaw.get("constraints", {})

            # Time-based violations
            if "quiet_start" in c and "start_time" in dim_map:
                quiet_h = int(c["quiet_start"].split(":")[0])
                end_h = int(c.get("quiet_end", "08:00").split(":")[0]) or 24
                t = dim_map["start_time"]
                if t >= quiet_h or t < end_h % 24:
                    total += 1.0

            if "end_time" in dim_map and "quiet_start" in c:
                quiet_h = int(c["quiet_start"].split(":")[0])
                t = dim_map["end_time"]
                if t > quiet_h:
                    total += 1.0

            # Distance violations
            if "min_distance_m" in c and "distance_m" in dim_map:
                if dim_map["distance_m"] < c["min_distance_m"]:
                    total += (c["min_distance_m"] - dim_map["distance_m"]) / c["min_distance_m"]

            # Licence/permit — binary, GA can't fix these (penalise heavily)
            if c.get("licence_required") and not dim_map.get("has_licence", 1):
                total += 2.0
            if c.get("stb_prohibited"):
                total += 5.0   # hard constraint — location change required

        return total

    return violation_fn
