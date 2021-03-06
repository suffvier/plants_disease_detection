class BilinearCNN(nn.Module):
    def __init__(self):
        # Convolution and pooling layers of VGG-16.
        nn.Module.__init__(self)
        self.features = torchvision.models.vgg16(pretrained=True).features
        self.features = torch.nn.Sequential(*list(self.features.children())
                                            [:-1])  # Remove pool5.
        # Linear classifier.
        self.fc = torch.nn.Linear(512**2, config.num_classes)

        # Freeze all previous layers.
        #for param in self.features.parameters():
        #    param.requires_grad = False
        # Initialize the fc layers.
        torch.nn.init.kaiming_normal(self.fc.weight.data)
        if self.fc.bias is not None:
            torch.nn.init.constant(self.fc.bias.data, val=0)

    def forward(self, X):
        """Forward pass of the network.
        Args:
            X, torch.autograd.Variable of shape N*3*448*448.
        Returns:
            Score, torch.autograd.Variable of shape N*200.
        """
        N = X.size()[0]
        assert X.size() == (N, 3, 448, 448)
        X = self.features(X)
        assert X.size() == (N, 512, 28, 28)
        X = X.view(N, 512, 28**2)
        X = torch.bmm(X, torch.transpose(X, 1, 2)) / (28**2)  # Bilinear
        assert X.size() == (N, 512, 512)
        X = X.view(N, 512**2)
        X = torch.sqrt(X + 1e-5)
        X = torch.nn.functional.normalize(X)
        X = self.fc(X)
        assert X.size() == (N, config.num_classes)
        return X
