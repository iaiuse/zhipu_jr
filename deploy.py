#!/usr/bin/env python3
# deploy.py
import click
import subprocess
import os
import time
from typing import Optional

class Deployer:
    def __init__(self, environment: str):
        self.environment = environment
        self.docker_compose_file = f"docker-compose.{environment}.yml"
    
    def check_prerequisites(self):
        """检查部署前提条件"""
        required_commands = ['docker', 'docker-compose', 'wrangler']
        for cmd in required_commands:
            try:
                subprocess.run([cmd, '--version'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                raise Exception(f"Missing required command: {cmd}")

    def build_images(self):
        """构建Docker镜像"""
        click.echo("Building Docker images...")
        subprocess.run([
            'docker-compose',
            '-f', self.docker_compose_file,
            'build'
        ], check=True)

    def deploy_containers(self):
        """部署Docker容器"""
        click.echo("Deploying containers...")
        subprocess.run([
            'docker-compose',
            '-f', self.docker_compose_file,
            'up', '-d'
        ], check=True)

    def deploy_to_cloudflare(self):
        """部署到Cloudflare"""
        if self.environment == 'production':
            click.echo("Deploying to Cloudflare...")
            subprocess.run(['wrangler', 'publish'], check=True)

    def run_migrations(self):
        """运行数据库迁移"""
        click.echo("Running migrations...")
        # 实现数据库迁移逻辑

    def run_health_check(self) -> bool:
        """运行健康检查"""
        click.echo("Running health checks...")
        try:
            result = subprocess.run([
                'curl', 'http://localhost:8501/healthz'
            ], check=True, capture_output=True)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def rollback(self):
        """回滚部署"""
        click.echo("Rolling back deployment...")
        subprocess.run([
            'docker-compose',
            '-f', self.docker_compose_file,
            'down'
        ], check=True)

@click.command()
@click.option('--environment', type=click.Choice(['dev', 'prod']), default='dev')
@click.option('--skip-build', is_flag=True)
@click.option('--skip-migrations', is_flag=True)
def deploy(environment: str, skip_build: bool, skip_migrations: bool):
    """部署应用"""
    deployer = Deployer(environment)

    try:
        # 检查前提条件
        deployer.check_prerequisites()

        # 构建镜像
        if not skip_build:
            deployer.build_images()

        # 部署容器
        deployer.deploy_containers()

        # 运行迁移
        if not skip_migrations:
            deployer.run_migrations()

        # 部署到Cloudflare
        if environment == 'prod':
            deployer.deploy_to_cloudflare()

        # 健康检查
        retries = 3
        while retries > 0:
            if deployer.run_health_check():
                click.echo("Deployment successful!")
                break
            retries -= 1
            time.sleep(10)
        else:
            raise Exception("Health check failed")

    except Exception as e:
        click.echo(f"Deployment failed: {str(e)}")
        deployer.rollback()
        raise

if __name__ == '__main__':
    deploy()