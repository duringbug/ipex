import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from tqdm import tqdm  # 导入 tqdm 库来显示进度条

def generate_normal_random(mean: float, std_dev: float) -> float:
    u, v = 0, 0
    while u == 0:
        u = np.random.rand()  # Converting [0,1) to (0,1)
    while v == 0:
        v = np.random.rand()
    normal = np.sqrt(-2.0 * np.log(u)) * np.cos(2.0 * np.pi * v)
    return mean + normal * std_dev

def get_centroids_by_normal_random(image_data: np.ndarray, iterations: int) -> np.ndarray:
    centroids = []
    for _ in tqdm(range(iterations), desc='Generating centroids', position=0, leave=True):
        rgba = []
        for _ in range(4):
            random_value = generate_normal_random(127.5, 63.75)  # 使用正态分布随机数生成 RGBA 分量
            random_value = np.round(np.clip(random_value, 0, 255))  # 确保值在 0 到 255 之间
            rgba.append(random_value)
        centroids.append(rgba)
    return np.array(centroids)

def get_centroids_by_random(image_data: np.ndarray, iterations: int) -> np.ndarray:
    num_pixels = len(image_data) // 4  # 图像中像素的数量
    centroids = []
    for _ in tqdm(range(iterations), desc='Generating centroids', position=0, leave=True):
        random_index = np.random.randint(num_pixels)  # 随机选择一个像素索引
        pixel_index = random_index * 4  # 转换为 image_data 中 RGBA 数据的起始索引
        centroids.append([
            image_data[pixel_index],
            image_data[pixel_index + 1],
            image_data[pixel_index + 2],
            image_data[pixel_index + 3]
        ])
    return np.array(centroids)

def generate_poisson_random(mean: float, max_value: int) -> int:
    # Generate a Poisson-distributed integer within the range [0, max_value - 1]
    poisson_value = np.random.poisson(mean)
    return min(poisson_value, max_value - 1)

def get_centroids_by_poisson(image_data: np.ndarray, iterations: int) -> np.ndarray:
    num_pixels = len(image_data) // 4  # 图像中像素的数量
    centroids = []
    for _ in tqdm(range(iterations), desc='Generating centroids', position=0, leave=True):
        random_index = generate_poisson_random(num_pixels - 1, num_pixels)  # 用柏松分布生成一个像素索引，确保不超过最大索引
        pixel_index = random_index * 4  # 转换为 image_data 中 RGBA 数据的起始索引
        
        centroids.append([
            image_data[pixel_index],
            image_data[pixel_index + 1],
            image_data[pixel_index + 2],
            image_data[pixel_index + 3]
        ])
    return np.array(centroids)

def calculate_distance(rgba1, rgba2):
    """计算两个 RGBA 值之间的欧氏距离"""
    squared_dist = sum((a - b) ** 2 for a, b in zip(rgba1, rgba2))
    return squared_dist ** 0.5

def calculate_manhattan_distance(rgba1, rgba2):
    """计算两个 RGBA 值之间的曼哈顿距离"""
    manhattan_dist = sum(abs(a - b) for a, b in zip(rgba1, rgba2))
    return manhattan_dist

def calculate_squared_error(image_data, clusters, centroids):
    sse = 0.0
    num_clusters = len(clusters)

    for cluster_index in tqdm(range(num_clusters), desc='Calculate squared error', position=0, leave=True):
        centroid = centroids[cluster_index]
        cluster_points = clusters[cluster_index]
        num_points = len(cluster_points)
        sse_cluster = 0.0

        if num_points > 0:
            for pixel_index in cluster_points:
                rgba = [
                    image_data[pixel_index * 4],         # Red
                    image_data[pixel_index * 4 + 1],     # Green
                    image_data[pixel_index * 4 + 2],     # Blue
                    image_data[pixel_index * 4 + 3]      # Alpha
                ]

                try:
                    distance = calculate_distance(rgba, centroid)
                except Exception as e:
                    print(f"Error calculating distance for pixel_index {pixel_index} in cluster {cluster_index}")
                    print(f"RGBA: {rgba}, Centroid: {centroid}")
                    print(f"centroids: {centroids}")
                    raise
                sse_cluster += distance 

            # Calculate average squared error for the current cluster
            sse_cluster /= num_points
            sse += sse_cluster

    return sse/num_clusters

def k_means(image_data, iterations):
    num_pixels = len(image_data) // 4
    pixel_indices = list(range(num_pixels))

    # 随机选择 'iterations' 个聚类中心
    centroids = get_centroids_by_random(image_data, iterations)
    clusters = [[] for _ in range(iterations)]  # 初始化每个聚类

    # 将每个像素分配到最近的聚类中心
    for pixel_index in tqdm(pixel_indices, desc='k_means: Assigning pixels to clusters', position=0, leave=True):
        rgba = [
            image_data[pixel_index * 4],         # Red
            image_data[pixel_index * 4 + 1],     # Green
            image_data[pixel_index * 4 + 2],     # Blue
            image_data[pixel_index * 4 + 3]      # Alpha
        ]

        min_distance = float('inf')
        cluster_index = -1

        for index, centroid in enumerate(centroids):
            distance = calculate_manhattan_distance(rgba, centroid)     
            if distance < min_distance:
                min_distance = distance
                cluster_index = index

        clusters[cluster_index].append(pixel_index)

    print(f'squared error: {calculate_squared_error(image_data,clusters,centroids)}')

    return clusters

# 使用torch计算平方误差
def calculate_squared_error_02(image_data, clusters, centroids):
    sse = 0.0
    num_clusters = len(clusters)
    count = 0.0

    for cluster_index in range(num_clusters):
        centroid = centroids[cluster_index]
        cluster_points = clusters[cluster_index]
        num_points = len(cluster_points)
        sse_cluster = 0.0

        if num_points > 0:
            count = count + 1
            for pixel_index in cluster_points:
                rgba = torch.tensor([
                    image_data[pixel_index * 4],         # Red
                    image_data[pixel_index * 4 + 1],     # Green
                    image_data[pixel_index * 4 + 2],     # Blue
                    image_data[pixel_index * 4 + 3]      # Alpha
                ], dtype=torch.float32)

                distance = calculate_distance(rgba, centroid)
                sse_cluster += distance

            sse_cluster /= num_points
            sse += sse_cluster

    return sse / count, count

# 定义神经网络模型
def save_model(model, epoch, optimizer, path="model.pth"):
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }, path)

def load_model(model, optimizer, path="model.pth"):
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch = checkpoint['epoch']
    return model, optimizer, epoch

class FeatureExtractor(nn.Module):
    def __init__(self, input_dim=128, feature_dim=4, iterations=20):
        super(FeatureExtractor, self).__init__()
        self.input_dim = input_dim
        self.feature_dim = feature_dim
        self.iterations = iterations
        
        # Initial cut points for RGB channels
        self.r_cut = nn.Parameter(torch.rand(11))  # Initialize with random values in [0, 1)
        self.g_cut = nn.Parameter(torch.rand(11))
        self.b_cut = nn.Parameter(torch.rand(11))
        
    def transform_cuts(self):
        # Ensure the cuts are in increasing order and within [0, 1]
        sorted_r_cut = torch.sort(self.r_cut.data)[0].clamp(0.0, 1.0)
        sorted_g_cut = torch.sort(self.g_cut.data)[0].clamp(0.0, 1.0)
        sorted_b_cut = torch.sort(self.b_cut.data)[0].clamp(0.0, 1.0)
        
        # Set the first and last elements explicitly
        sorted_r_cut[0] = 0.0
        sorted_r_cut[-1] = 1.0
        sorted_g_cut[0] = 0.0
        sorted_g_cut[-1] = 1.0
        sorted_b_cut[0] = 0.0
        sorted_b_cut[-1] = 1.0
        
        # Assign back to the parameters
        self.r_cut.data = sorted_r_cut
        self.g_cut.data = sorted_g_cut
        self.b_cut.data = sorted_b_cut

    def forward(self, x):
        self.transform_cuts() 

        x = x.view(self.input_dim, self.feature_dim)
        
        # Calculate RGBA values
        r_values = x[:, 0].contiguous()
        g_values = x[:, 1].contiguous()
        b_values = x[:, 2].contiguous()
        
        # Apply cuts to determine intervals
        expanded_r_cut = self.r_cut.unsqueeze(0).unsqueeze(0).contiguous() * 255
        expanded_g_cut = self.g_cut.unsqueeze(0).unsqueeze(0).contiguous() * 255
        expanded_b_cut = self.b_cut.unsqueeze(0).unsqueeze(0).contiguous() * 255


        # 在最后一个维度上求和，得到每个像素符合条件的区间数量
        r_intervals = torch.searchsorted(expanded_r_cut.squeeze(), r_values)
        g_intervals = torch.searchsorted(expanded_g_cut.squeeze(), g_values)
        b_intervals = torch.searchsorted(expanded_b_cut.squeeze(), b_values)


        counts = torch.zeros((len(self.r_cut), len(self.g_cut), len(self.b_cut)), dtype=torch.float32, requires_grad=True)
        counts = counts.clone() 

        for r, g, b in zip(r_intervals.flatten(), g_intervals.flatten(), b_intervals.flatten()):
            counts[r - 1, g - 1, b - 1] += 1

        flat_counts = counts.flatten()
        sorted_indices = torch.argsort(flat_counts, descending=True)

        # 获取排序后的 top iterations 个索引
        top_indices = sorted_indices[:2 * self.iterations]

        # 根据 top_indices 获取对应的 r_intervals, g_intervals, b_intervals 的展平后索引
        r_flat_indices = r_intervals.flatten()
        g_flat_indices = g_intervals.flatten()
        b_flat_indices = b_intervals.flatten()

        num_r = len(self.r_cut)
        num_g = len(self.g_cut)
        num_b = len(self.b_cut)

        top_r_indices = (top_indices // (num_g * num_b)) % num_r
        top_g_indices = (top_indices // num_b) % num_g
        top_b_indices = top_indices % num_b

        # 获取对应的 r, g, b 值
        top_r_values = top_r_indices + 1  # 加一是因为 r_intervals 索引是从 1 开始的
        top_g_values = top_g_indices + 1
        top_b_values = top_b_indices + 1

        # 初始化 unique_results 为一个空张量
        unique_results = torch.empty((0, 3), dtype=torch.float32, requires_grad=True)

        seen_rgb = set()

        # 合并 top_r_values, top_g_values, top_b_values 成一个张量
        rgb_values = torch.stack([top_r_values, top_g_values, top_b_values], dim=1)

        # 遍历每个 RGB 值
        for rgb in rgb_values:
            rgb_tuple = tuple(rgb.tolist())  # 转换为元组
            if rgb_tuple not in seen_rgb:
                seen_rgb.add(rgb_tuple)
                unique_results = torch.cat((unique_results, rgb.unsqueeze(0)), dim=0)
            if len(unique_results) == self.iterations:  # 达到指定数量后退出循环
                break

        # 输出结果
        output = torch.zeros((len(unique_results), 4), dtype=torch.float32, requires_grad=True)
        output = output.clone()
        for idx, (r, g, b) in enumerate(unique_results):
            r = r.long() - 1
            g = g.long() - 1
            b = b.long() - 1
            r = torch.clamp(r, 0, len(self.r_cut) - 2)
            g = torch.clamp(g, 0, len(self.g_cut) - 2)
            b = torch.clamp(b, 0, len(self.b_cut) - 2)
            r_value = (255 * r) / len(self.r_cut) + (self.r_cut[r + 1].item() - self.r_cut[r].item()) * 255 / 2
            g_value = (255 * g) / len(self.g_cut) + (self.g_cut[g + 1].item() - self.g_cut[g].item()) * 255 / 2
            b_value = (255 * b) / len(self.b_cut) + (self.b_cut[b + 1].item() - self.b_cut[b].item()) * 255 / 2
            a_value = 255.0 
            output[idx] = torch.tensor([r_value, g_value, b_value, a_value])

        return output

# 定义数据集
class ImageDataset(Dataset):
    def __init__(self, image_data):
        self.image_data = torch.tensor(image_data, dtype=torch.float32)
    
    def __len__(self):
        return len(self.image_data) // 4
    
    def __getitem__(self, idx):
        rgba = self.image_data[idx * 4:(idx + 1) * 4]
        return rgba

def k_means_with_convergence(image_data, iterations, width, height, lambda_val, offset, max_depth):
    avg_centroids = None
    clusters = None
    num_pixels = len(image_data) // 4
    pixel_indices = np.arange(num_pixels)

    # 将图像数据封装成数据集
    dataset = ImageDataset(image_data)

    # 训练神经网络模型
    num_epochs = 1
    batch_size = 1024  # 调整为适当的批大小
    # 定义神经网络模型和优化器
    model = FeatureExtractor(input_dim=batch_size,feature_dim=4,iterations = iterations)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    output_centroids = []

    if os.path.exists("final_model.pth"):
        model, optimizer, start_epoch = load_model(model, optimizer, path="final_model.pth")
        print("Model loaded. Skipping training.")
    else:
        for epoch in range(num_epochs):
            for batch_idx, batch in enumerate(tqdm(dataloader, desc=f'Epoch {epoch+1}/{num_epochs}', leave=False)):
            # for batch_idx, batch in enumerate(dataloader):
                optimizer.zero_grad()
                output_centroids = model(batch)

                # 计算每列的均值
                # avg_centroids = output_centroids.mean(dim=0)
                # 假设输出的形状为 (batch_size, iterations, 4)

                # 清空 clusters 列表
                clusters = [[] for _ in range(iterations)]

                # 将像素分配到最近的聚类中心
                for idx in range(batch_size):
                    rgba_list = batch[idx]
                    min_distance = float('inf')
                    cluster_index = -1
                    for i, centroid in enumerate(output_centroids):
                        distance = calculate_manhattan_distance(rgba_list, centroid)
                        if distance < min_distance:
                            min_distance = distance
                            cluster_index = i
                    clusters[cluster_index].append(pixel_indices[idx])

                # 计算损失并进行反向传播
                loss, count = calculate_squared_error_02(image_data, clusters, output_centroids)
                loss.backward()

                # 每当 batch_idx 是 100 的整数倍时，打印损失
                if (batch_idx + 1) % 10 == 0:
                    print(f'avg_centroids: {output_centroids}')
                    print(f'Batch [{batch_idx + 1}/{len(dataloader)}], Loss: {loss.item()}, Count: {count}')

                optimizer.step()
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

        save_model(model, epoch, optimizer, path="final_model.pth")

    clusters = [[] for _ in range(iterations)]
    image_data_tensor = torch.tensor(image_data, dtype=torch.float32).view(-1, 4)
    print(image_data_tensor.shape)
    num_rows = image_data_tensor.size(0)
    random_indices = torch.randperm(num_rows)[:batch_size]
    random_pixels = image_data_tensor[random_indices]
    print(random_pixels.shape)
    # 将挑选的像素输入到 model 中
    output_centroids = model(random_pixels)
    output_centroids = output_centroids.round().long()
    output_centroids_np = output_centroids.cpu().numpy()
    # 将每个像素分配到最近的聚类中心
    for pixel_index in tqdm(pixel_indices, desc='k_means: Assigning pixels to clusters', position=0, leave=True):
        rgba = [
            round(image_data[pixel_index * 4]),         # Red
            round(image_data[pixel_index * 4 + 1]),     # Green
            round(image_data[pixel_index * 4 + 2]),     # Blue
            round(image_data[pixel_index * 4 + 3])      # Alpha
        ]

        min_distance = float('inf')
        cluster_index = -1

        for index, centroid in enumerate(output_centroids_np):
            distance = calculate_manhattan_distance(rgba, centroid)     
            if distance < min_distance:
                min_distance = distance
                cluster_index = index

        clusters[cluster_index].append(int(pixel_index))
    print(f'squared error: {calculate_squared_error(image_data,clusters,output_centroids_np)}')

    return clusters

