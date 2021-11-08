import numpy as np
import torch

class DataAug:
    def __init__(self):
        pass
    def __str__(self):
        return "Data Augment Class"

    def unaltered(self, inputs:torch.Tensor, proportion:float=0.0, inject:bool=False) -> torch.Tensor:
        return inputs

    def rand_pixel(self, inputs:torch.Tensor, proportion:float=0.0, inject:bool=False) -> torch.Tensor:
        if int(inputs.shape[2]*inputs.shape[3]*proportion) < 1:
            return inputs
        if proportion > 1.0:
            proportion = 1.0
        num_loss = int(inputs.shape[2]*inputs.shape[3]*proportion)
        lossyinputs = torch.clone(inputs)
        mask = np.concatenate((np.zeros((inputs.shape[0],num_loss)),np.ones((inputs.shape[0],int(inputs.shape[2]*inputs.shape[3] - num_loss)))),axis=1)
        for i in range(inputs.shape[0]):
            np.random.shuffle(mask[i])
        mask = torch.Tensor(mask.reshape((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3])))
        lossyinputs *= mask
        if inject:
            lossyinputs += torch.Tensor(1-mask)*torch.rand((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        return lossyinputs.type(torch.FloatTensor)

    def rand_column(self, inputs:torch.Tensor, proportion:float=0.0, inject:bool=False) -> torch.Tensor:
        if proportion > 1.0:
            proportion = 1.0
        num_col = int(inputs.shape[3]*proportion)
        to_rem = np.random.choice([x for x in range(inputs.shape[3])],size=num_col,replace=False)
        mask = np.ones((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        for col in to_rem:
            mask[:,:,:,col] = 0
        lossyinputs = torch.clone(inputs)*mask
        if inject:
            lossyinputs += torch.Tensor(1-mask)*torch.rand((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        return lossyinputs.type(torch.FloatTensor)

    def rand_row(self, inputs:torch.Tensor, proportion:float=0.0, inject:bool=False) -> torch.Tensor:
        if proportion > 1.0:
            proportion = 1.0
        num_col = int(inputs.shape[2]*proportion)
        to_rem = np.random.choice([x for x in range(inputs.shape[2])],size=num_col,replace=False)
        mask = np.ones((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        for row in to_rem:
            mask[:,:,row,:] = 0
        lossyinputs = torch.clone(inputs)*mask
        if inject:
            lossyinputs += torch.Tensor(1-mask)*torch.rand((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        return lossyinputs.type(torch.FloatTensor)

    def rand_rowcol(self, inputs:torch.Tensor, proportion:float=0.0, inject:bool=False) -> torch.Tensor:
        if proportion == 0.0:
            return inputs
        if proportion > 1.0:
            proportion = 1.0
        K = (1 - np.sqrt(1-proportion))/proportion
        lossyinputs = torch.clone(inputs)
        lossyinputs = self.rand_row(lossyinputs,proportion*K,inject)
        lossyinputs = self.rand_column(lossyinputs,proportion*K,inject)
        return lossyinputs.type(torch.FloatTensor)

    def rand_block(self, inputs:torch.Tensor, proportion:float=0.0, inject:bool=False) -> torch.Tensor:
        block_dim = (3,3)
        num_loc = int(inputs.shape[2]*inputs.shape[3]*proportion/(block_dim[0]*block_dim[1]))
        to_rem_r = np.random.choice([x for x in range(inputs.shape[2])],size=num_loc,replace=False)
        to_rem_c = np.random.choice([x for x in range(inputs.shape[3])],size=num_loc,replace=False)
        mask = np.ones((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        for (row,col) in zip(to_rem_r,to_rem_c):
            mask[:,:,row:row+block_dim[0],col:col+block_dim[1]] = 0
        lossyinputs = torch.clone(inputs)*mask
        if inject:
            lossyinputs += torch.Tensor(1-mask)*torch.rand((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        return lossyinputs.type(torch.FloatTensor)
    
    def pattern_column(self, inputs:torch.Tensor, proportion:float=0.0, inject:bool=False) -> torch.Tensor:
        if proportion > 1.0:
            proportion = 1.0
        num_col = int(inputs.shape[3]*proportion)
        to_rem = np.arange(0,inputs.shape[3],2) # default: every other column
        mask = np.ones((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        for col in to_rem:
            mask[:,:,:,col] = 0
        lossyinputs = torch.clone(inputs)*mask
        if inject:
            lossyinputs += torch.Tensor(1-mask)*torch.rand((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        return lossyinputs.type(torch.FloatTensor)

    def pattern_row(self, inputs:torch.Tensor, proportion:float=0.0, inject:bool=False) -> torch.Tensor:
        if proportion > 1.0:
            proportion = 1.0
        num_row = int(inputs.shape[2]*proportion)
        to_rem = np.arange(0,inputs.shape[2],2) # default: every other column
        mask = np.ones((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        for row in to_rem:
            mask[:,:,row,:] = 0
        lossyinputs = torch.clone(inputs)*mask
        if inject:
            lossyinputs += torch.Tensor(1-mask)*torch.rand((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        return lossyinputs.type(torch.FloatTensor)

    def pattern_checkerboard(self, inputs:torch.Tensor, proportion:float=0.0, inject:bool=False) -> torch.Tensor:
        lossyinputs = torch.clone(inputs)
        mask = np.zeros(inputs.shape)
        for i in range(inputs.shape[2]):
            for j in range(inputs.shape[3]):
                if (i*inputs.shape[3] + j + i%2) % 2 == 0:
                    mask[:,:,i,j] = 1
        lossyinputs = torch.Tensor(mask)*lossyinputs
        if inject:
            lossyinputs += torch.Tensor(1-mask)*torch.rand((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        return lossyinputs


















    
