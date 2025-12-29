# -*- coding: utf-8 -*-
import os
import json
import torch
import torchaudio
import numpy as np
import faiss
from speechbrain.pretrained import EncoderClassifier
from robot import logging, config, utils

logger = logging.getLogger(__name__)

class SpeakerEncoder(object):
    def __init__(self, db_path='static/user_db.json', model_source="speechbrain/spkrec-ecapa-voxceleb"):
        """
        初始化声纹识别模块
        :param db_path: 用户画像数据库路径
        :param model_source: HuggingFace 模型路径 (ECAPA-TDNN)
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"正在加载声纹模型 ECAPA-TDNN (Device: {self.device})...")
        
        # 1. 加载 ECAPA-TDNN 预训练模型
        # 注意：第一次运行会自动下载模型到 ~/.cache/speechbrain
        try:
            self.classifier = EncoderClassifier.from_hparams(
                source=model_source, 
                run_opts={"device": self.device}
            )
            logger.info("声纹模型加载完成")
        except Exception as e:
            logger.error(f"声纹模型加载失败: {e}")
            self.classifier = None

        # 2. 初始化向量数据库 (Faiss)
        self.dimension = 192  # ECAPA-TDNN 输出维度
        self.index = faiss.IndexFlatIP(self.dimension)  # 使用内积 (Inner Product) 计算余弦相似度
        
        # 3. 加载用户数据
        self.db_path = db_path
        self.users = [] # 存储用户元数据 [{'id': 'u1', 'name': '三石', 'context': {...}}]
        self.load_database()

    def load_database(self):
        """加载本地用户数据库并重建 Faiss 索引"""
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return

        with open(self.db_path, 'r', encoding='utf-8') as f:
            self.users = json.load(f)
        
        # 重建索引
        if self.users:
            vectors = []
            for user in self.users:
                if 'embedding' in user:
                    vectors.append(np.array(user['embedding'], dtype='float32'))
            
            if vectors:
                matrix = np.vstack(vectors)
                faiss.normalize_L2(matrix) # 归一化以进行余弦相似度计算
                self.index.add(matrix)
                logger.info(f"已加载 {self.index.ntotal} 个用户声纹数据")

    def preprocess_audio(self, audio_data):
        """
        将原始 PCM 音频流转换为模型所需的 Tensor
        :param audio_data: bytes (16k, 16bit, mono)
        """
        # 将 bytes 转为 numpy float32
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        # 归一化到 [-1, 1]
        audio_np = audio_np / 32768.0
        # 转为 Tensor 并增加 batch 维度
        signal = torch.tensor(audio_np).unsqueeze(0).to(self.device)
        return signal

    def extract_embedding(self, audio_data):
        """提取声纹特征向量"""
        if self.classifier is None:
            return None
        
        with torch.no_grad():
            signal = self.preprocess_audio(audio_data)
            # 提取 embedding
            embeddings = self.classifier.encode_batch(signal)
            # 转换为 numpy (1, 192)
            vector = embeddings.squeeze().cpu().numpy().reshape(1, -1).astype('float32')
            return vector

    def identify(self, audio_data, threshold=0.25):
        """
        声纹识别核心逻辑
        :param audio_data: 语音流数据
        :param threshold: 余弦相似度阈值 (0.25-0.4 适用于 ECAPA-TDNN)
        :return: (user_info, score) 或 (None, 0)
        """
        vector = self.extract_embedding(audio_data)
        if vector is None or self.index.ntotal == 0:
            return None, 0

        # 归一化查询向量
        faiss.normalize_L2(vector)
        
        # 检索 Top-1
        D, I = self.index.search(vector, 1)
        score = D[0][0]
        user_idx = I[0][0]

        if score > threshold and user_idx != -1:
            user = self.users[user_idx]
            logger.info(f"声纹匹配成功: {user['name']} (相似度: {score:.2f})")
            # 返回用户画像 Context
            return user, score
        else:
            logger.debug(f"声纹未匹配 (最高相似度: {score:.2f})")
            return None, score

    def register_user(self, audio_data, user_id, name, anime_context):
        """
        注册新用户声纹
        :param anime_context: 动漫角色偏好配置，例如 {'role': '傲娇', 'fav_char': 'Asuka'}
        """
        vector = self.extract_embedding(audio_data)
        if vector is None:
            return False

        # 归一化并存入 Faiss (内存)
        vector_norm = vector.copy()
        faiss.normalize_L2(vector_norm)
        self.index.add(vector_norm)

        # 存入数据库 (文件)
        user_profile = {
            'id': user_id,
            'name': name,
            'context': anime_context,
            'embedding': vector.tolist()[0] # 存储原始向量
        }
        self.users.append(user_profile)
        
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False)
        
        logger.info(f"用户 {name} 注册成功")
        return True