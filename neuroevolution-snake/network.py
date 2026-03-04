"""
Minimal feedforward neural network implemented with NumPy only.
No autograd, no backprop - weights are evolved by the genetic algorithm.
"""
import numpy as np
import copy


class NeuralNetwork:
    """
    Fully-connected network with tanh activations on hidden layers.
    Output layer returns raw logits (argmax gives the chosen action).
    """

    def __init__(self, layer_sizes: list[int]):
        """
        layer_sizes: e.g. [24, 16, 16, 4]
          - 24 inputs  (8-direction vision ×3)
          - two hidden layers of 16 neurons
          - 4 outputs  (up / right / down / left)
        """
        self.layer_sizes = layer_sizes
        self.weights: list[np.ndarray] = []
        self.biases:  list[np.ndarray] = []

        rng = np.random.default_rng()
        for i in range(len(layer_sizes) - 1):
            fan_in = layer_sizes[i]
            fan_out = layer_sizes[i + 1]
            # Xavier/Glorot init
            scale = np.sqrt(2.0 / (fan_in + fan_out))
            self.weights.append(rng.normal(0, scale, (fan_in, fan_out)).astype(np.float32))
            self.biases.append(np.zeros(fan_out, dtype=np.float32))

    # ------------------------------------------------------------------
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass.  x shape: (input_size,)  →  returns (output_size,)."""
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            x = x @ w + b
            if i < len(self.weights) - 1:   # hidden layers: tanh
                x = np.tanh(x)
        return x   # raw logits for last layer

    # ------------------------------------------------------------------
    def get_weights_flat(self) -> np.ndarray:
        parts = []
        for w, b in zip(self.weights, self.biases):
            parts.append(w.ravel())
            parts.append(b.ravel())
        return np.concatenate(parts)

    def set_weights_flat(self, flat: np.ndarray):
        idx = 0
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            w_n = w.size
            b_n = b.size
            self.weights[i] = flat[idx: idx + w_n].reshape(w.shape)
            idx += w_n
            self.biases[i] = flat[idx: idx + b_n].reshape(b.shape)
            idx += b_n

    # ------------------------------------------------------------------
    @property
    def num_params(self) -> int:
        return sum(w.size + b.size for w, b in zip(self.weights, self.biases))

    def copy(self) -> "NeuralNetwork":
        nn = NeuralNetwork.__new__(NeuralNetwork)
        nn.layer_sizes = self.layer_sizes[:]
        nn.weights = [w.copy() for w in self.weights]
        nn.biases  = [b.copy() for b in self.biases]
        return nn

    def __repr__(self):
        return (f"NeuralNetwork({self.layer_sizes}, "
                f"params={self.num_params:,})")
