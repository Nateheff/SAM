import numpy as np
import torch
import torch.nn.functional as F
import time
import torchvision


def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = torch.zeros_like(x) if isinstance(x, torch.Tensor) else np.zeros_like(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y


def non_max_suppression(prediction, conf_thres=0.3, iou_thres=0.45, classes=None):
    """Performs Non-Maximum Suppression (NMS) on inference results
    Returns:
         detections with shape: nx6 (x1, y1, x2, y2, conf, cls)
    """

    nc = prediction.shape[2] - 5  # number of classes

    # Settings
    # (pixels) minimum and maximum box width and height
    max_wh = 4096
    max_det = 300  # maximum number of detections per image
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 1.0  # seconds to quit after
    multi_label = nc > 1  # multiple labels per box (adds 0.5ms/img)

    t = time.time()
    output = [torch.zeros((0, 6), device="cpu")] * prediction.shape[0]

    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[x[..., 4] > conf_thres]  # confidence

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box (center x, center y, width, height) to (x1, y1, x2, y2)
        box = xywh2xyxy(x[:, :4])

        # Detections matrix nx6 (xyxy, conf, cls)
        conf, j = x[:, 5:].max(1, keepdim=True)
        x = torch.cat((box, conf, j.float()), 1)[conf.view(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        elif n > max_nms:  # excess boxes
            # sort by confidence
            x = x[x[:, 4].argsort(descending=True)[:max_nms]]

        # Batched NMS
        c = x[:, 5:6] * max_wh  # classes
        # boxes (offset by class), scores
        boxes, scores = x[:, :4] + c, x[:, 4]
        i = torchvision.ops.nms(boxes, scores, iou_thres)  # NMS
        if i.shape[0] > max_det:  # limit detections
            i = i[:max_det]

        output[xi] = x[i].detach().cpu()

        if (time.time() - t) > time_limit:
            print(f'WARNING: NMS time limit {time_limit}s exceeded')
            break  # time limit exceeded

    return output


def make_grid(h, w, device):
    hv, wv = torch.meshgrid([torch.arange(h), torch.arange(w)])
    return torch.stack((wv, hv), 2).repeat(1,1,3).reshape(h, w, 3, -1).to(device)


def handel_preds(preds, device):
    #加载anchor配置
    anchors=[12.64,19.39, 37.88,51.48, 55.71,138.31, 126.91,78.23, 131.57,214.55, 279.92,258.87]
    anchors = np.array(anchors)
    anchors = torch.from_numpy(anchors.reshape(len(preds) // 3, 3, 2)).to(device)

    output_bboxes = []
    layer_index = [0, 0, 0, 1, 1, 1]

    for i in range(len(preds) // 3):
        bacth_bboxes = []
        reg_preds = preds[i * 3]
        obj_preds = preds[(i * 3) + 1]
        cls_preds = preds[(i * 3) + 2]

        for r, o, c in zip(reg_preds, obj_preds, cls_preds):
            r = r.permute(1, 2, 0)
            r = r.reshape(r.shape[0], r.shape[1], 3, -1)

            o = o.permute(1, 2, 0)
            o = o.reshape(o.shape[0], o.shape[1], 3, -1)

            c = c.permute(1, 2, 0)
            c = c.reshape(c.shape[0],c.shape[1], 1, c.shape[2])
            c = c.repeat(1, 1, 3, 1)

            anchor_boxes = torch.zeros(r.shape[0], r.shape[1], r.shape[2], r.shape[3] + c.shape[3] + 1)

            #计算anchor box的cx, cy
            grid = make_grid(r.shape[0], r.shape[1], device)
            stride = 352 /  r.shape[0]
            anchor_boxes[:, :, :, :2] = ((r[:, :, :, :2].sigmoid() * 2. - 0.5) + grid) * stride

            #计算anchor box的w, h
            anchors_cfg = anchors[i]
            anchor_boxes[:, :, :, 2:4] = (r[:, :, :, 2:4].sigmoid() * 2) ** 2 * anchors_cfg # wh

            #计算obj分数
            anchor_boxes[:, :, :, 4] = o[:, :, :, 0].sigmoid()

            #计算cls分数
            anchor_boxes[:, :, :, 5:] = F.softmax(c[:, :, :, :], dim = 3)

            #torch tensor 转为 numpy array
            anchor_boxes = anchor_boxes.cpu().detach().numpy() 
            bacth_bboxes.append(anchor_boxes)     

        #n, anchor num, h, w, box => n, (anchor num*h*w), box
        bacth_bboxes = torch.from_numpy(np.array(bacth_bboxes))
        bacth_bboxes = bacth_bboxes.view(bacth_bboxes.shape[0], -1, bacth_bboxes.shape[-1]) 

        output_bboxes.append(bacth_bboxes)    
        
    #merge
    output = torch.cat(output_bboxes, 1)
            
    return output