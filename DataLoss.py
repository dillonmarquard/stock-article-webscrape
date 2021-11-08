import numpy as np
import torch

class DataLoss:
    def __init__(self):
        pass
    def unaltered(self,inputs: torch.Tensor,ppp: float=0.0) -> torch.Tensor:
        return inputs
    
    def random_per_pixel(self,inputs: torch.Tensor,ppp: float=0.0) -> torch.Tensor:
        # ppp: proportion per pixel
        lossyinputs = torch.clone(inputs)
        mask = torch.Tensor(np.random.rand(inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        lossyinputs = lossyinputs * (mask > ppp)
        return lossyinputs.type(torch.FloatTensor)
    
    def random_per_img(self,inputs: torch.Tensor,ppp: float=0.0) -> torch.Tensor:
        if int(inputs.shape[2]*inputs.shape[3]*ppp) < 1:
            return inputs
        if ppp > 1.0:
            ppp = 1.0
        num_loss = int(inputs.shape[2]*inputs.shape[3]*ppp)
        lossyinputs = torch.clone(inputs)
        mask = np.concatenate((np.zeros((inputs.shape[0],num_loss)),np.ones((inputs.shape[0],int(inputs.shape[2]*inputs.shape[3] - num_loss)))),axis=1)
        for i in range(inputs.shape[0]):
            np.random.shuffle(mask[i])
        mask = torch.Tensor(mask.reshape((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3])))
        lossyinputs *= mask
        return lossyinputs.type(torch.FloatTensor)
    
    def columns_per_img(self,inputs: torch.Tensor,ppp: float=0.0) -> torch.Tensor:
        num_col = int(inputs.shape[3]*ppp)
        to_rem = np.random.choice([x for x in range(inputs.shape[3])],size=num_col,replace=False)
        mask = np.ones((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        for col in to_rem:
            mask[:,:,:,col] = 0
        lossyinputs = torch.clone(inputs)*mask
        return lossyinputs.type(torch.FloatTensor)
    
    def rows_per_img(self,inputs: torch.Tensor,ppp: float=0.0) -> torch.Tensor:
        num_row = int(inputs.shape[2]*ppp)
        to_rem = np.random.choice([x for x in range(inputs.shape[2])],size=num_row,replace=False)
        mask = np.ones((inputs.shape[0],inputs.shape[1],inputs.shape[2],inputs.shape[3]))
        for row in to_rem:
            mask[:,:,row,:] = 0
        lossyinputs = torch.clone(inputs)*mask
        return lossyinputs.type(torch.FloatTensor)
    
    def rowcol_per_img(self,inputs: torch.Tensor,ppp: float=0.0) -> torch.Tensor:
        if ppp == 0.0:
            return inputs
        K = (1 - np.sqrt(1-ppp))/ppp
        lossyinputs = torch.clone(inputs)
        lossyinputs = self.rows_per_img(lossyinputs,ppp*K)
        lossyinputs = self.columns_per_img(lossyinputs,ppp*K)
        return lossyinputs.type(torch.FloatTensor)
    
    def pattern_column(self,inputs: torch.Tensor,ppp: float=0.0) -> torch.Tensor:
        lossyinputs = torch.clone(inputs)
        for i in range(0,lossyinputs.shape[3],2):
            lossyinputs[:,:,:,i] = 0
        return lossyinputs
    
    def pattern_row(self,inputs: torch.Tensor,ppp: float=0.0) -> torch.Tensor:
        lossyinputs = torch.clone(inputs)
        for i in range(0,lossyinputs.shape[2],2):
            lossyinputs[:,:,i,:] = 0
        return lossyinputs
    
    def pattern_checkerboard(self,inputs: torch.Tensor,ppp: float=0.0) -> torch.Tensor:
        lossyinputs = torch.clone(inputs)
        mask = np.zeros(inputs.shape)
        for i in range(inputs.shape[2]):
            for j in range(inputs.shape[3]):
                if (i*inputs.shape[3] + j + i%2) % 2 == 0:
                    mask[:,:,i,j] = 1
        lossyinputs = torch.Tensor(mask)*lossyinputs
        return lossyinputs

    def random_block(self,inputs: torch.Tensor,ppp: float=0.0) -> torch.Tensor:
    	return inputs
