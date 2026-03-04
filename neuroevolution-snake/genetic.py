"""
Genetic Algorithm for evolving neural network weights.

No gradient descent — fitness is entirely determined by the Snake score.
Operators:
  • Elitism      – top-k agents survive unchanged
  • Tournament   – stochastic parent selection
  • Uniform crossover – child inherits each weight independently from a parent
  • Gaussian mutation – random noise applied per-weight with probability p
"""
import numpy as np
from network import NeuralNetwork
from snake_env import SnakeEnv

# Default network topology (24 inputs → 2 hidden → 4 outputs)
DEFAULT_LAYERS = [24, 16, 16, 4]


# ──────────────────────────────────────────────────────────────────────
# Agent evaluation
# ──────────────────────────────────────────────────────────────────────

def evaluate_agent(
    network: NeuralNetwork,
    grid_size: int = 20,
    max_steps_no_food: int = 150,
    n_trials: int = 3,
) -> tuple[float, float, float]:
    """
    Run the agent for n_trials episodes and return averaged metrics.

    Fitness formula:
        score² × 1000 + steps_survived
    The quadratic score term strongly rewards eating; steps_survived
    prevents agents that learn to dodge walls without eating from
    dominating the early generations.

    Returns (fitness, avg_score, avg_steps).
    """
    total_score = 0.0
    total_steps = 0.0
    total_fitness = 0.0

    for _ in range(n_trials):
        env = SnakeEnv(grid_size=grid_size, max_steps_no_food=max_steps_no_food)
        obs = env.reset()
        done = False

        while not done:
            logits = network.forward(obs)
            action = int(np.argmax(logits))
            obs, _, done, info = env.step(action)

        s = info["score"]
        t = info["steps"]
        total_score   += s
        total_steps   += t
        total_fitness += s ** 2 * 1000 + t

    n = n_trials
    return total_fitness / n, total_score / n, total_steps / n


def replay_agent(
    network: NeuralNetwork,
    grid_size: int = 20,
    max_steps_no_food: int = 150,
) -> list[np.ndarray]:
    """
    Play one episode and return every grid frame for animation.
    """
    env = SnakeEnv(grid_size=grid_size, max_steps_no_food=max_steps_no_food)
    obs = env.reset()
    frames = [env.render_grid()]
    done = False

    while not done:
        logits = network.forward(obs)
        action = int(np.argmax(logits))
        obs, _, done, _ = env.step(action)
        frames.append(env.render_grid())

    return frames


# ──────────────────────────────────────────────────────────────────────
# GA operators
# ──────────────────────────────────────────────────────────────────────

def init_population(pop_size: int, layer_sizes: list[int]) -> list[NeuralNetwork]:
    return [NeuralNetwork(layer_sizes) for _ in range(pop_size)]


def tournament_select(
    population: list[NeuralNetwork],
    fitnesses: np.ndarray,
    k: int = 5,
) -> NeuralNetwork:
    """Select one parent via k-tournament."""
    contenders = np.random.choice(len(population), k, replace=False)
    winner = contenders[np.argmax(fitnesses[contenders])]
    return population[winner]


def uniform_crossover(w1: np.ndarray, w2: np.ndarray) -> np.ndarray:
    """Each gene (weight) is inherited from a randomly chosen parent."""
    mask = np.random.rand(len(w1)) > 0.5
    return np.where(mask, w1, w2)


def mutate(
    weights: np.ndarray,
    mutation_rate: float = 0.10,
    mutation_std: float  = 0.20,
) -> np.ndarray:
    """
    Apply independent Gaussian perturbations with probability mutation_rate.
    A small fraction of genes receive larger 'macro-mutations' (std × 5)
    to aid exploration when the population has converged.
    """
    w = weights.copy()
    n = len(w)

    # Standard micro-mutations
    micro_mask = np.random.rand(n) < mutation_rate
    w[micro_mask] += np.random.randn(micro_mask.sum()) * mutation_std

    # Occasional macro-mutations (1 % of genes)
    macro_mask = np.random.rand(n) < 0.01
    w[macro_mask] += np.random.randn(macro_mask.sum()) * mutation_std * 5

    return w


# ──────────────────────────────────────────────────────────────────────
# One generation
# ──────────────────────────────────────────────────────────────────────

def evolve_generation(
    population:    list[NeuralNetwork],
    fitnesses:     np.ndarray,
    mutation_rate: float = 0.10,
    mutation_std:  float = 0.20,
    elite_n:       int   = 3,
    tournament_k:  int   = 5,
) -> list[NeuralNetwork]:
    """
    Produce the next generation:
      1. Elitism — copy the top elite_n agents unchanged.
      2. Fill the rest via tournament selection + crossover + mutation.
    """
    pop_size   = len(population)
    layer_sizes = population[0].layer_sizes

    sorted_idx  = np.argsort(fitnesses)[::-1]
    new_pop     = [population[i].copy() for i in sorted_idx[:elite_n]]

    while len(new_pop) < pop_size:
        p1 = tournament_select(population, fitnesses, tournament_k)
        p2 = tournament_select(population, fitnesses, tournament_k)
        w1 = p1.get_weights_flat()
        w2 = p2.get_weights_flat()
        child_w = uniform_crossover(w1, w2)
        child_w = mutate(child_w, mutation_rate, mutation_std)
        child = NeuralNetwork(layer_sizes)
        child.set_weights_flat(child_w)
        new_pop.append(child)

    return new_pop
