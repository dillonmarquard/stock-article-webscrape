import torch
import numpy as np

class Metrics:
    def __init__(self):
        pass
    
    def update_confusion_matrix(self, outputs: torch.Tensor, labels: torch.Tensor) -> None:       
        for (guess,label) in zip(outputs.argmax(1),labels):
            self.confusion_matrix[guess,label] += 1
            
    def get_confusion_matrix(self,norm=False) -> np.array:
        if norm:
            return self.confusion_matrix / self.confusion_matrix.sum()
        return self.confusion_matrix
    
    def reset_confusion_matrix(self,num_classes: int) -> None:
        self.confusion_matrix = np.zeros((num_classes,num_classes))
    
    def classification_metrics(self,print_=False) -> tuple:
        stats = [self.accuracy(),self.precision(),self.recall(),self.f1_score(),self.confusion_matrix.sum()]
        s = "Accuracy: {}\nPrecision: {}\nRecall: {}\nf1-score: {}\nSupport: {}".format(stats[0],stats[1],stats[2],stats[3],stats[4])
        if print_:
            print(s)
        return stats
    
    def accuracy(self) -> float:
        stat = np.diag(self.confusion_matrix).sum() / self.confusion_matrix.sum()
        if np.isnan(stat) or np.isinf(stat):
            return 0.0
        else:
            return stat
        
    def precision(self) -> float:
        stat = np.nanmean(np.diag(self.confusion_matrix) / np.sum(self.confusion_matrix, axis = 0))
        if np.isnan(stat) or np.isinf(stat):
            return 0.0
        else:
            return stat
        return stat
        
    def recall(self) -> float:
        stat = np.nanmean(np.diag(self.confusion_matrix) / np.sum(self.confusion_matrix, axis = 1))
        if np.isnan(stat) or np.isinf(stat):
            return 0.0
        return stat
    
    def f1_score(self) -> float:
        p = self.precision()
        r = self.recall()
        if p+r < 1:
            return 0.0
        stat = (2.0*p*r)/(p+r)
        if np.isnan(stat):
            return 0.0
        else:
            return stat
    
    def feature_map(self,inputs: torch.Tensor,model,print_=False):
        no_of_layers=0
        conv_layers=[]

        model_children=list(model.children())

        for child in model_children:
            if type(child)==nn.Conv2d:
                conv_layers.append(child)
            elif type(child) == nn.Sequential:
                for layer in child.children():
                    if type(layer) == nn.Conv2d:
                        conv_layers.append(layer)
#         (inputs,labels) = next(iter(test_loader))
        results = [conv_layers[0](inputs.to(device))]
        for i in range(1, len(conv_layers)):
            results.append(conv_layers[i](results[-1]))
        outputs = results
        if print_:
            plt.imshow(inputs[0,0].to('cpu'),cmap='Greys')
            plt.show()
            for num_layer in range(len(outputs)):
                plt.figure(figsize=(50, 10))
                layer_viz = outputs[num_layer][0, :, :, :]
                layer_viz = layer_viz.data
#                 print("Layer ",num_layer+1)
                for i, filter in enumerate(layer_viz.to('cpu')):
                    if i == 8: 
                        break
                    plt.subplot(2, 8, i + 1)
                    plt.imshow(filter, cmap='gray')
                    plt.axis("off")
                plt.show()
                plt.close()
        return results
    
    def feature_map_diff(map1,map1_loss) -> np.array:
        pass