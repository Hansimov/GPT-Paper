import os
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from utils.logger import logger


class ReadingBankDatasetProcessor:
    dataset_root = Path(__file__).parents[1] / "data" / "ReadingBank"

    def __init__(self):
        dataset_paths = list(self.dataset_root.glob("*"))
        for dataset_path in dataset_paths:
            logger.file(f"- {dataset_path}")


class RegionsVisualizer:
    def __init__(self, regions):
        self.regions = regions

    def draw_regions(regions):
        pass


class PDFRegionsOrderNetwork:
    def __init__(self):
        pass

    def prepare_dataset(self, sources, targets, test_sources=None, test_targets=None):
        self.sources = sources
        self.targets = targets
        self.test_sources = test_sources
        self.test_targets = test_targets

        # Define a custom dataset class
        class RegionOrderDataset(Dataset):
            def __init__(self, sources, targets):
                self.sources = sources
                self.targets = targets

            def __len__(self):
                return len(self.sources)

            def __getitem__(self, idx):
                source = self.sources[idx]
                target = self.targets[idx]
                return source, target

        # Create a dataset object
        self.train_dataset = RegionOrderDataset(self.sources, self.targets)
        if test_sources is not None and test_targets is not None:
            self.test_dataset = RegionOrderDataset(test_sources, test_targets)
        else:
            self.test_dataset = None

        # Create data loader objects
        self.train_data_loader = DataLoader(
            self.train_dataset, batch_size=4, shuffle=True
        )
        if self.test_dataset is not None:
            self.test_data_loader = DataLoader(self.test_dataset, batch_size=4)

        # Define a neural network architecture
        class Net(nn.Module):
            def __init__(self):
                super(Net, self).__init__()
                # Define layers here

            def forward(self, x):
                # Define forward pass here
                return x

        # Create a neural network object
        self.net = Net()

    def train(self, num_epochs=10):
        # Define a loss function
        criterion = nn.MSELoss()

        # Define an optimizer
        optimizer = optim.SGD(self.net.parameters(), lr=0.001)

        # Train the neural network
        for epoch in range(num_epochs):
            running_loss = 0.0
            for i, data in enumerate(self.train_data_loader):
                # Get the inputs
                sources, targets = data

                # Zero the parameter gradients
                optimizer.zero_grad()

                # Forward pass
                outputs = self.net(sources)

                # Compute loss
                loss = criterion(outputs, targets)

                # Backward pass
                loss.backward()

                # Update parameters
                optimizer.step()

                # Print statistics
                running_loss += loss.item()
            print(
                "Epoch: %d loss: %.3f"
                % (epoch + 1, running_loss / len(self.train_data_loader))
            )

    def test(self):
        if self.test_dataset is None:
            print("No test dataset provided.")
            return

        total_loss = 0.0
        criterion = nn.MSELoss()
        with torch.no_grad():
            for i, data in enumerate(self.test_data_loader):
                sources, targets = data
                outputs = self.net(sources)
                loss = criterion(outputs, targets)
                total_loss += loss.item()
        logger.line("Test loss: %.3f" % (total_loss / len(self.test_data_loader)))

    def sort_boxes(self, boxes):
        """
        Sorts region boxes on a page by human reading order.
        """
        with torch.no_grad():
            boxes_tensor = torch.tensor(boxes)
            sorted_boxes_tensor = self.net(boxes_tensor)
            sorted_boxes = sorted_boxes_tensor.tolist()
        return sorted_boxes


if __name__ == "__main__":
    # pdf_regions_order_network = PDFRegionsOrderNetwork(sources, targets)
    # pdf_regions_order_network.train()
    # pdf_regions_order_network.test()
    # sorted_boxes = pdf_regions_order_network.sort_boxes(boxes)
    data_processor = ReadingBankDatasetProcessor()
