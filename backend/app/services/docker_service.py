"""
Docker Service - Core Engine for Agent Management
Handles container lifecycle, resource enforcement, log streaming, health checks
"""

import docker
import logging
from typing import Optional, Dict, List
from docker.errors import APIError, ImageNotFound
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class DockerService:
    """Manages Docker containers for AI agents"""

    def __init__(self):
        self.client = docker.from_env()
        self.network_name = "agentnest"
        self._ensure_network()

    def _ensure_network(self):
        """Ensure AgentNest network exists"""
        try:
            self.client.networks.get(self.network_name)
        except docker.errors.NotFound:
            self.client.networks.create(self.network_name, driver="bridge")
            logger.info(f"Created network: {self.network_name}")

    def deploy_agent(
        self,
        agent_id: int,
        user_id: int,
        docker_image: str,
        name: str,
        cpu_limit: float = 1.0,
        memory_limit_mb: int = 512,
        environment: Optional[Dict] = None,
    ) -> Dict:
        """
        Deploy an agent container with resource limits

        Args:
            agent_id: Database agent ID
            user_id: Database user ID
            docker_image: Docker image to run
            name: Agent name
            cpu_limit: CPU cores limit
            memory_limit_mb: Memory in MB
            environment: Environment variables

        Returns:
            Dict with container info (id, port, status)
        """
        try:
            # Generate unique container name
            container_name = f"agent-{user_id}-{agent_id}"

            # Pull image if needed
            try:
                self.client.images.get(docker_image)
            except ImageNotFound:
                logger.info(f"Pulling image: {docker_image}")
                self.client.images.pull(docker_image)

            # Resource limits
            mem_limit = f"{memory_limit_mb}m"
            cpu_quota = int(cpu_limit * 100000)  # Docker CPU quota

            # Start container
            container = self.client.containers.run(
                image=docker_image,
                name=container_name,
                detach=True,
                restart_policy={"Name": "unless-stopped", "MaximumRetryCount": 5},
                network=self.network_name,
                environment=environment or {},
                labels={
                    "agentnest.agent_id": str(agent_id),
                    "agentnest.user_id": str(user_id),
                    "agentnest.deployed": datetime.utcnow().isoformat(),
                },
                # Resource constraints
                mem_limit=mem_limit,
                memswap_limit=mem_limit,
                cpu_quota=cpu_quota,
                cpu_period=100000,
                # Logging
                log_config={
                    "type": "json-file",
                    "config": {"max-size": "10m", "max-file": "3"},
                },
            )

            logger.info(f"Container deployed: {container_name} ({container.id[:12]})")

            return {
                "container_id": container.id[:12],
                "container_name": container_name,
                "status": "running",
                "docker_image": docker_image,
                "cpu_limit": cpu_limit,
                "memory_limit_mb": memory_limit_mb,
            }

        except APIError as e:
            logger.error(f"Docker API error: {str(e)}")
            raise Exception(f"Failed to deploy container: {str(e)}")

    def stop_agent(self, agent_id: int, user_id: int) -> bool:
        """Stop an agent container"""
        try:
            container_name = f"agent-{user_id}-{agent_id}"
            container = self.client.containers.get(container_name)
            container.stop(timeout=10)
            logger.info(f"Container stopped: {container_name}")
            return True
        except docker.errors.NotFound:
            logger.warning(f"Container not found: {container_name}")
            return False
        except APIError as e:
            logger.error(f"Failed to stop container: {str(e)}")
            return False

    def start_agent(self, agent_id: int, user_id: int) -> bool:
        """Start a stopped agent container"""
        try:
            container_name = f"agent-{user_id}-{agent_id}"
            container = self.client.containers.get(container_name)
            container.start()
            logger.info(f"Container started: {container_name}")
            return True
        except docker.errors.NotFound:
            logger.warning(f"Container not found: {container_name}")
            return False
        except APIError as e:
            logger.error(f"Failed to start container: {str(e)}")
            return False

    def delete_agent(self, agent_id: int, user_id: int) -> bool:
        """Delete an agent container"""
        try:
            container_name = f"agent-{user_id}-{agent_id}"
            container = self.client.containers.get(container_name)
            container.stop(timeout=5)
            container.remove(force=True)
            logger.info(f"Container deleted: {container_name}")
            return True
        except docker.errors.NotFound:
            logger.warning(f"Container not found: {container_name}")
            return False
        except APIError as e:
            logger.error(f"Failed to delete container: {str(e)}")
            return False

    def get_agent_logs(self, agent_id: int, user_id: int, tail: int = 100) -> str:
        """Get recent logs from an agent container"""
        try:
            container_name = f"agent-{user_id}-{agent_id}"
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=tail, timestamps=True).decode("utf-8")
            return logs
        except docker.errors.NotFound:
            return "Container not found"
        except APIError as e:
            return f"Error retrieving logs: {str(e)}"

    def stream_agent_logs(self, agent_id: int, user_id: int):
        """Stream logs from an agent container (for WebSocket)"""
        try:
            container_name = f"agent-{user_id}-{agent_id}"
            container = self.client.containers.get(container_name)
            for line in container.logs(stream=True, follow=True):
                yield line.decode("utf-8").strip()
        except docker.errors.NotFound:
            yield "Container not found"
        except APIError as e:
            yield f"Error: {str(e)}"

    def get_agent_stats(self, agent_id: int, user_id: int) -> Dict:
        """Get real-time resource usage stats for an agent"""
        try:
            container_name = f"agent-{user_id}-{agent_id}"
            container = self.client.containers.get(container_name)

            stats = container.stats(stream=False)

            # Calculate CPU percentage
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]
            )
            cpu_percent = (
                (cpu_delta / system_delta) * len(stats["cpu_stats"]["cpus"]) * 100
                if system_delta > 0
                else 0
            )

            # Memory usage
            memory_usage = stats["memory_stats"]["usage"]
            memory_limit = stats["memory_stats"]["limit"]
            memory_percent = (memory_usage / memory_limit * 100) if memory_limit > 0 else 0

            return {
                "container_id": container.short_id,
                "status": container.status,
                "cpu_percent": round(cpu_percent, 2),
                "memory_usage_mb": round(memory_usage / 1024 / 1024, 2),
                "memory_limit_mb": round(memory_limit / 1024 / 1024, 2),
                "memory_percent": round(memory_percent, 2),
                "uptime_seconds": self._get_uptime(container),
            }
        except docker.errors.NotFound:
            return {"error": "Container not found"}
        except Exception as e:
            return {"error": str(e)}

    def _get_uptime(self, container) -> int:
        """Calculate container uptime in seconds"""
        import time

        start_time = datetime.fromisoformat(container.attrs["State"]["StartedAt"].replace("Z", "+00:00"))
        uptime = (datetime.now(start_time.tzinfo) - start_time).total_seconds()
        return int(uptime)

    def list_agents(self, user_id: int) -> List[Dict]:
        """List all containers for a user"""
        try:
            containers = self.client.containers.list(
                all=True, filters={"label": f"agentnest.user_id={user_id}"}
            )

            agents = []
            for container in containers:
                labels = container.labels or {}
                agents.append(
                    {
                        "agent_id": labels.get("agentnest.agent_id"),
                        "container_id": container.short_id,
                        "name": container.name,
                        "status": container.status,
                        "image": container.image.tags[0] if container.image.tags else "unknown",
                        "created": container.attrs["Created"],
                    }
                )
            return agents
        except Exception as e:
            logger.error(f"Error listing agents: {str(e)}")
            return []

    def health_check(self, agent_id: int, user_id: int) -> bool:
        """Check if agent container is healthy"""
        try:
            container_name = f"agent-{user_id}-{agent_id}"
            container = self.client.containers.get(container_name)
            container.reload()
            return container.status == "running"
        except Exception:
            return False


# Singleton instance
_docker_service = None


def get_docker_service() -> DockerService:
    """Get or create Docker service singleton"""
    global _docker_service
    if _docker_service is None:
        _docker_service = DockerService()
    return _docker_service
