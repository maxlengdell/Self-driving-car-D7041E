import numpy as np

class Network:
    def __init__(self, model):
        #Input: distance left, right, forward, speed, gear
        #
        self.lr = 0.008
        self.model = model
        self.layers = []
        self.weights = []
        for layer in model:
            neurons = np.zeros((layer,1))
            self.layers.append(neurons)

        for i in range(len(model)-1):
            weight = np.random.uniform(-1,1,(model[i],model[i+1]))
            self.weights.append(weight)

        self.weights = np.array(self.weights)
        self.layers = np.array(self.layers)

    def next_move(self, car, maxRange):
        norm_dist = self.normalize_dist(car.dist,maxRange)

        norm_speed = self.normalize_input(car.speed)
        norm_gear = car.gear/4

        self.layers[0] = np.concatenate([car.dist,[car.speed],[car.gear]]) #input

        for i in range(1,len(self.layers)):
            self.layers[i] = self.activation(np.matmul(self.layers[i-1], self.weights[i-1]))

        #print("\r next move: {} layers: {}".format(np.argmax(self.layers[-1]),self.layers[-1]), end="\r")
        #print(self.layers[-1])
        return np.argmax(self.layers[-1])
    def normalize_input(self,X):
        #tanh_v = np.vectorize(self.tanh_norm)
        #return #tanh_v(X)
        return X/100
    def normalize_dist(self,X, maxRange):
        #print("X:", X[0])
        y = np.abs((X-np.int64(maxRange))/(np.int64(maxRange) - np.int64(0)))

        return y
    def activation(self,X):
        tanh_v = np.vectorize(self.tanh)
        return tanh_v(X)
    def mutate_weights(self, score, decay):

        #print("LR:", self.lr/(score/decay))
        for i in range(len(self.weights)):
            self.weights[i] = self.weights[i] + np.random.uniform(-1,1,(self.weights[i].shape[0], self.weights[i].shape[1])) * self.lr#/(score/decay)
    def store_weights(self, weights):
        self.weights = weights
    def ReLU(self,x):
        return np.maximum(x,0)
    def tanh_norm(self,x):
        x = x/150
        return (np.exp(x)-np.exp(-x))/(np.exp(-x)+np.exp(x))
    def tanh(self, x):
        return (np.exp(x)-np.exp(-x))/(np.exp(-x)+np.exp(x))
