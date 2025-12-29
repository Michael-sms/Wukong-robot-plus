# coding: utf-8
#!/usr/bin/env python3


"Tencent ASR && TTS API"
__author__ = "Charles Li, Joseph Pan"

import time
import uuid
import json
import random
import requests
import hmac
import base64
import urllib
import hashlib
# 步骤1: 导入腾讯云实时语音 SDK 依赖 (需先 pip install tencentcloud-sdk-python)
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.asr.v20190614 import asr_client, models

# 腾讯web API一句话识别请求
class tencentSpeech(object):
    __slots__ = (
        "SECRET_ID",
        "SECRET_KEY",
        "SourceType",
        "URL",
        "VoiceFormat",
        "PrimaryLanguage",
        "Text",
        "VoiceType",
        "Region",
    )

    def __init__(self, SECRET_KEY, SECRET_ID):
        self.SECRET_KEY, self.SECRET_ID = SECRET_KEY, SECRET_ID

    @property
    def secret_id(self):
        return self.SECRET_ID

    @secret_id.setter
    def secret_id(self, SECRET_ID):
        if not isinstance(SECRET_ID, str):
            raise ValueError("SecretId must be a string!")
        if len(SECRET_ID) == 0:
            raise ValueError("SecretId can not be empty!")
        self.SECRET_ID = SECRET_ID

    @property
    def secret_key(self):
        return self.SECRET_KEY

    @secret_key.setter
    def secret_key(self, SECRET_KEY):
        if not isinstance(SECRET_KEY, str):
            raise ValueError("SecretKey must be a string!")
        if len(SECRET_KEY) == 0:
            raise ValueError("SecretKey can not be empty!")
        self.SECRET_KEY = SECRET_KEY

    @property
    def source_type(self):
        return self.sourcetype

    @source_type.setter
    def source_type(self, SourceType):
        if not isinstance(SourceType, str):
            raise ValueError("SecretType must be an string!")
        if len(SourceType) == 0:
            raise ValueError("SourceType can not be empty!")
        self.SourceType = SourceType

    @property
    def url(self):
        return self.URL

    @url.setter
    def url(self, URL):
        if not isinstance(URL, str):
            raise ValueError("url must be an string!")
        if len(URL) == 0:
            raise ValueError("url can not be empty!")
        self.URL = URL

    @property
    def voiceformat(self):
        return self.VoiceFormat

    @voiceformat.setter
    def voiceformat(self, VoiceFormat):
        if not isinstance(VoiceFormat, str):
            raise ValueError("voiceformat must be an string!")
        if len(VoiceFormat) == 0:
            raise ValueError("voiceformat can not be empty!")
        self.VoiceFormat = VoiceFormat

    @property
    def text(self):
        return self.Text

    @text.setter
    def text(self, Text):
        if not isinstance(Text, str):
            raise ValueError("text must be an string!")
        if len(Text) == 0:
            raise ValueError("text can not be empty!")
        self.Text = Text

    @property
    def region(self):
        return self.Region

    @region.setter
    def region(self, Region):
        if not isinstance(Region, str):
            raise ValueError("region must be an string!")
        if len(Region) == 0:
            raise ValueError("region can not be empty!")
        self.Region = Region

    @property
    def primarylanguage(self):
        return self.PrimaryLanguage

    @primarylanguage.setter
    def primarylanguage(self, PrimaryLanguage):
        self.PrimaryLanguage = PrimaryLanguage

    @property
    def voicetype(self):
        return self.VoiceType

    @voicetype.setter
    def voicetype(self, VoiceType):
        self.VoiceType = VoiceType

    def TTS(self, text, voicetype, primarylanguage, region):
        self.text, self.voicetype, self.primarylanguage, self.region = (
            text,
            voicetype,
            primarylanguage,
            region,
        )
        return self.textToSpeech()

    def textToSpeech(self):
        # 生成body
        def make_body(config_dict, sign_encode):
            ##注意URL编码的时候分str编码，整段编码会丢data
            body = ""
            for a, b in config_dict:
                body += urllib.parse.quote(a) + "=" + urllib.parse.quote(str(b)) + "&"
            return body + "Signature=" + sign_encode

        HOST = "aai.tencentcloudapi.com"
        config_dict = {
            "Action": "TextToVoice",
            "Version": "2018-05-22",
            "ProjectId": 0,
            "Region": self.Region,
            "VoiceType": self.VoiceType,
            "Timestamp": int(time.time()),
            "Nonce": random.randint(100000, 200000),
            "SecretId": self.SECRET_ID,
            "Text": self.Text,
            "PrimaryLanguage": self.PrimaryLanguage,
            "ModelType": 1,
            "SessionId": uuid.uuid1(),
        }
        # 按key排序
        config_dict = sorted(config_dict.items())
        signstr = self.formatSignString(config_dict)
        sign_encode = urllib.parse.quote(self.encode_sign(signstr, self.SECRET_KEY))
        body = make_body(config_dict, sign_encode)
        # Get URL
        req_url = "https://aai.tencentcloudapi.com"
        header = {
            "Host": HOST,
            "Content-Type": "application/x-www-form-urlencoded",
            "Charset": "UTF-8",
        }
        request = requests.post(req_url, headers=header, data=body)
        # 有些音频utf8解码失败，存在编码错误
        s = request.content.decode("utf8", "ignore")
        return json.loads(s)

    def ASR(self, URL, voiceformat, sourcetype, region):
        self.url, self.voiceformat, self.source_type, self.region = (
            URL,
            voiceformat,
            sourcetype,
            region,
        )
        return self.oneSentenceRecognition()

    def oneSentenceRecognition(self):
        # 生成body
        def make_body(config_dict, sign_encode):
            ##注意URL编码的时候分str编码，整段编码会丢data
            body = ""
            for a, b in config_dict:
                body += urllib.parse.quote(a) + "=" + urllib.parse.quote(str(b)) + "&"
            return body + "Signature=" + sign_encode

        HOST = "aai.tencentcloudapi.com"
        config_dict = {
            "Action": "SentenceRecognition",
            "Version": "2018-05-22",
            "Region": self.Region,
            "ProjectId": 0,
            "SubServiceType": 2,
            "EngSerViceType": "16k",
            "VoiceFormat": self.VoiceFormat,
            "UsrAudioKey": random.randint(0, 20),
            "Timestamp": int(time.time()),
            "Nonce": random.randint(100000, 200000),
            "SecretId": self.SECRET_ID,
            "SourceType": self.SourceType,
        }
        if self.SourceType == "0":
            config_dict["Url"] = urllib.parse.quote(str(self.url))
        else:
            # 不能大于1M
            file_path = self.URL
            file = open(file_path, "rb")
            content = file.read()
            config_dict["DataLen"] = len(content)
            config_dict["Data"] = base64.b64encode(content).decode()
            # config_dict['Data'] = content
            file.close()
        # 按key排序
        config_dict = sorted(config_dict.items())
        signstr = self.formatSignString(config_dict)
        sign_encode = urllib.parse.quote(self.encode_sign(signstr, self.SECRET_KEY))
        body = make_body(config_dict, sign_encode)
        # Get URL
        req_url = "https://aai.tencentcloudapi.com"
        header = {
            "Host": HOST,
            "Content-Type": "application/x-www-form-urlencoded",
            "Charset": "UTF-8",
        }
        request = requests.post(req_url, headers=header, data=body)
        # 有些音频utf8解码失败，存在编码错误
        s = request.content.decode("utf8", "ignore")
        return s

    # 拼接url和参数
    def formatSignString(self, config_dict):
        signstr = "POSTaai.tencentcloudapi.com/?"
        argArr = []
        for a, b in config_dict:
            argArr.append(a + "=" + str(b))
        config_str = "&".join(argArr)
        return signstr + config_str

    # 生成签名
    def encode_sign(self, signstr, SECRET_KEY):
        myhmac = hmac.new(SECRET_KEY.encode(), signstr.encode(), digestmod="sha1")
        code = myhmac.digest()
        # hmac() 完一定要decode()和 python 2 hmac不一样
        signature = base64.b64encode(code).decode()
        return signature

class TencentSpeech(object):
    def __init__(self, appid, secret_id, secret_key, engine_model_type='16k_zh'):
        # ...existing code...
        self.appid = appid
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.engine_model_type = engine_model_type
        # 步骤2: 初始化实时识别客户端
        self.cred = credential.Credential(secret_id, secret_key)

    # 步骤3: 新增流式识别方法，实现“录音即传”
    def transcribe_stream(self, audio_chunk, seq, session_id, is_end=False):
        """
        流式识别接口
        :param audio_chunk: 二进制音频分片
        :param seq: 分片序号，从0开始
        :param session_id: 当前对话的唯一ID
        :param is_end: 是否为最后一片
        """
        try:
            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = asr_client.AsrClient(self.cred, "", clientProfile)

            req = models.CreateRecTaskRequest()
            # 这里使用腾讯实时语音识别接口参数
            params = {
                "EngineModelType": self.engine_model_type,
                "ChannelNum": 1,
                "ResType": 1,
                "InputSampleRate": 16000,
                "SourceType": 1, # 1: 语音数据
                "Data": base64.b64encode(audio_chunk).decode("utf-8"),
                "DataLen": len(audio_chunk),
                "Seq": seq,
                "End": 1 if is_end else 0,
                "VoiceId": session_id
            }
            req.from_json_string(json.dumps(params))
            
            # [新增] 2. 记录请求开始时间
            t_start = time.time()

            # 发起网络请求
            resp = client.SentenceRecognition(req) 
            
            # [新增] 3. 记录请求结束时间并计算延迟
            t_end = time.time()
            latency = (t_end - t_start) * 1000  # 转换为毫秒

            result = json.loads(resp.to_json_string())
            text = result.get("Result", "")
            
            # 语义预测逻辑
            is_final = False
            if "。" in text or "？" in text or "！" in text:
                is_final = True 

            # [新增] 4. 输出性能日志
            # 仅在检测到句子结束(is_final)或流结束(is_end)时打印，避免刷屏
            if is_final or is_end:
                logger.info(f"[前端感知优化] ASR响应延迟: {latency:.2f}ms | 识别结果: {text}")
                if latency < 200:
                    logger.info("[前端感知优化] ✅ 达标 (延迟 < 200ms)")
                else:
                    logger.warning("[前端感知优化] ⚠️ 未达标 (延迟 > 200ms)")
            # 在你的功能代码中添加
            print("DEBUG: 成员1的功能已触发")
                
            return text, is_final

        except Exception as e:
            logger.error(f"Tencent RASR error: {e}")
            return "", True
        # 在你的功能代码中添加
        print("DEBUG: 成员1的功能已触发")
    