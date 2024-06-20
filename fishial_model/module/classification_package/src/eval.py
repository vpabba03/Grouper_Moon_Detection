import numpy as np
import typing as t
import torch
import os

from torch import nn
from torch.utils.data import DataLoader
from module.classification_package.src.dataset import FishialDataset
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KDTree


def dump_embeddings(dataloader: DataLoader, model: nn.Module, device: torch.device) -> np.ndarray:
    embeddings = []
    for i, batch in enumerate(dataloader):
        embeddings_batch = model(batch[0].to(device))
        embeddings.append(embeddings_batch.cpu().detach().numpy())

    return np.vstack(embeddings)


def accuracy_at_k(y_true: np.ndarray, embeddings: np.ndarray, K: int, sample: int = None) -> float:
    kdtree = KDTree(embeddings)
    if sample is None:
        sample = len(y_true)
    y_true_sample = y_true[:sample]

    indices_of_neighbours = kdtree.query(embeddings[:sample], k=K + 1, return_distance=False)[:, 1:]

    y_hat = y_true[indices_of_neighbours]

    matching_category_mask = np.expand_dims(np.array(y_true_sample), -1) == y_hat

    matching_cnt = np.sum(matching_category_mask.sum(-1) > 0)
    accuracy = matching_cnt / len(y_true_sample)

    return accuracy


def accuracy(labels: np.array, dump: np.ndarray) -> t.List[float]:
    y_pred = np.argmax(dump, axis=1)
    accuracies = []
    acc = accuracy_score(labels, y_pred)
    accuracies.append(acc)
    return accuracies


def evaluate_at_k(labels: np.array, dump: np.ndarray) -> t.List[float]:
    accuracies = []
    for K in [1, 3, 5]:
        acc_k = accuracy_at_k(labels, dump, K)
        accuracies.append(round(acc_k, 7))
    return accuracies


def evaluate(model: nn.Module, datasets: [FishialDataset], metrics: list, device: torch.device):
    total_accuracy = {}
    for dataset in datasets:
        model.eval()
        data_loader = DataLoader(dataset, batch_size=128, shuffle=False)
        dump = dump_embeddings(data_loader, model, device)
        for metric in metrics:
            if metric == 'at_k':
                accuracies = evaluate_at_k(np.array(dataset.targets), dump)
                total_accuracy.update(
                    {str(dataset.train_state) + "_" + metric: accuracies}
                )
            elif metric == 'accuracy':
                accuracies = accuracy(np.array(dataset.data_frame['target'].tolist()), dump)
                total_accuracy.update(
                    {str(dataset.train_state) + "_" + metric: accuracies}
                )
    return total_accuracy