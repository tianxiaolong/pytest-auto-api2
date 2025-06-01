# pytest-auto-api2 Docker镜像
# 基于Python 3.9的轻量级镜像

FROM python:3.9-slim

# 设置维护者信息
LABEL maintainer="pytest-auto-api2 team"
LABEL description="企业级接口自动化测试框架"
LABEL version="2.0"

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装Java（Allure需要）
RUN apt-get update && apt-get install -y openjdk-11-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# 安装Allure
RUN wget -O allure.tgz https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.tgz \
    && tar -zxf allure.tgz \
    && mv allure-2.24.0 /opt/allure \
    && ln -s /opt/allure/bin/allure /usr/local/bin/allure \
    && rm allure.tgz

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install pytest-xdist pytest-html pytest-cov

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p logs report/tmp report/html data/yaml_data data/excel_data

# 设置权限
RUN chmod +x run.py

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# 暴露端口
EXPOSE 8080

# 默认命令
CMD ["python", "run.py"]
