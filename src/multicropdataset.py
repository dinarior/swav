
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from logging import getLogger

import cv2

import numpy as np
import torchvision.datasets as datasets
import torchvision.transforms as transforms

logger = getLogger()


class MultiCropDataset(datasets.CIFAR100):
    def __init__(
        self,
        data_path,
        size_crops,
        nmb_crops,
        min_scale_crops,
        max_scale_crops,
        size_dataset=-1,
        return_index=False,
    ):
        super(MultiCropDataset, self).__init__(data_path,download=True,train = True)
        assert len(size_crops) == len(nmb_crops)
        assert len(min_scale_crops) == len(nmb_crops)
        assert len(max_scale_crops) == len(nmb_crops)
        if size_dataset >= 0:
            self.samples = self.samples[:size_dataset]
        self.return_index = return_index

        trans = []
        color_transform = transforms.Compose([get_color_distortion(), RandomGaussianBlur()])
        mean = [0.4914, 0.4822, 0.4465]
        std = [0.2023, 0.1994, 0.2010]
        for i in range(len(size_crops)):
            randomresizedcrop = transforms.RandomResizedCrop(
                size_crops[i],
                scale=(min_scale_crops[i], max_scale_crops[i]),
            )
            trans.extend([transforms.Compose([
                randomresizedcrop,
                transforms.RandomHorizontalFlip(p=0.5),
                color_transform,
                transforms.ToTensor(),
                transforms.Normalize(mean=mean, std=std)])
            ] * nmb_crops[i])
        self.trans = trans

    def __getitem__(self, index):
        # path, _ = self.samples[index]
        # image = self.loader(path)
        image,target = super(MultiCropDataset,self).__getitem__(index)
        multi_crops = list(map(lambda trans: trans(image), self.trans))
        if self.return_index:
            return index, multi_crops
        return multi_crops


class RandomGaussianBlur(object):
    def __call__(self, img):
        do_it = np.random.rand() > 0.5
        if not do_it:
            return img
        sigma = np.random.rand() * 1.9 + 0.1
        return cv2.GaussianBlur(np.asarray(img), (23, 23), sigma)


def get_color_distortion(s=1.0):
    # s is the strength of color distortion.
    color_jitter = transforms.ColorJitter(0.8*s, 0.8*s, 0.8*s, 0.2*s)
    rnd_color_jitter = transforms.RandomApply([color_jitter], p=0.8)
    rnd_gray = transforms.RandomGrayscale(p=0.2)
    color_distort = transforms.Compose([rnd_color_jitter, rnd_gray])
    return color_distort





















# # Copyright (c) Facebook, Inc. and its affiliates.
# # All rights reserved.
# #
# # This source code is licensed under the license found in the
# # LICENSE file in the root directory of this source tree.
# #

# from logging import getLogger

# import cv2

# import numpy as np
# import torchvision.datasets as datasets
# import torchvision.transforms as transforms

# logger = getLogger()


# class MultiCropDataset(datasets.ImageFolder):
#     def __init__(
#         self,
#         data_path,
#         size_crops,
#         nmb_crops,
#         min_scale_crops,
#         max_scale_crops,
#         size_dataset=-1,
#         return_index=False,
#     ):
#         super(MultiCropDataset, self).__init__(data_path)
#         assert len(size_crops) == len(nmb_crops)
#         assert len(min_scale_crops) == len(nmb_crops)
#         assert len(max_scale_crops) == len(nmb_crops)
#         if size_dataset >= 0:
#             self.samples = self.samples[:size_dataset]
#         self.return_index = return_index

#         trans = []
#         color_transform = transforms.Compose([get_color_distortion(), RandomGaussianBlur()])
#         mean = [0.485, 0.456, 0.406]
#         std = [0.228, 0.224, 0.225]
#         for i in range(len(size_crops)):
#             randomresizedcrop = transforms.RandomResizedCrop(
#                 size_crops[i],
#                 scale=(min_scale_crops[i], max_scale_crops[i]),
#             )
#             trans.extend([transforms.Compose([
#                 randomresizedcrop,
#                 transforms.RandomHorizontalFlip(p=0.5),
#                 color_transform,
#                 transforms.ToTensor(),
#                 transforms.Normalize(mean=mean, std=std)])
#             ] * nmb_crops[i])
#         self.trans = trans

#     def __getitem__(self, index):
#         path, _ = self.samples[index]
#         image = self.loader(path)
#         multi_crops = list(map(lambda trans: trans(image), self.trans))
#         if self.return_index:
#             return index, multi_crops
#         return multi_crops


# class RandomGaussianBlur(object):
#     def __call__(self, img):
#         do_it = np.random.rand() > 0.5
#         if not do_it:
#             return img
#         sigma = np.random.rand() * 1.9 + 0.1
#         return cv2.GaussianBlur(np.asarray(img), (23, 23), sigma)


# def get_color_distortion(s=1.0):
#     # s is the strength of color distortion.
#     color_jitter = transforms.ColorJitter(0.8*s, 0.8*s, 0.8*s, 0.2*s)
#     rnd_color_jitter = transforms.RandomApply([color_jitter], p=0.8)
#     rnd_gray = transforms.RandomGrayscale(p=0.2)
#     color_distort = transforms.Compose([rnd_color_jitter, rnd_gray])
#     return color_distort


# python -m torch.distributed.launch --nproc_per_node=2 main_swav.py \
# --data_path ./cifar \
# --epochs 400 \
# --base_lr 0.6 \
# --final_lr 0.0006 \
# --warmup_epochs 0 \
# --batch_size 32 \
# --size_crops 224 96 \
# --nmb_crops 2 6 \
# --min_scale_crops 0.14 0.05 \
# --max_scale_crops 1. 0.14 \
# --use_fp16 true \
# --freeze_prototypes_niters 5005 \
# --queue_length 3840 \
# --epoch_queue_starts 15