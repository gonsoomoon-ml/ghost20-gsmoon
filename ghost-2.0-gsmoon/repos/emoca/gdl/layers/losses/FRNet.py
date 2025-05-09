# THIS FILE HAS BEEN COPIEF FROM THE EMOCA REPOSITORY

import torch.nn as nn
import numpy as np
import torch
# from pro_gan_pytorch.PRO_GAN import ProGAN, Generator, Discriminator
import torch.nn.functional as F
import cv2
from torch.autograd import Variable
import math


def conv3x3(in_planes, out_planes, stride=1):
    """3x3 convolution with padding"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(Bottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, stride=stride, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class ResNet(nn.Module):

    def __init__(self, block, layers, num_classes=1000, include_top=True):
        self.inplanes = 64
        super(ResNet, self).__init__()
        self.include_top = include_top

        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=0, ceil_mode=True)

        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        self.avgpool = nn.AvgPool2d(7, stride=1)
        self.fc = nn.Linear(512 * block.expansion, num_classes)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)

    def forward(self, x):
        feats = []
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        feats.append(x)
        x = self.layer2(x)
        feats.append(x)
        x = self.layer3(x)
        feats.append(x)
        x = self.layer4(x)
        feats.append(x)
        
        x = self.avgpool(x)

        if not self.include_top:
            return x, feats

        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x, feats


def resnet50(**kwargs):
    """Constructs a ResNet-50 model.
    """
    model = ResNet(Bottleneck, [3, 4, 6, 3], **kwargs)
    return model


import pickle

def load_state_dict(model, fname):
    """
    Set parameters converted from Caffe models authors of VGGFace2 provide.
    See https://www.robots.ox.ac.uk/~vgg/data/vgg_face2/.
    Arguments:
        model: model
        fname: file name of parameters converted from a Caffe model, assuming the file format is Pickle.
    """
    # 경로를 수정하여 이미 존재하는 체크포인트 파일을 사용
    fname = "repos/emoca/gdl_apps/EmotionRecognition/ResNet50/checkpoints/deca-epoch=01-val_loss_total/dataloader_idx_0=1.27607644.ckpt"
    print("## fname: ", fname)
    
    # torch.load에 weights_only=False 파라미터 추가
    weights = torch.load(fname, map_location='cpu', weights_only=False)
    
    # 체크포인트 파일의 구조에 따라 state_dict 추출
    if 'state_dict' in weights:
        weights = weights['state_dict']
    
    new_weights = {}
    for k, v in weights.items():
        # 'backbone' 접두사 처리
        if k.startswith('backbone'):
            new_weights[k[9:]] = v.cpu().numpy() if torch.is_tensor(v) else v
        else:
            new_weights[k] = v.cpu().numpy() if torch.is_tensor(v) else v
    
    own_state = model.state_dict()
    
    for name, param in new_weights.items():
        if name in own_state:
            try:
                own_state[name].copy_(torch.from_numpy(param) if isinstance(param, np.ndarray) else param)
            except Exception as e:
                print(f"오류 발생 ({name}): {e}")
                print(f"모델 파라미터 크기: {own_state[name].size()}")
                print(f"체크포인트 파라미터 크기: {param.shape if hasattr(param, 'shape') else 'unknown'}")
        else:
            # 모델에 없는 파라미터는 무시 (strict=False와 같은 효과)
            pass
    
    return model

# def load_state_dict(model, fname):
#     """
#     Set parameters converted from Caffe models authors of VGGFace2 provide.
#     See https://www.robots.ox.ac.uk/~vgg/data/vgg_face2/.
#     Arguments:
#         model: model
#         fname: file name of parameters converted from a Caffe model, assuming the file format is Pickle.
#     """
#     # with open(fname, 'rb') as f:
#     #     weights = pickle.load(f)
#     # fname = "ps/scratch/rdanecek/FaceRecognition/resnet50_ft_weight.pkl"
#     fname = "ps/scratch/rdanecek/FaceRecognition/resnet_v1_50.ckpt"
#     print("## fname: ", fname)
#     # weights = torch.load(fname, map_location='cpu')['state_dict']
#     # 수정할 코드
#     weights = torch.load(fname, map_location='cpu', weights_only=False)['state_dict']
#     new_weights = {}
#     for k, v in weights.items():
#         if k.startswith('backbone'):
#             new_weights[k[9:]] = v.numpy()
#         else:
#             new_weights[k] = v.numpy()
#     own_state = model.state_dict()
    
#     for name, param in new_weights.items():
#         if name in own_state:
#             # try:
#             own_state[name].copy_(torch.from_numpy(param))
#             # except Exception:
#             #     raise RuntimeError(
#             #         'While copying the parameter named {}, whose dimensions in the model are {} and whose ' \
#             #         'dimensions in the checkpoint are {}.'.format(name, own_state[name].size(), param.size()))
#         else:
#             pass
#             #raise KeyError('unexpected key "{}" in state_dict'.format(name))


## https://github.com/cydonia999/VGGFace2-pytorch
class VGGFace2(nn.Module):
    def __init__(self, pretrained_data='vggface2'):
        super(VGGFace2, self).__init__()
        self.reg_model = resnet50(num_classes=8631, include_top=False).eval() #.cuda()
        # checkpoint = '/ps/scratch/face2d3d/ringnetpp/eccv/data/resnet50_ft_weight.pkl'
        checkpoint = '/ps/scratch/rdanecek/FaceRecognition/resnet50_ft_weight.pkl'
        load_state_dict(self.reg_model, checkpoint)
        self._freeze_layer(self.reg_model)

    def _freeze_layer(self, layer):
        for param in layer.parameters():
            param.requires_grad = False

    def forward(self, x):
        # out = []
        # margin=20
        # cropped_x = x[:,:,margin:224-margin,margin:224-margin]
        # x = F.interpolate(cropped_x*2. - 1., [160,160])
        # import ipdb; ipdb.set_trace()
        out = self.reg_model(x)
        # import ipdb; ipdb.set_trace()
        out = out.view(out.size(0), -1)
        return out  # , cropped_x
