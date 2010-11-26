class LayeredObject(object):
    def __init__(self, color, position, orientation):
        self.color = color
        self.position = position
        self.orientation = orientation
        self.layers = []

    def add_layer(self, layer):
        self.layers.append(layer)

    def project_layers(self):
        return [layer.project(self.position, self.orientation)
                for layer in self.layers]
